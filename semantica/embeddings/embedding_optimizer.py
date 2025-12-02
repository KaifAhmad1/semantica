"""
Embedding Optimizer Module

This module provides comprehensive optimization utilities for embedding generation,
compression, and storage in the Semantica framework.

Key Features:
    - Embedding compression (PCA, quantization)
    - Dimension reduction
    - Batch processing optimization
    - Performance profiling
    - Memory optimization

Example Usage:
    >>> from semantica.embeddings import EmbeddingOptimizer
    >>> optimizer = EmbeddingOptimizer(compression_method="pca", target_dimension=128)
    >>> compressed = optimizer.compress(embeddings, target_dim=64)
    >>> metrics = optimizer.profile_performance(embeddings)

Author: Semantica Contributors
License: MIT
"""

from typing import Any, Dict, List, Optional

import numpy as np

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker

try:
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class EmbeddingOptimizer:
    """
    Embedding optimization utilities for compression and performance.

    This class provides methods for compressing embeddings, reducing dimensions,
    optimizing batch processing, and profiling embedding performance.

    Features:
        - PCA-based dimension reduction
        - Quantization for memory efficiency
        - Batch processing optimization
        - Performance profiling and metrics

    Example Usage:
        >>> optimizer = EmbeddingOptimizer(
        ...     compression_method="pca",
        ...     target_dimension=128
        ... )
        >>> compressed = optimizer.compress(embeddings, target_dim=64)
        >>> metrics = optimizer.profile_performance(embeddings)
    """

    def __init__(
        self, compression_method: str = "pca", target_dimension: int = 128, **config
    ):
        """
        Initialize embedding optimizer.

        Sets up the optimizer with specified compression method and target dimension
        for embedding reduction operations.

        Args:
            compression_method: Method for compression - "pca" or "quantization"
                               (default: "pca")
            target_dimension: Default target dimension for reduction (default: 128)
            **config: Additional configuration options
        """
        self.logger = get_logger("embedding_optimizer")
        self.config = config

        # Compression configuration
        self.compression_method = compression_method
        self.target_dimension = target_dimension

        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()

        self.logger.debug(
            f"Embedding optimizer initialized "
            f"(method: {compression_method}, target_dim: {target_dimension})"
        )

    def compress(
        self,
        embeddings: np.ndarray,
        target_dim: Optional[int] = None,
        method: Optional[str] = None,
        **options,
    ) -> np.ndarray:
        """
        Compress embeddings using specified method.

        This method reduces the size or dimension of embeddings to optimize
        storage and processing. Supports PCA-based dimension reduction and
        quantization for memory efficiency.

        Compression Methods:
            - "pca": Principal Component Analysis - reduces dimension while
                    preserving variance (requires sklearn)
            - "quantization": Reduces precision to save memory

        Args:
            embeddings: Input embeddings array of shape (n_embeddings, dim)
            target_dim: Target dimension for compression (default: self.target_dimension)
            method: Compression method - "pca" or "quantization" (default: self.compression_method)
            **options: Additional compression options:
                - bits: Bit depth for quantization (default: 8)

        Returns:
            np.ndarray: Compressed embeddings with same or reduced dimension.
                       Returns original embeddings if compression fails or not applicable.

        Example:
            >>> # PCA compression
            >>> compressed = optimizer.compress(embeddings, target_dim=64, method="pca")
            >>> # Quantization
            >>> quantized = optimizer.compress(embeddings, method="quantization", bits=8)
        """
        # Track embedding compression
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="embeddings",
            submodule="EmbeddingOptimizer",
            message=f"Compressing embeddings: {embeddings.shape}",
        )

        try:
            target_dim = target_dim or self.target_dimension
            method = method or self.compression_method

            self.logger.debug(
                f"Compressing embeddings: shape {embeddings.shape}, "
                f"method={method}, target_dim={target_dim}"
            )

            if method == "pca":
                self.progress_tracker.update_tracking(
                    tracking_id, message="Applying PCA compression..."
                )
                result = self._compress_pca(embeddings, target_dim)
            elif method == "quantization":
                self.progress_tracker.update_tracking(
                    tracking_id, message="Applying quantization..."
                )
                result = self._compress_quantization(embeddings, **options)
            else:
                self.logger.warning(
                    f"Unknown compression method: {method}. Returning original embeddings."
                )
                self.progress_tracker.stop_tracking(
                    tracking_id,
                    status="completed",
                    message="Unknown method, returning original",
                )
                return embeddings

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Compressed to shape: {result.shape}",
            )
            return result

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def _compress_pca(self, embeddings: np.ndarray, target_dim: int) -> np.ndarray:
        """
        Compress embeddings using Principal Component Analysis (PCA).

        PCA reduces the dimensionality of embeddings while preserving as much
        variance as possible. This is useful for reducing storage and computation
        while maintaining semantic information.

        Args:
            embeddings: Input embeddings array of shape (n_embeddings, dim)
            target_dim: Target dimension for reduction

        Returns:
            np.ndarray: Compressed embeddings of shape (n_embeddings, target_dim).
                       Returns original if sklearn unavailable or target_dim >= current dim.
        """
        if not SKLEARN_AVAILABLE:
            self.logger.warning(
                "sklearn not available for PCA. Install with: pip install scikit-learn. "
                "Returning original embeddings."
            )
            return embeddings

        # Check if reduction is needed
        if embeddings.shape[1] <= target_dim:
            self.logger.debug(
                f"Target dimension {target_dim} >= current dimension {embeddings.shape[1]}. "
                "No reduction needed."
            )
            return embeddings

        try:
            # Apply PCA
            pca = PCA(n_components=target_dim)
            compressed = pca.fit_transform(embeddings)

            # Calculate variance preserved
            variance_ratio = np.sum(pca.explained_variance_ratio_)
            self.logger.debug(
                f"PCA compression: {embeddings.shape[1]} -> {target_dim} dims, "
                f"variance preserved: {variance_ratio:.3f}"
            )

            return compressed.astype(np.float32)

        except Exception as e:
            error_msg = f"Failed to compress with PCA: {e}"
            self.logger.error(error_msg)
            return embeddings

    def _compress_quantization(
        self, embeddings: np.ndarray, bits: int = 8, **options
    ) -> np.ndarray:
        """
        Compress embeddings using quantization.

        Quantization reduces the precision of embedding values to save memory.
        Values are quantized to specified bit depth and then dequantized back
        to float32 for use.

        Args:
            embeddings: Input embeddings array
            bits: Bit depth for quantization (default: 8, range: 1-16)
            **options: Unused (for compatibility)

        Returns:
            np.ndarray: Quantized and dequantized embeddings (same shape, reduced precision)
        """
        if bits < 1 or bits > 16:
            self.logger.warning(f"Invalid bit depth {bits}, using 8 bits")
            bits = 8

        # Find value range
        min_val = np.min(embeddings)
        max_val = np.max(embeddings)

        # Handle constant embeddings
        if max_val == min_val:
            self.logger.debug("Constant embeddings detected, returning original")
            return embeddings

        # Scale to [0, 2^bits - 1]
        scale = (2**bits - 1) / (max_val - min_val)
        quantized = ((embeddings - min_val) * scale).astype(np.uint8)

        # Dequantize back to float32
        dequantized = (quantized.astype(np.float32) / scale) + min_val

        self.logger.debug(
            f"Quantization: {bits} bits, "
            f"memory reduction: {embeddings.nbytes / quantized.nbytes:.2f}x"
        )

        return dequantized

    def reduce_dimensions(
        self, embeddings: np.ndarray, target_dim: int, method: str = "pca", **options
    ) -> np.ndarray:
        """
        Reduce embedding dimensions using specified method.

        This method reduces the dimensionality of embeddings using PCA or simple
        truncation. Useful for reducing computational requirements and storage.

        Reduction Methods:
            - "pca": Principal Component Analysis - preserves variance (recommended)
            - "truncate": Simple truncation - takes first target_dim dimensions

        Args:
            embeddings: Input embeddings array of shape (n_embeddings, dim)
            target_dim: Target dimension for reduction
            method: Reduction method - "pca" or "truncate" (default: "pca")
            **options: Additional reduction options (unused)

        Returns:
            np.ndarray: Reduced embeddings of shape (n_embeddings, target_dim)

        Example:
            >>> # PCA reduction (preserves variance)
            >>> reduced = optimizer.reduce_dimensions(embeddings, target_dim=64, method="pca")
            >>> # Truncation (simple, fast)
            >>> truncated = optimizer.reduce_dimensions(embeddings, target_dim=64, method="truncate")
        """
        self.logger.debug(
            f"Reducing dimensions: {embeddings.shape[1]} -> {target_dim} "
            f"(method: {method})"
        )

        if method == "pca":
            return self._compress_pca(embeddings, target_dim)
        elif method == "truncate":
            # Simple truncation: take first target_dim dimensions
            if embeddings.shape[1] <= target_dim:
                self.logger.debug("No truncation needed")
                return embeddings
            truncated = embeddings[:, :target_dim]
            self.logger.debug(
                f"Truncated embeddings: {embeddings.shape} -> {truncated.shape}"
            )
            return truncated
        else:
            self.logger.warning(
                f"Unknown reduction method: {method}. Returning original."
            )
            return embeddings

    def optimize_batch_processing(
        self, embeddings: List[np.ndarray], normalize: bool = True, **options
    ) -> np.ndarray:
        """
        Optimize batch processing of embeddings.

        This method converts a list of embeddings to a normalized batch array,
        optimizing for efficient processing and similarity calculations.

        Args:
            embeddings: List of embedding vectors
            normalize: Whether to normalize embeddings to unit vectors (default: True)
            **options: Additional optimization options (unused)

        Returns:
            np.ndarray: Optimized batch embeddings array of shape (n_embeddings, dim)

        Example:
            >>> embeddings_list = [emb1, emb2, emb3]
            >>> batch = optimizer.optimize_batch_processing(embeddings_list)
            >>> print(f"Batch shape: {batch.shape}")  # (3, dim)
        """
        if not embeddings:
            self.logger.debug("Empty embeddings list provided")
            return np.array([])

        # Convert to array
        emb_array = np.array(embeddings)

        self.logger.debug(
            f"Optimizing batch: {len(embeddings)} embeddings, shape {emb_array.shape}"
        )

        # Apply normalization if requested
        if normalize:
            norms = np.linalg.norm(emb_array, axis=1, keepdims=True)
            # Avoid division by zero for zero-norm vectors
            norms[norms == 0] = 1
            emb_array = emb_array / norms
            self.logger.debug("Normalized batch embeddings")

        return emb_array

    def profile_performance(self, embeddings: np.ndarray, **options) -> Dict[str, Any]:
        """
        Profile embedding performance and characteristics.

        This method analyzes embeddings and returns comprehensive metrics including
        shape, memory usage, statistical properties, and sparsity.

        Args:
            embeddings: Input embeddings array to profile
            **options: Additional profiling options (unused)

        Returns:
            Dictionary containing performance metrics:
                - shape: Embedding array shape (tuple)
                - dtype: Data type (str)
                - memory_mb: Memory usage in megabytes (float)
                - mean: Mean value across all embeddings (float)
                - std: Standard deviation (float)
                - min: Minimum value (float)
                - max: Maximum value (float)
                - sparsity: Fraction of zero values (float, 0-1)

        Example:
            >>> metrics = optimizer.profile_performance(embeddings)
            >>> print(f"Memory: {metrics['memory_mb']:.2f} MB")
            >>> print(f"Sparsity: {metrics['sparsity']:.3f}")
        """
        metrics = {
            "shape": embeddings.shape,
            "dtype": str(embeddings.dtype),
            "memory_mb": embeddings.nbytes / (1024 * 1024),
            "mean": float(np.mean(embeddings)),
            "std": float(np.std(embeddings)),
            "min": float(np.min(embeddings)),
            "max": float(np.max(embeddings)),
        }

        # Calculate sparsity (fraction of zero values)
        non_zero = np.count_nonzero(embeddings)
        total = embeddings.size
        metrics["sparsity"] = 1.0 - (non_zero / total) if total > 0 else 0.0

        self.logger.debug(
            f"Performance profile: shape={metrics['shape']}, "
            f"memory={metrics['memory_mb']:.2f}MB, "
            f"sparsity={metrics['sparsity']:.3f}"
        )

        return metrics
