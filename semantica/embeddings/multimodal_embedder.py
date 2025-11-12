"""
Multimodal Embedder Module

This module provides comprehensive cross-modal embedding generation capabilities
for the Semantica framework, enabling unified embedding spaces for text, image,
and audio content.

Key Features:
    - Cross-modal embedding generation (text, image, audio)
    - Multimodal embedding combination strategies
    - Cross-modal similarity computation
    - Dimension alignment across modalities
    - Configurable combination methods (concatenation, averaging)

Example Usage:
    >>> from semantica.embeddings import MultimodalEmbedder
    >>> embedder = MultimodalEmbedder()
    >>> embedding = embedder.embed_multimodal(
    ...     text="A cat sitting on a mat",
    ...     image_path="cat.jpg"
    ... )
    >>> similarity = embedder.compute_cross_modal_similarity(
    ...     text="A cat",
    ...     image_path="cat.jpg"
    ... )

Author: Semantica Contributors
License: MIT
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker
from .text_embedder import TextEmbedder
from .image_embedder import ImageEmbedder
from .audio_embedder import AudioEmbedder


class MultimodalEmbedder:
    """
    Multimodal embedding generator for cross-modal semantic representation.
    
    This class provides unified embedding generation across multiple modalities
    (text, image, audio), enabling cross-modal similarity and combined embeddings.
    
    Features:
        - Cross-modal embedding generation
        - Multimodal embedding combination (concatenation, averaging)
        - Cross-modal similarity computation
        - Automatic dimension alignment
        - Configurable normalization
    
    Example Usage:
        >>> embedder = MultimodalEmbedder(
        ...     align_modalities=True,
        ...     normalize=True
        ... )
        >>> # Combined embedding from text and image
        >>> embedding = embedder.embed_multimodal(
        ...     text="A cat",
        ...     image_path="cat.jpg"
        ... )
        >>> # Cross-modal similarity
        >>> similarity = embedder.compute_cross_modal_similarity(
        ...     text="A cat",
        ...     image_path="cat.jpg"
        ... )
    """
    
    def __init__(
        self,
        align_modalities: bool = True,
        normalize: bool = True,
        **config
    ):
        """
        Initialize multimodal embedder.
        
        Sets up embedders for each modality (text, image, audio) and configures
        cross-modal processing options.
        
        Args:
            align_modalities: Whether to align embedding dimensions across modalities
                            before combination (default: True)
            normalize: Whether to normalize embeddings to unit vectors (default: True)
            **config: Additional configuration options:
                - text: Text embedder configuration
                - image: Image embedder configuration
                - audio: Audio embedder configuration
        """
        self.logger = get_logger("multimodal_embedder")
        self.config = config
        
        # Cross-modal configuration
        self.align_modalities = align_modalities
        self.normalize = normalize
        
        # Initialize modality-specific embedders
        text_config = config.get("text", {})
        image_config = config.get("image", {})
        audio_config = config.get("audio", {})
        
        self.text_embedder = TextEmbedder(**text_config)
        self.image_embedder = ImageEmbedder(**image_config)
        self.audio_embedder = AudioEmbedder(**audio_config)
        
        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()
        
        self.logger.debug(
            f"Multimodal embedder initialized "
            f"(align_modalities={align_modalities}, normalize={normalize})"
        )
    
    def embed_text(self, text: str, **options) -> np.ndarray:
        """
        Generate embedding for text using text embedder.
        
        Convenience method that delegates to the text embedder.
        
        Args:
            text: Input text string to embed
            **options: Embedding options passed to text embedder
        
        Returns:
            np.ndarray: Text embedding vector
        """
        return self.text_embedder.embed_text(text, **options)
    
    def embed_image(self, image_path: Union[str, Path], **options) -> np.ndarray:
        """
        Generate embedding for image using image embedder.
        
        Convenience method that delegates to the image embedder.
        
        Args:
            image_path: Path to image file
            **options: Embedding options passed to image embedder
        
        Returns:
            np.ndarray: Image embedding vector
        """
        return self.image_embedder.embed_image(image_path, **options)
    
    def embed_audio(self, audio_path: Union[str, Path], **options) -> np.ndarray:
        """
        Generate embedding for audio using audio embedder.
        
        Convenience method that delegates to the audio embedder.
        
        Args:
            audio_path: Path to audio file
            **options: Embedding options passed to audio embedder
        
        Returns:
            np.ndarray: Audio embedding vector
        """
        return self.audio_embedder.embed_audio(audio_path, **options)
    
    def embed_multimodal(
        self,
        text: Optional[str] = None,
        image_path: Optional[Union[str, Path]] = None,
        audio_path: Optional[Union[str, Path]] = None,
        combine_method: str = "concat",
        **options
    ) -> np.ndarray:
        """
        Generate multimodal embedding from multiple input modalities.
        
        This method combines embeddings from different modalities (text, image, audio)
        into a single unified embedding vector. Supports concatenation or averaging
        as combination strategies.
        
        Combination Methods:
            - "concat": Concatenate embeddings (default) - preserves all information
            - "mean": Average embeddings - creates compact representation
        
        Args:
            text: Input text string (optional)
            image_path: Path to image file (optional)
            audio_path: Path to audio file (optional)
            combine_method: Method to combine embeddings - "concat" or "mean" (default: "concat")
            **options: Additional embedding options passed to individual embedders
        
        Returns:
            np.ndarray: Combined multimodal embedding vector.
                       If only one modality provided, returns that embedding directly.
        
        Raises:
            ProcessingError: If no inputs provided or embedding generation fails
        
        Example:
            >>> # Text + Image
            >>> embedding = embedder.embed_multimodal(
            ...     text="A cat",
            ...     image_path="cat.jpg",
            ...     combine_method="concat"
            ... )
            >>> # All three modalities
            >>> embedding = embedder.embed_multimodal(
            ...     text="Speech about cats",
            ...     image_path="cat.jpg",
            ...     audio_path="speech.wav"
            ... )
        """
        # Track multimodal embedding
        modalities = []
        if text:
            modalities.append("text")
        if image_path:
            modalities.append("image")
        if audio_path:
            modalities.append("audio")
        
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="embeddings",
            submodule="MultimodalEmbedder",
            message=f"Generating multimodal embedding ({', '.join(modalities)})"
        )
        
        try:
            embeddings = []
            
            # Embed each provided modality
            if text:
                self.logger.debug("Embedding text modality")
                self.progress_tracker.update_tracking(tracking_id, message="Generating text embedding...")
                text_emb = self.embed_text(text, **options)
                embeddings.append(text_emb)
            
            if image_path:
                self.logger.debug(f"Embedding image modality: {image_path}")
                self.progress_tracker.update_tracking(tracking_id, message="Generating image embedding...")
                img_emb = self.embed_image(image_path, **options)
                embeddings.append(img_emb)
            
            if audio_path:
                self.logger.debug(f"Embedding audio modality: {audio_path}")
                self.progress_tracker.update_tracking(tracking_id, message="Generating audio embedding...")
                audio_emb = self.embed_audio(audio_path, **options)
                embeddings.append(audio_emb)
            
            # Validate at least one input provided
            if not embeddings:
                raise ProcessingError(
                    "At least one input (text, image, or audio) is required "
                    "for multimodal embedding"
                )
            
            # If only one modality, return it directly
            if len(embeddings) == 1:
                self.logger.debug("Single modality provided, returning directly")
                self.progress_tracker.stop_tracking(tracking_id, status="completed",
                                                   message=f"Generated {modalities[0]} embedding")
                return embeddings[0]
            
            # Align dimensions if needed (ensures all embeddings have same dimension)
            if self.align_modalities:
                self.logger.debug("Aligning embedding dimensions across modalities")
                self.progress_tracker.update_tracking(tracking_id, message="Aligning embedding dimensions...")
                embeddings = self._align_dimensions(embeddings)
            
            # Combine embeddings using specified method
            self.progress_tracker.update_tracking(tracking_id, message=f"Combining embeddings using {combine_method}...")
            if combine_method == "concat":
                # Concatenate: preserves all information, larger dimension
                combined = np.concatenate(embeddings)
                self.logger.debug(
                    f"Combined {len(embeddings)} embeddings via concatenation: "
                    f"shape {combined.shape}"
                )
            elif combine_method == "mean":
                # Average: compact representation, same dimension as inputs
                combined = np.mean(embeddings, axis=0)
                self.logger.debug(
                    f"Combined {len(embeddings)} embeddings via averaging: "
                    f"shape {combined.shape}"
                )
            else:
                raise ProcessingError(
                    f"Unsupported combine_method: {combine_method}. "
                    "Use 'concat' or 'mean'."
                )
            
            # Normalize if requested
            if self.normalize:
                self.progress_tracker.update_tracking(tracking_id, message="Normalizing embedding...")
                norm = np.linalg.norm(combined)
                if norm > 0:
                    combined = combined / norm
            
            self.progress_tracker.stop_tracking(tracking_id, status="completed",
                                               message=f"Generated multimodal embedding (dim: {len(combined)})")
            return combined
            
        except Exception as e:
            self.progress_tracker.stop_tracking(tracking_id, status="failed", message=str(e))
            raise
    
    def _align_dimensions(self, embeddings: List[np.ndarray]) -> List[np.ndarray]:
        """
        Align embedding dimensions across different modalities.
        
        This method ensures all embeddings have the same dimension by truncating
        larger embeddings or padding smaller ones. Uses the minimum dimension
        as the target to preserve information from all modalities.
        
        Args:
            embeddings: List of embedding vectors with potentially different dimensions
        
        Returns:
            List of np.ndarray: Aligned embeddings, all with same dimension
        """
        if not embeddings:
            return []
        
        # Find target dimension (use minimum to preserve information)
        dims = [emb.shape[0] for emb in embeddings]
        target_dim = min(dims)
        
        self.logger.debug(
            f"Aligning embeddings: dimensions {dims} -> target {target_dim}"
        )
        
        aligned = []
        for i, emb in enumerate(embeddings):
            if emb.shape[0] == target_dim:
                # Already correct dimension
                aligned.append(emb)
            elif emb.shape[0] > target_dim:
                # Truncate: take first target_dim elements
                aligned.append(emb[:target_dim])
                self.logger.debug(
                    f"Truncated embedding {i} from {emb.shape[0]} to {target_dim}"
                )
            else:
                # Pad: add zeros to reach target dimension
                padding = target_dim - emb.shape[0]
                padded = np.pad(emb, (0, padding), 'constant')
                aligned.append(padded)
                self.logger.debug(
                    f"Padded embedding {i} from {emb.shape[0]} to {target_dim}"
                )
        
        return aligned
    
    def compute_cross_modal_similarity(
        self,
        text: Optional[str] = None,
        image_path: Optional[Union[str, Path]] = None,
        audio_path: Optional[Union[str, Path]] = None,
        **options
    ) -> float:
        """
        Compute similarity between different input modalities.
        
        This method calculates the semantic similarity between embeddings from
        different modalities (e.g., text and image, image and audio). Useful for
        cross-modal retrieval and matching tasks.
        
        The method computes pairwise cosine similarities between all provided
        modalities and returns the average similarity score.
        
        Args:
            text: Input text string (optional)
            image_path: Path to image file (optional)
            audio_path: Path to audio file (optional)
            **options: Additional embedding options passed to embedders
        
        Returns:
            float: Average pairwise similarity score between modalities (0-1).
                   Higher values indicate greater semantic similarity.
        
        Raises:
            ProcessingError: If fewer than two modalities provided or embedding fails
        
        Example:
            >>> # Text-Image similarity
            >>> similarity = embedder.compute_cross_modal_similarity(
            ...     text="A cat sitting on a mat",
            ...     image_path="cat.jpg"
            ... )
            >>> print(f"Text-Image similarity: {similarity:.3f}")
            >>> # All three modalities
            >>> similarity = embedder.compute_cross_modal_similarity(
            ...     text="Speech about cats",
            ...     image_path="cat.jpg",
            ...     audio_path="speech.wav"
            ... )
        """
        embeddings = {}
        
        # Generate embeddings for each provided modality
        if text:
            self.logger.debug("Computing text embedding for similarity")
            embeddings['text'] = self.embed_text(text, **options)
        
        if image_path:
            self.logger.debug(f"Computing image embedding for similarity: {image_path}")
            embeddings['image'] = self.embed_image(image_path, **options)
        
        if audio_path:
            self.logger.debug(f"Computing audio embedding for similarity: {audio_path}")
            embeddings['audio'] = self.embed_audio(audio_path, **options)
        
        # Validate at least two modalities provided
        if len(embeddings) < 2:
            raise ProcessingError(
                f"At least two modalities required for cross-modal similarity. "
                f"Provided: {list(embeddings.keys())}"
            )
        
        # Get list of embeddings for pairwise comparison
        emb_list = list(embeddings.values())
        
        # Align dimensions for fair comparison
        aligned = self._align_dimensions(emb_list)
        
        # Compute pairwise cosine similarities
        similarities = []
        for i in range(len(aligned)):
            for j in range(i + 1, len(aligned)):
                similarity = self._cosine_similarity(aligned[i], aligned[j])
                similarities.append(similarity)
                self.logger.debug(
                    f"Similarity between modality {i} and {j}: {similarity:.3f}"
                )
        
        # Return average similarity
        avg_similarity = np.mean(similarities) if similarities else 0.0
        self.logger.debug(f"Average cross-modal similarity: {avg_similarity:.3f}")
        
        return avg_similarity
    
    def _cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embedding vectors.
        
        Cosine similarity measures the cosine of the angle between two vectors,
        providing a normalized similarity score between -1 and 1. For normalized
        embeddings, this ranges from 0 to 1.
        
        Args:
            emb1: First embedding vector
            emb2: Second embedding vector
        
        Returns:
            float: Cosine similarity score (0-1 for normalized embeddings).
                   Returns 0.0 if either vector has zero norm.
        """
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        # Handle zero-norm vectors
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
