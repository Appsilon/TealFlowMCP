# Test Fixtures

This directory contains test data files used by the dataset reader tests.

## RDS Files (R Data Format)

- **ADSL.Rds** - Sample Subject-Level Analysis Dataset (copied from knowledge_base)
- **ADTTE.Rds** - Sample Time-to-Event Analysis Dataset (copied from knowledge_base)
- **invalid.rds** - Invalid RDS file (plain text) for error testing

## CSV Files

- **test_basic.csv** - Basic CSV with 3 columns, 3 rows
- **test_with_samples.csv** - CSV with 4 columns, 7 rows (for sample value testing)
- **test_missing.csv** - CSV with missing values (empty cells)
- **test_many_rows.csv** - CSV with 10 rows (for testing sample value limits)
- **test_types.csv** - CSV with different data types (numeric, string, float)
- **empty.csv** - Empty file (for error testing)

## Usage

These fixtures are referenced in `test_dataset_readers.py` using:

```python
FIXTURES_DIR = Path(__file__).parent / "fixtures"
csv_file = FIXTURES_DIR / "test_basic.csv"
```

All tests check if fixtures exist and skip gracefully if not found.
