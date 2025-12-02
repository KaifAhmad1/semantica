"""
Lifecycle Management Module

This module provides comprehensive lifecycle management for the Semantica framework,
including startup/shutdown sequences, health monitoring, and resource management.

Key Features:
    - Startup and shutdown hook system with priority ordering
    - Component health monitoring and status tracking
    - Graceful degradation and error handling
    - Resource cleanup and state management
    - System state tracking (uninitialized, ready, running, stopped, etc.)

Example Usage:
    >>> from semantica.core import LifecycleManager
    >>> manager = LifecycleManager()
    >>> manager.register_startup_hook(my_hook, priority=10)
    >>> manager.startup()
    >>> health = manager.get_health_summary()

Author: Semantica Contributors
License: MIT
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..utils.exceptions import SemanticaError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker


class SystemState(str, Enum):
    """System state enumeration."""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class HealthStatus:
    """Health status information."""

    component: str
    healthy: bool
    message: str = ""
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)


class LifecycleManager:
    """
    System lifecycle manager.

    This class coordinates the startup, shutdown, and health monitoring of all
    framework components. It provides a hook-based system for executing code
    at specific lifecycle stages with priority ordering.

    Features:
        - Priority-based startup/shutdown hooks
        - Component registration and health monitoring
        - State management and tracking
        - Graceful error handling during lifecycle transitions

    Example Usage:
        >>> manager = LifecycleManager()
        >>> manager.register_component("database", db_connection)
        >>> manager.register_startup_hook(init_db, priority=10)
        >>> manager.startup()
        >>> # System is now ready
        >>> manager.shutdown(graceful=True)
    """

    def __init__(self):
        """
        Initialize lifecycle manager.

        Creates a new lifecycle manager in UNINITIALIZED state with empty
        registries for components, hooks, and health status.
        """
        self.logger = get_logger("lifecycle")

        # System state tracking
        self.state: SystemState = SystemState.UNINITIALIZED

        # Component registry for health monitoring
        self._component_registry: Dict[str, Any] = {}

        # Health status tracking
        self.health_status: Dict[str, HealthStatus] = {}
        self._last_health_check: Optional[float] = None

        # Hook registries: list of (hook_function, priority) tuples
        # Lower priority = earlier execution
        self.startup_hooks: List[Tuple[Callable[[], None], int]] = []
        self.shutdown_hooks: List[Tuple[Callable[[], None], int]] = []

        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()

        self.logger.debug("Lifecycle manager initialized")

    def startup(self) -> None:
        """
        Execute startup sequence.

        This method runs all registered startup hooks in priority order,
        verifies component initialization, and performs initial health checks.
        The system transitions from UNINITIALIZED -> INITIALIZING -> READY.

        Raises:
            SemanticaError: If startup fails (hook failure, component verification failure)

        Example:
            >>> manager = LifecycleManager()
            >>> manager.register_startup_hook(init_config, priority=10)
            >>> manager.register_startup_hook(init_database, priority=20)
            >>> manager.startup()  # Hooks execute in order: init_config, then init_database
        """
        # Track system startup
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="core",
            submodule="LifecycleManager",
            message="Starting system lifecycle",
        )

        try:
            # Check if already started
            if self.state in (SystemState.READY, SystemState.RUNNING):
                self.logger.warning(
                    f"System already in {self.state.value} state, skipping startup"
                )
                self.progress_tracker.stop_tracking(
                    tracking_id, status="completed", message="System already started"
                )
                return

            # Transition to initializing state
            self.state = SystemState.INITIALIZING
            self.logger.info("Starting system lifecycle")

            # Sort hooks by priority (lower priority = earlier execution)
            sorted_hooks = sorted(self.startup_hooks, key=lambda x: x[1])

            if sorted_hooks:
                self.logger.debug(f"Executing {len(sorted_hooks)} startup hook(s)")

            # Execute all startup hooks in priority order
            for hook_fn, priority in sorted_hooks:
                try:
                    self.logger.debug(
                        f"Executing startup hook with priority {priority}"
                    )
                    hook_fn()
                except Exception as e:
                    error_msg = f"Startup hook (priority {priority}) failed: {e}"
                    self.logger.error(error_msg)
                    self.state = SystemState.ERROR
                    raise SemanticaError(error_msg) from e

            # Verify all registered components are properly initialized
            self._verify_components()

            # Run initial health checks on all components
            health_results = self.health_check()
            unhealthy_components = [
                name for name, status in health_results.items() if not status.healthy
            ]

            if unhealthy_components:
                self.logger.warning(
                    f"Some components are unhealthy after startup: {unhealthy_components}"
                )
            else:
                self.logger.debug("All components are healthy")

            # Transition to ready state
            self.state = SystemState.READY
            self.logger.info("System startup completed successfully")

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message="System startup completed successfully",
            )

        except Exception as e:
            # Transition to error state on failure
            self.state = SystemState.ERROR
            self.logger.error(f"System startup failed: {e}")
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def shutdown(self, graceful: bool = True) -> None:
        """
        Execute shutdown sequence.

        This method runs all registered shutdown hooks in priority order and
        cleans up resources. In graceful mode, hook failures are logged but
        don't stop the shutdown process.

        Args:
            graceful: Whether to shutdown gracefully (default: True)
                - True: Continue shutdown even if hooks fail (log warnings)
                - False: Stop shutdown on first hook failure (raise error)

        Raises:
            SemanticaError: If shutdown fails and graceful=False

        Example:
            >>> manager.shutdown(graceful=True)  # Continue even if cleanup fails
            >>> manager.shutdown(graceful=False)  # Stop on first error
        """
        # Track system shutdown
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="core",
            submodule="LifecycleManager",
            message=f"Shutting down system (graceful={graceful})",
        )

        try:
            # Check if already stopped
            if self.state == SystemState.STOPPED:
                self.logger.warning("System already in STOPPED state")
                self.progress_tracker.stop_tracking(
                    tracking_id, status="completed", message="System already stopped"
                )
                return

            # Transition to stopping state
            self.state = SystemState.STOPPING
            self.logger.info(f"Shutting down system (graceful={graceful})")

            # Sort hooks by priority (lower priority = earlier execution)
            sorted_hooks = sorted(self.shutdown_hooks, key=lambda x: x[1])

            if sorted_hooks:
                self.logger.debug(f"Executing {len(sorted_hooks)} shutdown hook(s)")

            # Execute all shutdown hooks in priority order
            for hook_fn, priority in sorted_hooks:
                try:
                    self.logger.debug(
                        f"Executing shutdown hook with priority {priority}"
                    )
                    hook_fn()
                except Exception as e:
                    error_msg = f"Shutdown hook (priority {priority}) failed: {e}"

                    if graceful:
                        # In graceful mode, log warning but continue
                        self.logger.warning(error_msg)
                    else:
                        # In non-graceful mode, stop on first error
                        self.logger.error(error_msg)
                        raise SemanticaError(error_msg) from e

            # Cleanup all registered components
            self._cleanup_resources()

            # Transition to stopped state
            self.state = SystemState.STOPPED
            self.logger.info("System shutdown completed successfully")

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message="System shutdown completed successfully",
            )

        except Exception as e:
            # Transition to error state on failure
            self.state = SystemState.ERROR
            self.logger.error(f"System shutdown failed: {e}")
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            if not graceful:
                raise

    def health_check(self) -> Dict[str, HealthStatus]:
        """
        Perform comprehensive system health check.

        This method checks the health of all registered components by calling
        their health_check() method if available, or using default health logic.
        Results are cached in health_status and returned.

        Returns:
            Dictionary mapping component names to HealthStatus objects,
            containing health status, messages, and details for each component

        Example:
            >>> health = manager.health_check()
            >>> for name, status in health.items():
            ...     print(f"{name}: {'✓' if status.healthy else '✗'}")
        """
        # Record health check timestamp
        self._last_health_check = time.time()

        health_results = {}

        # Check health of each registered component
        for component_name, component in self._component_registry.items():
            try:
                # Try to get health status from component
                if hasattr(component, "health_check"):
                    # Component has its own health check method
                    component_health = component.health_check()

                    # Handle different return types
                    if isinstance(component_health, dict):
                        # Dictionary format: {"healthy": bool, "message": str, "details": dict}
                        healthy = component_health.get("healthy", True)
                        message = component_health.get("message", "")
                        details = component_health.get("details", {})
                    elif isinstance(component_health, bool):
                        # Simple boolean
                        healthy = component_health
                        message = ""
                        details = {}
                    else:
                        # Other types: convert to boolean
                        healthy = bool(component_health)
                        message = ""
                        details = {}
                else:
                    # No health_check method: assume healthy if component exists
                    healthy = component is not None
                    message = "Component exists" if healthy else "Component is None"
                    details = {}

                # Create health status object
                status = HealthStatus(
                    component=component_name,
                    healthy=healthy,
                    message=message,
                    details=details,
                )

            except Exception as e:
                # Health check failed: mark as unhealthy
                error_msg = f"Health check failed: {e}"
                self.logger.warning(
                    f"Component {component_name} health check error: {e}"
                )

                status = HealthStatus(
                    component=component_name,
                    healthy=False,
                    message=error_msg,
                    details={"error": str(e), "error_type": type(e).__name__},
                )

            # Store results
            health_results[component_name] = status
            self.health_status[component_name] = status

        # Log summary of unhealthy components
        unhealthy_components = [
            name for name, status in health_results.items() if not status.healthy
        ]

        if unhealthy_components:
            self.logger.warning(
                f"Health check found {len(unhealthy_components)} unhealthy component(s): "
                f"{unhealthy_components}"
            )
        else:
            self.logger.debug(
                f"Health check passed for all {len(health_results)} component(s)"
            )

        return health_results

    def register_component(self, name: str, component: Any) -> None:
        """
        Register a component for health monitoring.

        Args:
            name: Component name
            component: Component instance
        """
        self._component_registry[name] = component
        self.logger.debug(f"Registered component: {name}")

    def unregister_component(self, name: str) -> None:
        """
        Unregister a component.

        Args:
            name: Component name
        """
        if name in self._component_registry:
            del self._component_registry[name]
            if name in self.health_status:
                del self.health_status[name]
            self.logger.debug(f"Unregistered component: {name}")

    def register_startup_hook(
        self, hook_fn: Callable[[], None], priority: int = 50
    ) -> None:
        """
        Register a startup hook.

        Hooks are executed in order of priority (lower = earlier).
        Priority values are typically between 0-100.

        Args:
            hook_fn: Function to call during startup (no arguments)
            priority: Hook priority (lower = earlier execution, default: 50)
        """
        if not callable(hook_fn):
            raise ValueError("hook_fn must be callable")

        self.startup_hooks.append((hook_fn, priority))
        self.logger.debug(f"Registered startup hook with priority {priority}")

    def register_shutdown_hook(
        self, hook_fn: Callable[[], None], priority: int = 50
    ) -> None:
        """
        Register a shutdown hook.

        Hooks are executed in order of priority (lower = earlier).
        Priority values are typically between 0-100.

        Args:
            hook_fn: Function to call during shutdown (no arguments)
            priority: Hook priority (lower = earlier execution, default: 50)
        """
        if not callable(hook_fn):
            raise ValueError("hook_fn must be callable")

        self.shutdown_hooks.append((hook_fn, priority))
        self.logger.debug(f"Registered shutdown hook with priority {priority}")

    def get_state(self) -> SystemState:
        """
        Get current system state.

        Returns:
            Current system state
        """
        return self.state

    def is_ready(self) -> bool:
        """
        Check if system is ready.

        Returns:
            True if system is ready, False otherwise
        """
        return self.state == SystemState.READY or self.state == SystemState.RUNNING

    def is_running(self) -> bool:
        """
        Check if system is running.

        Returns:
            True if system is running, False otherwise
        """
        return self.state == SystemState.RUNNING

    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get summary of system health.

        Returns:
            Dictionary with health summary information
        """
        health_results = self.health_check()

        total = len(health_results)
        healthy = sum(1 for status in health_results.values() if status.healthy)
        unhealthy = total - healthy

        return {
            "state": self.state.value,
            "total_components": total,
            "healthy_components": healthy,
            "unhealthy_components": unhealthy,
            "is_healthy": unhealthy == 0,
            "last_check": self._last_health_check,
            "components": {
                name: {
                    "healthy": status.healthy,
                    "message": status.message,
                    "timestamp": status.timestamp,
                }
                for name, status in health_results.items()
            },
        }

    def _verify_components(self) -> None:
        """
        Verify that all registered components are initialized.

        Raises:
            SemanticaError: If components are not properly initialized
        """
        uninitialized = []

        for name, component in self._component_registry.items():
            if component is None:
                uninitialized.append(name)

        if uninitialized:
            raise SemanticaError(
                f"Components not initialized: {', '.join(uninitialized)}"
            )

    def _cleanup_resources(self) -> None:
        """
        Cleanup all system resources.

        This method attempts to cleanup all registered components by calling
        their cleanup() or close() methods if available. Errors during cleanup
        are logged but don't stop the cleanup process.
        """
        cleanup_count = 0

        # Cleanup each registered component
        for component_name, component in self._component_registry.items():
            try:
                # Try cleanup() method first, then close()
                if hasattr(component, "cleanup"):
                    component.cleanup()
                    cleanup_count += 1
                    self.logger.debug(f"Cleaned up component: {component_name}")
                elif hasattr(component, "close"):
                    component.close()
                    cleanup_count += 1
                    self.logger.debug(f"Closed component: {component_name}")
            except Exception as e:
                # Log but continue cleanup for other components
                self.logger.warning(
                    f"Failed to cleanup component {component_name}: {e}"
                )

        if cleanup_count > 0:
            self.logger.debug(f"Cleaned up {cleanup_count} component(s)")

        # Clear all registries
        self._component_registry.clear()
        self.health_status.clear()

        self.logger.debug("Resource cleanup completed")
