## Description

Fixes #145 - Groq LLM API key not being passed to provider in `NERExtractor`, `RelationExtractor`, and `TripletExtractor` when using `method="llm"`, causing extraction to return zero results.

## Type of Change

- [x] Bug fix (non-breaking change which fixes an issue)

## Related Issues

Fixes #145

## Changes Made

1. **API Key Handling** (`semantica/semantic_extract/methods.py`):
   - Added API key extraction from `kwargs` in `extract_entities_llm()`, `extract_relations_llm()`, and `extract_triplets_llm()`
   - All functions now pass `api_key` to `create_provider()` via `provider_kwargs`
   - Added environment variable fallback: `{PROVIDER}_API_KEY` (e.g., `GROQ_API_KEY`)

2. **Consistency**:
   - Added `llm_model` parameter support in `extract_triplets_llm()` for consistency

3. **Bug Fix**:
   - Fixed relation extraction: added type checking for `subject_text`/`object_text` to prevent `'bool' object has no attribute 'lower'` error

4. **Optional Dependencies** (`pyproject.toml`):
   - Added `llm-deepseek` optional dependency group

## Testing

- [x] Tested locally
- [x] All tests pass

**Test Results:**
- ✅ Groq LLM Initialization: PASS
- ✅ NER Extraction: PASS (10-14 entities)
- ✅ Relation Extraction: PASS (3-10 relations)
- ✅ Triplet Extraction: PASS (6-8 triplets)

## Breaking Changes

**No** - Backward compatible bug fix

## Impact

- **Severity**: High - Previously blocked all Groq LLM usage for semantic extraction
- **Resolution**: Groq LLM now works correctly for all extraction methods

## Files Changed

- `semantica/semantic_extract/methods.py` - Core API key handling fixes
- `semantica/semantic_extract/providers.py` - Linter warning fixes
- `pyproject.toml` - Added `llm-deepseek` dependency

## Example

**Before:**
```python
ner = NERExtractor(method="llm", provider="groq", api_key="key")
entities = ner.extract_entities("Apple Inc. was founded by Steve Jobs.")
# Returns: []  ❌
```

**After:**
```python
ner = NERExtractor(method="llm", provider="groq", api_key="key")
entities = ner.extract_entities("Apple Inc. was founded by Steve Jobs.")
# Returns: [Entity("Apple Inc.", "ORG"), Entity("Steve Jobs", "PERSON")]  ✅
```

