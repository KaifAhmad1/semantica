"""
Text Embedder Module

This module provides comprehensive text embedding generation capabilities for the
Semantica framework, supporting multiple embedding models including sentence-transformers
and fallback methods.

Key Features:
    - Sentence-transformers integration for high-quality embeddings
    - Batch processing for multiple texts
    - Sentence-level embedding extraction
    - Fallback embedding methods when dependencies unavailable
    - Configurable normalization and device selection

Example Usage:
    >>> from semantica.embeddings import TextEmbedder
    >>> embedder = TextEmbedder(model_name="all-MiniLM-L6-v2")
    >>> embedding = embedder.embed_text("Hello world")
    >>> batch_embeddings = embedder.embed_batch(["text1", "text2"])

Author: Semantica Contributors
License: MIT
"""

from typing import Any, Dict, List, Optional, Union

import numpy as np

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class TextEmbedder:
    """
    Text embedding generator for semantic text representation.

    This class provides text embedding generation using sentence-transformers
    models or fallback methods. Supports single text, batch processing, and
    sentence-level embedding extraction.

    Features:
        - Sentence-transformers model integration
        - Batch processing for efficiency
        - Sentence-level embedding extraction
        - Fallback hash-based embeddings (when dependencies unavailable)
        - Configurable normalization and device selection

    Example Usage:
        >>> embedder = TextEmbedder(
        ...     model_name="all-MiniLM-L6-v2",
        ...     device="cpu",
        ...     normalize=True
        ... )
        >>> embedding = embedder.embed_text("Hello world")
        >>> dim = embedder.get_embedding_dimension()
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        normalize: bool = True,
        **config,
    ):
        """
        Initialize text embedder.

        Sets up the embedder with the specified model and configuration.
        Attempts to load sentence-transformers model, falls back to hash-based
        embeddings if unavailable.

        Args:
            model_name: Name of sentence-transformers model to use
                       (default: "all-MiniLM-L6-v2")
            device: Device to run model on - "cpu" or "cuda" (default: "cpu")
            normalize: Whether to normalize embeddings to unit vectors (default: True)
            **config: Additional configuration options
        """
        self.logger = get_logger("text_embedder")
        self.config = config

        # Model configuration
        self.model_name = model_name
        self.device = device
        self.normalize = normalize

        # Initialize model (will be None if sentence-transformers unavailable)
        self.model = None

        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()

        self._initialize_model()

    def _initialize_model(self) -> None:
        """
        Initialize embedding model.

        Attempts to load the specified sentence-transformers model. If unavailable
        or loading fails, falls back to hash-based embedding method. Logs warnings
        but doesn't raise errors to allow graceful degradation.
        """
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.model_name, device=self.device)
                self.logger.info(
                    f"Loaded sentence-transformers model: {self.model_name} "
                    f"(device: {self.device})"
                )
            except Exception as e:
                self.logger.warning(
                    f"Failed to load model '{self.model_name}': {e}. "
                    "Using fallback embedding method."
                )
                self.model = None
        else:
            self.logger.warning(
                "sentence-transformers not available. "
                "Install with: pip install sentence-transformers. "
                "Using fallback embedding method."
            )

    def embed_text(self, text: str, **options) -> np.ndarray:
        """
        Generate embedding for a single text string.

        This method creates a semantic embedding vector for the input text using
        the configured model. Returns a normalized vector suitable for similarity
        calculations.

        Args:
            text: Input text string to embed. Must be non-empty.
            **options: Additional embedding options passed to model:
                - show_progress_bar: Show progress bar for encoding
                - convert_to_numpy: Convert to numpy array (default: True)
                - batch_size: Batch size for processing

        Returns:
            np.ndarray: 1D embedding vector of shape (embedding_dim,).
                       Dimension depends on model (typically 384-768).

        Raises:
            ProcessingError: If text is empty or embedding generation fails

        Example:
            >>> embedder = TextEmbedder()
            >>> embedding = embedder.embed_text("The quick brown fox")
            >>> print(f"Embedding shape: {embedding.shape}")
            >>> print(f"Embedding dimension: {len(embedding)}")
        """
        # Track text embedding
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="embeddings",
            submodule="TextEmbedder",
            message=f"Generating text embedding: {text[:50]}...",
        )

        try:
            if not text or not text.strip():
                raise ProcessingError("Text cannot be empty or whitespace-only")

            # Use model if available, otherwise fallback
            if self.model:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Using sentence-transformers model..."
                )
                result = self._embed_with_model(text, **options)
            else:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Using fallback embedding method..."
                )
                result = self._embed_fallback(text, **options)

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Generated embedding (dim: {len(result)})",
            )
            return result

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def _embed_with_model(self, text: str, **options) -> np.ndarray:
        """
        Embed text using sentence-transformers model.

        This method uses the loaded sentence-transformers model to generate
        high-quality semantic embeddings.

        Args:
            text: Input text to embed
            **options: Options passed to model.encode()

        Returns:
            np.ndarray: Embedding vector from model
        """
        embeddings = self.model.encode(
            [text], normalize_embeddings=self.normalize, **options
        )

        return embeddings[0]

    def _embed_fallback(self, text: str, **options) -> np.ndarray:
        """
        Fallback embedding using hash-based method.

        This method generates a deterministic embedding using SHA-256 hashing
        when sentence-transformers is not available. Useful for testing or
        when dependencies cannot be installed.

        Note: Hash-based embeddings are not semantic and should not be used
        for production similarity calculations. They are deterministic but
        don't capture semantic meaning.

        Args:
            text: Input text to embed
            **options: Unused (for compatibility)

        Returns:
            np.ndarray: 128-dimensional hash-based embedding vector
        """
        import hashlib

        # Generate hash from text
        hash_obj = hashlib.sha256(text.encode("utf-8"))
        hash_bytes = hash_obj.digest()

        # Convert to numpy array (128-dimensional)
        # Use hash bytes + first 64 bytes to get 128 bytes total
        embedding = np.frombuffer(hash_bytes + hash_bytes[:64], dtype=np.float32)[:128]

        # Normalize if requested
        if self.normalize:
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

        return embedding

    def embed_batch(self, texts: List[str], **options) -> np.ndarray:
        """
        Generate embeddings for multiple texts in batch.

        This method efficiently processes multiple texts at once, which is
        faster than calling embed_text() repeatedly. The model processes
        texts in batches for optimal performance.

        Args:
            texts: List of text strings to embed. Empty list returns empty array.
            **options: Additional embedding options:
                - batch_size: Batch size for processing (default: model default)
                - show_progress_bar: Show progress bar (default: False)
                - convert_to_numpy: Convert to numpy array (default: True)

        Returns:
            np.ndarray: 2D array of embeddings with shape (n_texts, embedding_dim).
                       Returns empty array if input list is empty.

        Example:
            >>> texts = ["First text", "Second text", "Third text"]
            >>> embeddings = embedder.embed_batch(texts)
            >>> print(f"Shape: {embeddings.shape}")  # (3, embedding_dim)
        """
        if not texts:
            self.logger.debug("Empty text list provided, returning empty array")
            return np.array([])

        self.logger.debug(f"Generating embeddings for {len(texts)} text(s)")

        if self.model:
            # Use model's efficient batch encoding
            embeddings = self.model.encode(
                texts, normalize_embeddings=self.normalize, **options
            )
            return np.array(embeddings)
        else:
            # Fallback: process each text individually
            self.logger.debug("Using fallback method for batch embedding")
            return np.array([self._embed_fallback(text, **options) for text in texts])

    def embed_sentences(self, text: str, **options) -> List[np.ndarray]:
        """
        Generate embeddings for each sentence in text.

        This method splits the input text into sentences and generates an
        embedding for each sentence. Useful for document-level analysis where
        sentence-level embeddings are needed.

        Sentence Splitting:
            - Splits on sentence boundaries (. ! ?)
            - Preserves sentence content
            - Filters out empty sentences

        Args:
            text: Input text containing multiple sentences
            **options: Embedding options passed to embed_batch()

        Returns:
            List of np.ndarray: One embedding vector per sentence.
                               Returns empty list if no sentences found.

        Example:
            >>> text = "First sentence. Second sentence! Third sentence?"
            >>> sentence_embeddings = embedder.embed_sentences(text)
            >>> print(f"Found {len(sentence_embeddings)} sentence embeddings")
        """
        import re

        if not text or not text.strip():
            self.logger.debug("Empty text provided for sentence embedding")
            return []

        # Split text into sentences using punctuation
        sentences = re.split(r"[.!?]+", text)
        # Clean and filter sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            self.logger.debug("No sentences found in text")
            return []

        self.logger.debug(f"Extracting embeddings for {len(sentences)} sentence(s)")

        # Generate embeddings for all sentences in batch
        embeddings = self.embed_batch(sentences, **options)

        # Convert to list of individual embeddings
        return [embeddings[i] for i in range(len(sentences))]

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this embedder.

        Returns the size of the embedding vectors that will be generated.
        Dimension depends on the model used.

        Returns:
            int: Embedding dimension (number of features in embedding vector).
                 - Model-based: Dimension from loaded model (typically 384-768)
                 - Fallback: 128 (hash-based embedding dimension)

        Example:
            >>> embedder = TextEmbedder()
            >>> dim = embedder.get_embedding_dimension()
            >>> print(f"Embedding dimension: {dim}")
        """
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        else:
            return 128  # Fallback hash-based embedding dimension
