"""
Image Embedder Module

This module provides comprehensive image embedding generation capabilities for the
Semantica framework, supporting CLIP models and fallback methods for image analysis.

Key Features:
    - CLIP model integration for high-quality image embeddings
    - Batch processing for multiple images
    - Fallback image feature extraction
    - Configurable normalization and device selection
    - Support for various image formats (JPEG, PNG, etc.)

Example Usage:
    >>> from semantica.embeddings import ImageEmbedder
    >>> embedder = ImageEmbedder(model_name="ViT-B/32")
    >>> embedding = embedder.embed_image("image.jpg")
    >>> batch_embeddings = embedder.embed_batch(["img1.jpg", "img2.png"])

Author: Semantica Contributors
License: MIT
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
from PIL import Image

from ..utils.exceptions import ProcessingError, ValidationError
from ..utils.logging import get_logger

try:
    import clip
    import torch

    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False


class ImageEmbedder:
    """
    Image embedding generator for semantic image representation.

    This class provides image embedding generation using CLIP models or fallback
    methods. Supports single images, batch processing, and various image formats.

    Features:
        - CLIP model integration for high-quality image embeddings
        - Batch processing for multiple images
        - Fallback image feature extraction (when CLIP unavailable)
        - Configurable normalization and device selection
        - Support for common image formats

    Example Usage:
        >>> embedder = ImageEmbedder(
        ...     model_name="ViT-B/32",
        ...     device="cpu",
        ...     normalize=True
        ... )
        >>> embedding = embedder.embed_image("photo.jpg")
        >>> dim = embedder.get_embedding_dimension()
    """

    def __init__(
        self,
        model_name: str = "ViT-B/32",
        device: str = "cpu",
        normalize: bool = True,
        **config,
    ):
        """
        Initialize image embedder.

        Sets up the embedder with the specified CLIP model and configuration.
        Attempts to load CLIP model, falls back to feature-based embeddings
        if unavailable.

        Args:
            model_name: Name of CLIP model to use (default: "ViT-B/32")
            device: Device to run model on - "cpu" or "cuda" (default: "cpu")
            normalize: Whether to normalize embeddings to unit vectors (default: True)
            **config: Additional configuration options
        """
        self.logger = get_logger("image_embedder")
        self.config = config

        # Model configuration
        self.model_name = model_name
        self.device = device
        self.normalize = normalize

        # Initialize model (will be None if CLIP unavailable)
        self.model = None
        self.preprocess = None

        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()

        self._initialize_model()

    def _initialize_model(self) -> None:
        """
        Initialize CLIP model.

        Attempts to load the specified CLIP model and preprocessing function.
        If unavailable or loading fails, falls back to feature-based embedding
        method. Logs warnings but doesn't raise errors to allow graceful degradation.
        """
        if CLIP_AVAILABLE:
            try:
                self.model, self.preprocess = clip.load(
                    self.model_name, device=self.device
                )
                self.logger.info(
                    f"Loaded CLIP model: {self.model_name} (device: {self.device})"
                )
            except Exception as e:
                self.logger.warning(
                    f"Failed to load CLIP model '{self.model_name}': {e}. "
                    "Using fallback image embedding method."
                )
                self.model = None
                self.preprocess = None
        else:
            self.logger.warning(
                "CLIP not available. Install with: pip install clip-by-openai. "
                "Using fallback image embedding method."
            )

    def embed_image(self, image_path: Union[str, Path], **options) -> np.ndarray:
        """
        Generate embedding for a single image file.

        This method creates a semantic embedding vector for the input image using
        the configured CLIP model or fallback method. Returns a normalized vector
        suitable for similarity calculations.

        Args:
            image_path: Path to image file. Supports common formats (JPEG, PNG, etc.)
            **options: Additional embedding options (currently unused)

        Returns:
            np.ndarray: 1D embedding vector of shape (embedding_dim,).
                       Dimension depends on model (typically 512 for CLIP ViT-B/32).

        Raises:
            ValidationError: If image file doesn't exist
            ProcessingError: If image cannot be processed or embedded

        Example:
            >>> embedder = ImageEmbedder()
            >>> embedding = embedder.embed_image("photo.jpg")
            >>> print(f"Embedding shape: {embedding.shape}")
        """
        # Track image embedding
        tracking_id = self.progress_tracker.start_tracking(
            file=str(image_path),
            module="embeddings",
            submodule="ImageEmbedder",
            message=f"Generating image embedding: {image_path}",
        )

        try:
            image_path = Path(image_path)

            # Validate image file exists
            if not image_path.exists():
                self.progress_tracker.stop_tracking(
                    tracking_id,
                    status="failed",
                    message=f"File not found: {image_path}",
                )
                raise ValidationError(
                    f"Image file not found: {image_path}. "
                    "Please provide a valid image file path."
                )

            if not image_path.is_file():
                self.progress_tracker.stop_tracking(
                    tracking_id,
                    status="failed",
                    message=f"Path is not a file: {image_path}",
                )
                raise ValidationError(f"Path is not a file: {image_path}")

            self.logger.debug(f"Generating embedding for image: {image_path}")

            # Use CLIP if available, otherwise fallback
            if self.model and self.preprocess:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Using CLIP model..."
                )
                result = self._embed_with_clip(image_path, **options)
            else:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Using fallback method..."
                )
                result = self._embed_fallback(image_path, **options)

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

    def _embed_with_clip(self, image_path: Path, **options) -> np.ndarray:
        """
        Embed image using CLIP model.

        This method uses the loaded CLIP model to generate high-quality semantic
        embeddings that capture visual content and can be compared with text
        embeddings in the same space.

        Args:
            image_path: Path to image file
            **options: Unused (for compatibility)

        Returns:
            np.ndarray: CLIP embedding vector

        Raises:
            ProcessingError: If image processing or embedding fails
        """
        try:
            # Load and preprocess image
            image = Image.open(image_path)
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)

            # Generate embedding (no gradient computation needed)
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)

            # Extract embedding and convert to numpy
            embedding = image_features[0].cpu().numpy().astype(np.float32)

            # Normalize if requested
            if self.normalize:
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm

            self.logger.debug(f"Generated CLIP embedding: shape {embedding.shape}")
            return embedding

        except Exception as e:
            error_msg = f"Failed to embed image with CLIP: {e}"
            self.logger.error(error_msg)
            raise ProcessingError(error_msg) from e

    def _embed_fallback(self, image_path: Path, **options) -> np.ndarray:
        """
        Fallback embedding using image feature extraction.

        This method generates a simple embedding from image pixel data when
        CLIP is not available. Resizes image to fixed size and extracts
        pixel features as embedding.

        Note: This is a basic feature extraction method and does not provide
        semantic embeddings. For production use, CLIP is recommended.

        Args:
            image_path: Path to image file
            **options: Unused (for compatibility)

        Returns:
            np.ndarray: 512-dimensional feature-based embedding vector

        Raises:
            ProcessingError: If image cannot be processed
        """
        try:
            # Load image
            image = Image.open(image_path)

            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Resize to fixed size for consistent feature extraction
            image = image.resize((224, 224))

            # Convert to numpy array
            img_array = np.array(image).astype(np.float32)

            # Flatten image to 1D array
            flat = img_array.flatten()

            # Downsample to fixed dimension (512)
            if len(flat) > 512:
                # Sample evenly across the flattened array
                step = len(flat) // 512
                embedding = flat[::step][:512]
            else:
                # Pad with zeros if smaller than target dimension
                embedding = np.pad(flat, (0, 512 - len(flat)), "constant")[:512]

            # Normalize if requested
            if self.normalize:
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm

            self.logger.debug(f"Generated fallback embedding: shape {embedding.shape}")
            return embedding.astype(np.float32)

        except Exception as e:
            error_msg = f"Failed to embed image: {e}"
            self.logger.error(error_msg)
            raise ProcessingError(error_msg) from e

    def embed_batch(self, image_paths: List[Union[str, Path]], **options) -> np.ndarray:
        """
        Generate embeddings for multiple images in batch.

        This method processes multiple images sequentially and returns their
        embeddings as a batch array. Useful for processing image collections.

        Args:
            image_paths: List of image file paths. Empty list returns empty array.
            **options: Additional embedding options passed to embed_image()

        Returns:
            np.ndarray: 2D array of embeddings with shape (n_images, embedding_dim).
                       Returns empty array if input list is empty.

        Raises:
            ProcessingError: If any image cannot be processed (processing continues
                           for other images, but errors are logged)

        Example:
            >>> image_paths = ["img1.jpg", "img2.png", "img3.jpeg"]
            >>> embeddings = embedder.embed_batch(image_paths)
            >>> print(f"Shape: {embeddings.shape}")  # (3, embedding_dim)
        """
        if not image_paths:
            self.logger.debug("Empty image list provided, returning empty array")
            return np.array([])

        self.logger.info(f"Generating embeddings for {len(image_paths)} image(s)")

        embeddings = []
        failed_count = 0

        # Process each image
        for image_path in image_paths:
            try:
                embedding = self.embed_image(image_path, **options)
                embeddings.append(embedding)
            except Exception as e:
                failed_count += 1
                self.logger.warning(
                    f"Failed to embed image {image_path}: {e}. "
                    "Continuing with other images."
                )

        if failed_count > 0:
            self.logger.warning(
                f"Failed to embed {failed_count} out of {len(image_paths)} image(s)"
            )

        if not embeddings:
            raise ProcessingError(
                f"Failed to embed any images from {len(image_paths)} provided"
            )

        self.logger.info(f"Successfully generated {len(embeddings)} embedding(s)")

        return np.array(embeddings)

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this embedder.

        Returns the size of the embedding vectors that will be generated.
        Dimension depends on the model used.

        Returns:
            int: Embedding dimension (number of features in embedding vector).
                 - CLIP model: Dimension from model (typically 512 for ViT-B/32)
                 - Fallback: 512 (feature-based embedding dimension)

        Example:
            >>> embedder = ImageEmbedder()
            >>> dim = embedder.get_embedding_dimension()
            >>> print(f"Embedding dimension: {dim}")
        """
        if self.model:
            return self.model.visual.output_dim
        else:
            return 512  # Fallback feature-based embedding dimension
