# Fix & Align Split Module with Documentation

## 📝 Summary
This PR aligns the `semantica.split` module with its documentation, ensuring that all documented chunking strategies are fully implemented, registered, and accessible via the unified `TextSplitter` interface. It specifically enables direct usage of "structural" and "sliding_window" methods and fixes kwargs handling in hierarchical chunking.

## 🚀 Motivation
Previously, the `docs/reference/split.md` documentation listed "structural" and "sliding_window" as available methods for `TextSplitter`, but they were not registered in the `_SPLIT_METHODS` dictionary in `methods.py`. This caused `TextSplitter(method="structural")` to fail or fallback unexpectedly. Additionally, there were minor discrepancies in method signatures and argument handling (specifically `chunk_size` collisions) that needed resolution.

## 🔍 Key Changes

### 1. Method Registration & Implementation
- **New Wrappers**: Added `split_structural` and `split_sliding_window` wrapper functions in `semantica/split/methods.py`.
- **Registry Update**: Registered these methods in `_SPLIT_METHODS`, enabling:
  ```python
  # Now works out-of-the-box
  splitter = TextSplitter(method="structural")
  splitter = TextSplitter(method="sliding_window")
  ```
- **Conditional Imports**: Added robust import handling for specialized chunkers to ensure the module remains usable even if optional dependencies are missing.

### 2. Documentation Alignment (`docs/reference/split.md`)
- **Signature Updates**: Updated method signatures in the documentation to exactly match the code implementation (e.g., `StructuralChunker`, `TableChunker`).
- **TableChunker**: Clarified `TableChunker` usage, documenting its specialized methods (`chunk_table`, `chunk_to_text_chunks`) since it handles structured data differently from standard text splitters.
- **NER Aliases**: Confirmed and documented support for `ner_method="ml"` (mapping to spaCy) in Entity/Relation aware chunking.

### 3. Bug Fixes
- **Hierarchical Splitting**: Fixed a `TypeError: multiple values for keyword argument 'chunk_size'` bug in `split_hierarchical` by properly managing `kwargs` when delegating to sub-splitters (paragraph/sentence).
- **Import Handling**: Resolved potential circular imports and improved error messages for missing dependencies.

## 🧪 Verification
- [x] **Registry Check**: Verified that `list_available_methods()` now returns `structural` and `sliding_window`.
- [x] **Runtime Verification**: Confirmed `TextSplitter` successfully delegates to the new wrappers.
- [x] **Documentation**: Verified that documentation tables match the actual code capabilities.
- [x] **Kwargs Handling**: Verified hierarchical splitting no longer throws duplicate argument errors.

## ✅ Checklist
- [x] Code follows the project's coding standards.
- [x] Documentation has been updated to reflect the changes.
- [x] All chunking strategies listed in docs are now functionally accessible.
