# Data Normalization Module Usage Guide

This comprehensive guide demonstrates how to use the data normalization module for text normalization, entity normalization, date/time normalization, number/quantity normalization, data cleaning, language detection, and encoding handling.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Text Normalization](#text-normalization)
3. [Entity Normalization](#entity-normalization)
4. [Date/Time Normalization](#datetime-normalization)
5. [Number/Quantity Normalization](#numberquantity-normalization)
6. [Data Cleaning](#data-cleaning)
7. [Language Detection](#language-detection)
8. [Encoding Handling](#encoding-handling)
9. [Using Methods](#using-methods)
10. [Using Registry](#using-registry)
11. [Configuration](#configuration)
12. [Advanced Examples](#advanced-examples)

## Basic Usage

### Using the Convenience Functions

```python
from semantica.normalize import normalize_text, normalize_entity, normalize_date

# Normalize text
text = normalize_text("Hello   World", method="default")
print(f"Normalized: {text}")

# Normalize entity
entity = normalize_entity("John Doe", entity_type="Person", method="default")
print(f"Normalized entity: {entity}")

# Normalize date
date = normalize_date("2023-01-15", method="default")
print(f"Normalized date: {date}")
```

### Using Main Classes

```python
from semantica.normalize import TextNormalizer, EntityNormalizer, DateNormalizer

# Create normalizers
text_norm = TextNormalizer()
entity_norm = EntityNormalizer()
date_norm = DateNormalizer()

# Normalize text
normalized_text = text_norm.normalize_text("Hello   World", case="lower")

# Normalize entity
normalized_entity = entity_norm.normalize_entity("John Doe", entity_type="Person")

# Normalize date
normalized_date = date_norm.normalize_date("2023-01-15", format="ISO8601")
```

## Text Normalization

### Basic Text Normalization

```python
from semantica.normalize import normalize_text, TextNormalizer

# Using convenience function
normalized = normalize_text("Hello   World", method="default")
print(f"Normalized: {normalized}")

# Using class directly
normalizer = TextNormalizer()
normalized = normalizer.normalize_text("Hello   World", case="lower")
```

### Unicode Normalization

```python
from semantica.normalize import normalize_text, UnicodeNormalizer

# Normalize with different Unicode forms
nfc = normalize_text("café", method="default", unicode_form="NFC")
nfd = normalize_text("café", method="default", unicode_form="NFD")
nfkc = normalize_text("café", method="default", unicode_form="NFKC")
nfkd = normalize_text("café", method="default", unicode_form="NFKD")

# Using UnicodeNormalizer directly
unicode_norm = UnicodeNormalizer()
normalized = unicode_norm.normalize_unicode("café", form="NFC")
```

### Whitespace Normalization

```python
from semantica.normalize import normalize_text, WhitespaceNormalizer

# Normalize whitespace
normalized = normalize_text(
    "Hello   World\n\nTest",
    method="default",
    line_break_type="unix"
)

# Using WhitespaceNormalizer directly
whitespace_norm = WhitespaceNormalizer()
normalized = whitespace_norm.normalize_whitespace(
    "Hello   World",
    line_break_type="unix"
)
```

### Case Normalization

```python
from semantica.normalize import normalize_text

# Lowercase
lower = normalize_text("Hello World", method="default", case="lower")

# Uppercase
upper = normalize_text("Hello World", method="default", case="upper")

# Title case
title = normalize_text("hello world", method="default", case="title")

# Preserve case
preserved = normalize_text("Hello World", method="default", case="preserve")
```

### Special Character Processing

```python
from semantica.normalize import normalize_text, SpecialCharacterProcessor

# Normalize with special character processing
normalized = normalize_text(
    "Hello—World",
    method="default",
    normalize_diacritics=True
)

# Using SpecialCharacterProcessor directly
char_processor = SpecialCharacterProcessor()
processed = char_processor.process_special_chars("Hello—World")
```

### Text Cleaning

```python
from semantica.normalize import clean_text, TextCleaner

# Using convenience function
cleaned = clean_text(
    "<p>Hello World</p>",
    method="default",
    remove_html=True,
    normalize_whitespace=True
)

# Using TextCleaner directly
cleaner = TextCleaner()
cleaned = cleaner.clean(
    "<p>Hello World</p>",
    remove_html=True,
    normalize_unicode=True
)
```

### Batch Text Processing

```python
from semantica.normalize import TextNormalizer

normalizer = TextNormalizer()

texts = [
    "Hello   World",
    "Test   Text",
    "Another   Example"
]

# Process batch
normalized_texts = normalizer.process_batch(texts, case="lower")
for text in normalized_texts:
    print(text)
```

## Entity Normalization

### Basic Entity Normalization

```python
from semantica.normalize import normalize_entity, EntityNormalizer

# Using convenience function
normalized = normalize_entity(
    "John Doe",
    entity_type="Person",
    method="default"
)

# Using class directly
normalizer = EntityNormalizer()
normalized = normalizer.normalize_entity("John Doe", entity_type="Person")
```

### Alias Resolution

```python
from semantica.normalize import resolve_aliases, AliasResolver

# Using convenience function
canonical = resolve_aliases(
    "J. Doe",
    entity_type="Person",
    method="default"
)

# Using AliasResolver directly
resolver = AliasResolver(alias_map={"j. doe": "John Doe"})
canonical = resolver.resolve_aliases("J. Doe", entity_type="Person")
```

### Entity Disambiguation

```python
from semantica.normalize import disambiguate_entity, EntityDisambiguator

# Using convenience function
result = disambiguate_entity(
    "Apple",
    method="default",
    entity_type="Organization",
    context="technology company"
)

print(f"Entity: {result['entity_name']}")
print(f"Type: {result['entity_type']}")
print(f"Confidence: {result['confidence']}")
print(f"Candidates: {result['candidates']}")

# Using EntityDisambiguator directly
disambiguator = EntityDisambiguator()
result = disambiguator.disambiguate("Apple", entity_type="Organization")
```

### Entity Linking

```python
from semantica.normalize import EntityNormalizer

normalizer = EntityNormalizer()

entities = [
    "John Doe",
    "J. Doe",
    "Johnny Doe"
]

# Link entities to canonical forms
linked = normalizer.link_entities(entities, entity_type="Person")
for original, canonical in linked.items():
    print(f"{original} -> {canonical}")
```

### Name Variant Handling

```python
from semantica.normalize import EntityNormalizer, NameVariantHandler

normalizer = EntityNormalizer()

# Normalize with variant handling
normalized = normalizer.normalize_entity(
    "Dr. John Doe",
    entity_type="Person"
)

# Using NameVariantHandler directly
variant_handler = NameVariantHandler()
normalized = variant_handler.normalize_name_format(
    "Dr. John Doe",
    format_type="standard"
)
```

## Date/Time Normalization

### Basic Date Normalization

```python
from semantica.normalize import normalize_date, DateNormalizer

# Using convenience function
normalized = normalize_date("2023-01-15", method="default")
print(f"Normalized: {normalized}")

# Using class directly
normalizer = DateNormalizer()
normalized = normalizer.normalize_date("2023-01-15", format="ISO8601")
```

### Different Date Formats

```python
from semantica.normalize import normalize_date

# ISO8601 format
iso_date = normalize_date("2023-01-15", format="ISO8601", method="default")

# Date only
date_only = normalize_date("2023-01-15", format="date", method="default")

# Custom format
custom = normalize_date("2023-01-15", format="%Y-%m-%d", method="default")
```

### Timezone Normalization

```python
from semantica.normalize import normalize_date, TimeZoneNormalizer

# Normalize with timezone
normalized = normalize_date(
    "2023-01-15T10:30:00",
    timezone="America/New_York",
    method="default"
)

# Using TimeZoneNormalizer directly
tz_norm = TimeZoneNormalizer()
from datetime import datetime
dt = datetime(2023, 1, 15, 10, 30, 0)
utc_dt = tz_norm.convert_to_utc(dt)
```

### Relative Date Processing

```python
from semantica.normalize import normalize_date, RelativeDateProcessor

# Process relative dates
yesterday = normalize_date("yesterday", method="relative")
three_days_ago = normalize_date("3 days ago", method="relative")
next_week = normalize_date("next week", method="relative")

# Using RelativeDateProcessor directly
relative_processor = RelativeDateProcessor()
dt = relative_processor.process_relative_expression("3 days ago")
```

### Time Normalization

```python
from semantica.normalize import normalize_time, DateNormalizer

# Normalize time
normalized = normalize_time("10:30:00", method="default")
print(f"Normalized time: {normalized}")

# Using DateNormalizer directly
normalizer = DateNormalizer()
normalized = normalizer.normalize_time("10:30 AM")
```

### Temporal Expression Parsing

```python
from semantica.normalize import DateNormalizer, TemporalExpressionParser

normalizer = DateNormalizer()

# Parse temporal expressions
result = normalizer.parse_temporal_expression("from January to March")
print(f"Date range: {result.get('range')}")

# Using TemporalExpressionParser directly
parser = TemporalExpressionParser()
result = parser.parse_temporal_expression("last week")
```

## Number/Quantity Normalization

### Basic Number Normalization

```python
from semantica.normalize import normalize_number, NumberNormalizer

# Using convenience function
number = normalize_number("1,234.56", method="default")
print(f"Normalized: {number}")

# Using class directly
normalizer = NumberNormalizer()
number = normalizer.normalize_number("1,234.56")
```

### Percentage Handling

```python
from semantica.normalize import normalize_number

# Normalize percentage
percentage = normalize_number("50%", method="default")
print(f"Percentage as decimal: {percentage}")  # 0.5
```

### Scientific Notation

```python
from semantica.normalize import normalize_number, ScientificNotationHandler

# Normalize scientific notation
number = normalize_number("1.5e3", method="default")
print(f"Normalized: {number}")  # 1500.0

# Using ScientificNotationHandler directly
sci_handler = ScientificNotationHandler()
parsed = sci_handler.parse_scientific_notation("1.5e3")
```

### Quantity Normalization

```python
from semantica.normalize import normalize_quantity, NumberNormalizer

# Using convenience function
quantity = normalize_quantity("5 kg", method="default")
print(f"Value: {quantity['value']}, Unit: {quantity['unit']}")

# Using class directly
normalizer = NumberNormalizer()
quantity = normalizer.normalize_quantity("10 meters")
```

### Unit Conversion

```python
from semantica.normalize import NumberNormalizer, UnitConverter

normalizer = NumberNormalizer()

# Convert units
converted = normalizer.convert_units(100, "kg", "pound")
print(f"100 kg = {converted} pounds")

# Using UnitConverter directly
converter = UnitConverter()
converted = converter.convert_units(1, "kilometer", "mile")
```

### Currency Processing

```python
from semantica.normalize import NumberNormalizer, CurrencyNormalizer

normalizer = NumberNormalizer()

# Process currency
currency = normalizer.process_currency("$100", default_currency="USD")
print(f"Amount: {currency['amount']}, Currency: {currency['currency']}")

# Using CurrencyNormalizer directly
currency_norm = CurrencyNormalizer()
currency = currency_norm.normalize_currency("€50", default_currency="EUR")
```

## Data Cleaning

### Basic Data Cleaning

```python
from semantica.normalize import clean_data, DataCleaner

dataset = [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": None},
    {"id": 1, "name": "Alice", "age": 30},  # Duplicate
]

# Using convenience function
cleaned = clean_data(
    dataset,
    remove_duplicates=True,
    validate=True,
    handle_missing=True,
    method="default"
)

# Using class directly
cleaner = DataCleaner()
cleaned = cleaner.clean_data(
    dataset,
    remove_duplicates=True,
    handle_missing=True
)
```

### Duplicate Detection

```python
from semantica.normalize import detect_duplicates, DuplicateDetector

dataset = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 1, "name": "Alice"},  # Duplicate
]

# Using convenience function
duplicates = detect_duplicates(
    dataset,
    threshold=0.8,
    method="default"
)

for group in duplicates:
    print(f"Duplicate group: {len(group.records)} records")
    print(f"Similarity: {group.similarity_score}")

# Using DuplicateDetector directly
detector = DuplicateDetector(similarity_threshold=0.8)
duplicates = detector.detect_duplicates(dataset, key_fields=["id", "name"])
```

### Data Validation

```python
from semantica.normalize import DataCleaner, DataValidator

schema = {
    "fields": {
        "id": {"type": int, "required": True},
        "name": {"type": str, "required": True},
        "age": {"type": int, "required": False}
    }
}

dataset = [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob"},  # Missing age (optional)
    {"id": None, "name": "Charlie"},  # Missing required id
]

# Validate data
cleaner = DataCleaner()
validation = cleaner.validate_data(dataset, schema)

if not validation.valid:
    print(f"Validation errors: {len(validation.errors)}")
    for error in validation.errors:
        print(f"  {error}")

# Using DataValidator directly
validator = DataValidator()
validation = validator.validate_dataset(dataset, schema)
```

### Missing Value Handling

```python
from semantica.normalize import DataCleaner, MissingValueHandler

dataset = [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": None},
    {"id": 3, "name": None, "age": 25},
]

# Handle missing values with different strategies
cleaner = DataCleaner()

# Remove records with missing values
cleaned_remove = cleaner.handle_missing_values(dataset, strategy="remove")

# Fill missing values
cleaned_fill = cleaner.handle_missing_values(
    dataset,
    strategy="fill",
    fill_value="Unknown"
)

# Impute missing values
cleaned_impute = cleaner.handle_missing_values(
    dataset,
    strategy="impute",
    method="mean"
)

# Using MissingValueHandler directly
handler = MissingValueHandler()
cleaned = handler.handle_missing_values(dataset, strategy="remove")
```

## Language Detection

### Basic Language Detection

```python
from semantica.normalize import detect_language, LanguageDetector

# Using convenience function
language = detect_language("Hello world", method="default")
print(f"Detected language: {language}")

# Using class directly
detector = LanguageDetector()
language = detector.detect("Bonjour le monde")
```

### Detection with Confidence

```python
from semantica.normalize import detect_language

# Detect with confidence score
lang, confidence = detect_language(
    "Bonjour le monde",
    method="confidence"
)

print(f"Language: {lang}, Confidence: {confidence:.2f}")
```

### Multiple Language Detection

```python
from semantica.normalize import LanguageDetector

detector = LanguageDetector()

# Detect top N languages
languages = detector.detect_multiple(
    "Hello world. Bonjour le monde.",
    top_n=3
)

for lang, conf in languages:
    print(f"{lang}: {conf:.2f}")
```

### Language Validation

```python
from semantica.normalize import LanguageDetector

detector = LanguageDetector()

# Check if text is in specific language
is_english = detector.is_language("Hello world", "en")
is_french = detector.is_language("Bonjour", "fr")

print(f"Is English: {is_english}")
print(f"Is French: {is_french}")
```

## Encoding Handling

### Encoding Detection

```python
from semantica.normalize import handle_encoding, EncodingHandler

# Using convenience function
encoding, confidence = handle_encoding(
    data,
    operation="detect",
    method="default"
)

print(f"Encoding: {encoding}, Confidence: {confidence:.2f}")

# Using EncodingHandler directly
handler = EncodingHandler()
encoding, confidence = handler.detect(data)
```

### UTF-8 Conversion

```python
from semantica.normalize import handle_encoding, EncodingHandler

# Convert to UTF-8
utf8_text = handle_encoding(
    data,
    operation="convert",
    method="default",
    source_encoding="latin-1"
)

# Using EncodingHandler directly
handler = EncodingHandler()
utf8_text = handler.convert_to_utf8(data, source_encoding="latin-1")
```

### BOM Removal

```python
from semantica.normalize import handle_encoding, EncodingHandler

# Remove BOM
cleaned = handle_encoding(
    data,
    operation="remove_bom",
    method="default"
)

# Using EncodingHandler directly
handler = EncodingHandler()
cleaned = handler.remove_bom(data)
```

### File Encoding Conversion

```python
from semantica.normalize import EncodingHandler

handler = EncodingHandler()

# Convert file to UTF-8
handler.convert_file_to_utf8("input.txt", "output.txt")

# Detect file encoding
encoding, confidence = handler.detect_file("input.txt")
print(f"File encoding: {encoding}")
```

## Using Methods

### Getting Available Methods

```python
from semantica.normalize.methods import get_normalize_method, list_available_methods

# List all available methods
all_methods = list_available_methods()
print("Available methods:", all_methods)

# List methods for specific task
text_methods = list_available_methods("text")
print("Text normalization methods:", text_methods)

# Get specific method
normalize_method = get_normalize_method("text", "default")
if normalize_method:
    result = normalize_method("Hello   World")
```

### Method Examples

```python
from semantica.normalize.methods import (
    normalize_text,
    clean_text,
    normalize_entity,
    resolve_aliases,
    disambiguate_entity,
    normalize_date,
    normalize_time,
    normalize_number,
    normalize_quantity,
    clean_data,
    detect_duplicates,
    detect_language,
    handle_encoding
)

# Text normalization
text = normalize_text("Hello   World", method="default")

# Text cleaning
cleaned = clean_text("<p>Hello</p>", method="default", remove_html=True)

# Entity normalization
entity = normalize_entity("John Doe", entity_type="Person", method="default")

# Alias resolution
canonical = resolve_aliases("J. Doe", entity_type="Person", method="default")

# Entity disambiguation
result = disambiguate_entity("Apple", method="default", entity_type="Organization")

# Date normalization
date = normalize_date("2023-01-15", method="default")

# Time normalization
time = normalize_time("10:30:00", method="default")

# Number normalization
number = normalize_number("1,234.56", method="default")

# Quantity normalization
quantity = normalize_quantity("5 kg", method="default")

# Data cleaning
cleaned = clean_data(dataset, method="default", remove_duplicates=True)

# Duplicate detection
duplicates = detect_duplicates(dataset, method="default", threshold=0.8)

# Language detection
language = detect_language("Hello world", method="default")

# Encoding handling
encoding, confidence = handle_encoding(data, operation="detect", method="default")
```

## Using Registry

### Registering Custom Methods

```python
from semantica.normalize.registry import method_registry

# Custom text normalization method
def custom_text_normalization(text, **kwargs):
    """Custom normalization logic."""
    # Your custom normalization code
    return text.upper().strip()

# Register custom method
method_registry.register("text", "custom_upper", custom_text_normalization)

# Use custom method
from semantica.normalize.methods import get_normalize_method
custom_method = get_normalize_method("text", "custom_upper")
result = custom_method("hello world")
```

### Listing Registered Methods

```python
from semantica.normalize.registry import method_registry

# List all registered methods
all_methods = method_registry.list_all()
print("Registered methods:", all_methods)

# List methods for specific task
text_methods = method_registry.list_all("text")
print("Text methods:", text_methods)

entity_methods = method_registry.list_all("entity")
print("Entity methods:", entity_methods)
```

### Unregistering Methods

```python
from semantica.normalize.registry import method_registry

# Unregister a method
method_registry.unregister("text", "custom_upper")

# Clear all methods for a task
method_registry.clear("text")

# Clear all methods
method_registry.clear()
```

## Configuration

### Using Configuration Manager

```python
from semantica.normalize.config import normalize_config

# Get configuration values
unicode_form = normalize_config.get("unicode_form", default="NFC")
case = normalize_config.get("case", default="preserve")
date_format = normalize_config.get("date_format", default="ISO8601")
timezone = normalize_config.get("timezone", default="UTC")

# Set configuration values
normalize_config.set("unicode_form", "NFKC")
normalize_config.set("case", "lower")

# Method-specific configuration
normalize_config.set_method_config("text", unicode_form="NFC", case="lower")
text_config = normalize_config.get_method_config("text")

# Get all configuration
all_config = normalize_config.get_all()
print("All config:", all_config)
```

### Environment Variables

```bash
# Set environment variables
export NORMALIZE_UNICODE_FORM=NFC
export NORMALIZE_CASE=lower
export NORMALIZE_DATE_FORMAT=ISO8601
export NORMALIZE_TIMEZONE=UTC
export NORMALIZE_DEFAULT_LANGUAGE=en
export NORMALIZE_DEFAULT_ENCODING=utf-8
```

### Configuration File

```yaml
# config.yaml
normalize:
  unicode_form: NFC
  case: lower
  date_format: ISO8601
  timezone: UTC
  default_language: en
  default_encoding: utf-8

normalize_methods:
  text:
    unicode_form: NFC
    case: lower
  entity:
    resolve_aliases: true
  date:
    format: ISO8601
    timezone: UTC
```

```python
from semantica.normalize.config import NormalizeConfig

# Load from config file
config = NormalizeConfig(config_file="config.yaml")
unicode_form = config.get("unicode_form")
```

## Advanced Examples

### Complete Normalization Pipeline

```python
from semantica.normalize import (
    normalize_text,
    normalize_entity,
    normalize_date,
    normalize_number,
    clean_data
)

# Step 1: Normalize text
text = normalize_text("Hello   World", method="default", case="lower")

# Step 2: Normalize entities
entities = ["John Doe", "J. Doe", "Johnny Doe"]
normalized_entities = [
    normalize_entity(e, entity_type="Person", method="default")
    for e in entities
]

# Step 3: Normalize dates
dates = ["2023-01-15", "yesterday", "3 days ago"]
normalized_dates = [
    normalize_date(d, method="default") for d in dates
]

# Step 4: Normalize numbers
numbers = ["1,234.56", "50%", "1.5e3"]
normalized_numbers = [
    normalize_number(n, method="default") for n in numbers
]

# Step 5: Clean dataset
dataset = [
    {"id": 1, "name": "Alice", "date": "2023-01-15"},
    {"id": 2, "name": "Bob", "date": "yesterday"},
]
cleaned = clean_data(dataset, method="default", remove_duplicates=True)
```

### Custom Normalization Workflow

```python
from semantica.normalize import (
    TextNormalizer,
    EntityNormalizer,
    DateNormalizer,
    NumberNormalizer,
    DataCleaner
)

# Create normalizers with custom config
text_norm = TextNormalizer(unicode_form="NFKC", case="lower")
entity_norm = EntityNormalizer(alias_map={"j. doe": "John Doe"})
date_norm = DateNormalizer()
number_norm = NumberNormalizer()
cleaner = DataCleaner(similarity_threshold=0.85)

# Normalize text
text = text_norm.normalize_text("Hello   World")

# Normalize entities
entity = entity_norm.normalize_entity("J. Doe", entity_type="Person")

# Normalize dates
date = date_norm.normalize_date("2023-01-15", format="ISO8601")

# Normalize numbers
number = number_norm.normalize_number("1,234.56")

# Clean data
cleaned = cleaner.clean_data(dataset, remove_duplicates=True)
```

### Batch Processing

```python
from semantica.normalize import TextNormalizer, EntityNormalizer

text_norm = TextNormalizer()
entity_norm = EntityNormalizer()

# Batch text normalization
texts = ["Hello   World", "Test   Text", "Another   Example"]
normalized_texts = text_norm.process_batch(texts, case="lower")

# Batch entity normalization
entities = ["John Doe", "Jane Smith", "Bob Johnson"]
normalized_entities = [
    entity_norm.normalize_entity(e, entity_type="Person")
    for e in entities
]
```

### Integration with Other Modules

```python
from semantica.normalize import normalize_text, normalize_entity
from semantica.kg import build

# Normalize text before KG building
text = normalize_text("Apple Inc. was founded by Steve Jobs", method="default")

# Normalize entities before adding to KG
entities = [
    normalize_entity("Apple Inc.", entity_type="Organization", method="default"),
    normalize_entity("Steve Jobs", entity_type="Person", method="default")
]

# Build knowledge graph with normalized data
kg = build(sources=[{"entities": entities, "relationships": []}])
```

### Custom Validation Rules

```python
from semantica.normalize import DataCleaner, DataValidator

cleaner = DataCleaner()

# Custom validation schema
schema = {
    "fields": {
        "id": {"type": int, "required": True},
        "name": {"type": str, "required": True, "min_length": 2},
        "age": {"type": int, "required": False, "min": 0, "max": 150}
    }
}

dataset = [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "B", "age": 200},  # Invalid: name too short, age out of range
]

# Validate
validation = cleaner.validate_data(dataset, schema)
if not validation.valid:
    for error in validation.errors:
        print(f"Error: {error}")
```

### Language-Aware Normalization

```python
from semantica.normalize import (
    normalize_text,
    detect_language,
    LanguageDetector
)

detector = LanguageDetector()

# Detect language first
text = "Bonjour le monde"
language, confidence = detector.detect_with_confidence(text)

# Normalize based on language
if language == "fr":
    normalized = normalize_text(text, method="default", case="preserve")
else:
    normalized = normalize_text(text, method="default", case="lower")
```

### Encoding-Aware Text Processing

```python
from semantica.normalize import (
    handle_encoding,
    normalize_text,
    EncodingHandler
)

handler = EncodingHandler()

# Detect and convert encoding
data = b'\xff\xfeH\x00e\x00l\x00l\x00o\x00'  # UTF-16 LE with BOM
encoding, confidence = handler.detect(data)
utf8_text = handler.convert_to_utf8(data, source_encoding=encoding)

# Normalize text after encoding conversion
normalized = normalize_text(utf8_text, method="default")
```

### Comprehensive Data Cleaning Pipeline

```python
from semantica.normalize import (
    clean_data,
    detect_duplicates,
    normalize_text,
    normalize_date,
    DataCleaner
)

# Raw dataset
raw_dataset = [
    {"id": 1, "name": "  Alice  ", "date": "2023-01-15"},
    {"id": 2, "name": "Bob", "date": "yesterday"},
    {"id": 1, "name": "Alice", "date": "2023-01-15"},  # Duplicate
    {"id": 3, "name": None, "date": "2023-01-20"},  # Missing name
]

# Step 1: Normalize text fields
for record in raw_dataset:
    if record.get("name"):
        record["name"] = normalize_text(record["name"], method="default")

# Step 2: Normalize dates
for record in raw_dataset:
    if record.get("date"):
        record["date"] = normalize_date(record["date"], method="default")

# Step 3: Clean data
cleaner = DataCleaner()
cleaned = cleaner.clean_data(
    raw_dataset,
    remove_duplicates=True,
    handle_missing=True,
    missing_strategy="remove"
)

print(f"Cleaned {len(raw_dataset)} -> {len(cleaned)} records")
```

## Best Practices

1. **Unicode Normalization**: Always use NFC form for most use cases, NFKC for compatibility
2. **Case Handling**: Preserve case when possible, normalize only when necessary
3. **Entity Normalization**: Provide entity_type when available for better normalization
4. **Date Parsing**: Use ISO8601 format for consistency, handle timezones explicitly
5. **Number Parsing**: Be aware of locale-specific formatting (commas vs periods)
6. **Data Cleaning**: Validate data before cleaning, use appropriate strategies
7. **Language Detection**: Ensure minimum text length (10+ characters) for reliable detection
8. **Encoding Handling**: Always detect encoding before conversion, use fallback chain
9. **Batch Processing**: Use batch methods for large datasets to improve performance
10. **Configuration**: Use configuration files for consistent settings across environments
11. **Error Handling**: Always handle ValidationError and ProcessingError exceptions
12. **Method Registry**: Register custom methods for domain-specific normalization needs

