"""
Context Manager Module

This module provides comprehensive context window management for embedding generation
and processing in the Semantica framework, enabling efficient handling of long texts.

Key Features:
    - Context window creation and management
    - Text splitting with sentence boundary preservation
    - Context merging and retrieval
    - Configurable window size and overlap
    - Context metadata tracking

Example Usage:
    >>> from semantica.embeddings import ContextManager
    >>> manager = ContextManager(window_size=512, overlap=50)
    >>> windows = manager.split_into_windows(long_text)
    >>> merged = manager.merge_contexts([window1.context_id, window2.context_id])

Author: Semantica Contributors
License: MIT
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker


@dataclass
class ContextWindow:
    """
    Context window representation for text processing.

    This dataclass represents a window of text with its position in the original
    document and associated metadata. Used for managing text chunks in embedding
    generation and processing.

    Attributes:
        text: The text content of this context window
        start_index: Starting character index in original text
        end_index: Ending character index in original text
        context_id: Unique identifier for this context window
        metadata: Additional metadata dictionary (source, tags, etc.)

    Example:
        >>> window = ContextWindow(
        ...     text="This is a context window.",
        ...     start_index=0,
        ...     end_index=25,
        ...     context_id="uuid-123",
        ...     metadata={"source": "document.txt"}
        ... )
    """

    text: str
    start_index: int
    end_index: int
    context_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """
    Context window manager for embedding generation and text processing.

    This class manages context windows for processing long texts, enabling
    efficient chunking, retrieval, and merging of text contexts.

    Features:
        - Context window creation and storage
        - Text splitting with sentence boundary preservation
        - Context merging for combining windows
        - Configurable window size and overlap
        - Automatic context cleanup when limit reached

    Example Usage:
        >>> manager = ContextManager(
        ...     window_size=512,
        ...     overlap=50,
        ...     max_contexts=100
        ... )
        >>> windows = manager.split_into_windows(long_text)
        >>> context = manager.get_context(windows[0].context_id)
    """

    def __init__(
        self,
        window_size: int = 512,
        overlap: int = 50,
        max_contexts: int = 100,
        **config,
    ):
        """
        Initialize context manager.

        Sets up the manager with specified window size, overlap, and maximum
        number of contexts to maintain in memory.

        Args:
            window_size: Size of context windows in characters (default: 512)
            overlap: Overlap between consecutive windows in characters (default: 50)
            max_contexts: Maximum number of contexts to keep in memory (default: 100)
            **config: Additional configuration options
        """
        self.logger = get_logger("context_manager")
        self.config = config

        # Window configuration
        self.window_size = window_size
        self.overlap = overlap
        self.max_contexts = max_contexts

        # Store contexts (context_id -> ContextWindow)
        self.contexts: Dict[str, ContextWindow] = {}

        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()

        self.logger.debug(
            f"Context manager initialized: window_size={window_size}, "
            f"overlap={overlap}, max_contexts={max_contexts}"
        )

    def create_context_window(
        self, text: str, start_index: int = 0, **metadata
    ) -> ContextWindow:
        """
        Create a context window from text.

        This method creates a new context window with a unique ID and stores it
        for later retrieval. Automatically removes oldest context if limit reached.

        Args:
            text: Input text content for the context window
            start_index: Starting character index in original text (default: 0)
            **metadata: Additional metadata to attach to context window
                       (e.g., source, tags, document_id)

        Returns:
            ContextWindow: Created context window with unique ID

        Example:
            >>> window = manager.create_context_window(
            ...     text="This is a context window.",
            ...     start_index=0,
            ...     source="document.txt"
            ... )
            >>> print(window.context_id)
        """
        import uuid

        # Generate unique context ID
        context_id = str(uuid.uuid4())
        end_index = start_index + len(text)

        # Create context window
        window = ContextWindow(
            text=text,
            start_index=start_index,
            end_index=end_index,
            context_id=context_id,
            metadata=metadata,
        )

        # Manage context storage (remove oldest if limit reached)
        if len(self.contexts) >= self.max_contexts:
            # Find and remove oldest context (by start_index)
            oldest_id = min(
                self.contexts.keys(), key=lambda k: self.contexts[k].start_index
            )
            del self.contexts[oldest_id]
            self.logger.debug(
                f"Removed oldest context {oldest_id} (limit reached: {self.max_contexts})"
            )

        # Store new context
        self.contexts[context_id] = window

        self.logger.debug(
            f"Created context window: id={context_id}, "
            f"start={start_index}, end={end_index}, "
            f"text_length={len(text)}"
        )

        return window

    def split_into_windows(
        self, text: str, preserve_sentences: bool = True, **options
    ) -> List[ContextWindow]:
        """
        Split text into context windows.

        This method splits long text into overlapping context windows, optionally
        preserving sentence boundaries to avoid cutting sentences in half.

        Splitting Strategy:
            - Creates windows of size window_size
            - Overlaps by overlap characters between windows
            - Optionally preserves sentence boundaries (default: True)
            - Ensures minimum window size (50% of window_size) when preserving sentences

        Args:
            text: Input text to split into windows
            preserve_sentences: Whether to preserve sentence boundaries when splitting
                              (default: True). If True, windows end at sentence boundaries.
            **options: Additional options passed to create_context_window()

        Returns:
            List of ContextWindow: List of context windows covering the entire text

        Example:
            >>> long_text = "Sentence one. Sentence two! Sentence three?"
            >>> windows = manager.split_into_windows(long_text, preserve_sentences=True)
            >>> print(f"Created {len(windows)} context windows")
        """
        # Track context window splitting
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="embeddings",
            submodule="ContextManager",
            message=f"Splitting text into windows (length: {len(text)})",
        )

        try:
            if not text:
                self.logger.debug("Empty text provided, returning empty window list")
                self.progress_tracker.stop_tracking(
                    tracking_id,
                    status="completed",
                    message="Empty text, no windows created",
                )
                return []

            windows = []
            text_length = len(text)
            start = 0

            self.logger.debug(
                f"Splitting text into windows: length={text_length}, "
                f"window_size={self.window_size}, overlap={self.overlap}, "
                f"preserve_sentences={preserve_sentences}"
            )

            self.progress_tracker.update_tracking(
                tracking_id, message="Creating context windows..."
            )
            while start < text_length:
                # Calculate end position
                end = min(start + self.window_size, text_length)

                # Try to preserve sentence boundaries if requested
                if preserve_sentences and end < text_length:
                    # Look for sentence boundaries (., !, ?, newline)
                    for boundary in [".", "!", "?", "\n"]:
                        last_boundary = text.rfind(boundary, start, end)
                        # Only use boundary if it's at least 50% into the window
                        # (ensures minimum window size)
                        if last_boundary > start + self.window_size * 0.5:
                            end = last_boundary + 1
                            break

                # Extract window text
                window_text = text[start:end]

                # Create and store context window
                window = self.create_context_window(window_text, start, **options)
                windows.append(window)

                # Move to next window position with overlap
                start += self.window_size - self.overlap

            self.logger.info(f"Split text into {len(windows)} context window(s)")

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Created {len(windows)} context windows",
            )
            return windows

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def get_context(self, context_id: str) -> Optional[ContextWindow]:
        """
        Get context window by ID.

        Retrieves a previously created context window using its unique identifier.

        Args:
            context_id: Unique context window identifier

        Returns:
            ContextWindow if found, None otherwise

        Example:
            >>> window = manager.get_context("uuid-123")
            >>> if window:
            ...     print(window.text)
        """
        context = self.contexts.get(context_id)
        if context:
            self.logger.debug(f"Retrieved context: {context_id}")
        else:
            self.logger.debug(f"Context not found: {context_id}")
        return context

    def merge_contexts(
        self, context_ids: List[str], **options
    ) -> Optional[ContextWindow]:
        """
        Merge multiple context windows into a single window.

        This method combines multiple context windows by concatenating their texts
        and merging their metadata. Contexts are sorted by start_index before merging.

        Args:
            context_ids: List of context IDs to merge
            **options: Additional options passed to create_context_window()

        Returns:
            ContextWindow: Merged context window, or None if no valid contexts found.
                         The merged window has:
                         - Combined text from all contexts
                         - Start index from first context
                         - End index from last context
                         - Merged metadata from all contexts

        Example:
            >>> merged = manager.merge_contexts(
            ...     [window1.context_id, window2.context_id, window3.context_id]
            ... )
            >>> print(f"Merged text length: {len(merged.text)}")
        """
        # Retrieve all valid contexts
        contexts = [
            self.contexts.get(cid) for cid in context_ids if cid in self.contexts
        ]
        contexts = [c for c in contexts if c is not None]

        if not contexts:
            self.logger.warning(f"No valid contexts found for merging: {context_ids}")
            return None

        # Sort contexts by start index to maintain order
        contexts.sort(key=lambda c: c.start_index)

        # Merge texts (join with space)
        merged_text = " ".join(c.text for c in contexts)
        start_index = contexts[0].start_index
        end_index = contexts[-1].end_index

        # Combine metadata from all contexts
        merged_metadata = {}
        for ctx in contexts:
            merged_metadata.update(ctx.metadata)

        # Add merge information
        merged_metadata["merged"] = True
        merged_metadata["source_contexts"] = context_ids
        merged_metadata["num_contexts"] = len(contexts)

        self.logger.debug(
            f"Merged {len(contexts)} contexts: "
            f"start={start_index}, end={end_index}, "
            f"text_length={len(merged_text)}"
        )

        return self.create_context_window(
            merged_text, start_index, **merged_metadata, **options
        )

    def clear_contexts(self) -> None:
        """
        Clear all stored contexts.

        Removes all context windows from memory. Useful for freeing memory
        or resetting the context manager.
        """
        count = len(self.contexts)
        self.contexts.clear()
        self.logger.debug(f"Cleared {count} context(s)")

    def get_context_count(self) -> int:
        """
        Get number of stored contexts.

        Returns:
            int: Number of context windows currently stored in memory
        """
        return len(self.contexts)
