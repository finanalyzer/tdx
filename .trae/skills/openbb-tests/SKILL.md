---
name: openbb-tests
description: This skill automates the creation of test scripts and generates detailed test reports for assessing compatibility of data extensions with OpenBB standards. It provides a structured approach to evaluate how well data providers (like tdxquant, akshare, tushare) implement OpenBB's standard data models and field requirements.
---

# OpenBB Data Extension Compatibility Evaluation

## Overview

This skill automates the creation of test scripts and generates detailed test reports for assessing compatibility of data extensions with OpenBB standards. It provides a structured approach to evaluate how well data providers (like tdxquant, akshare, tushare) implement OpenBB's standard data models and field requirements.

## Input Parameters

### Required Parameters
- `providers`: List of data providers to test (e.g., ["tdxquant", "akshare", "tushare"])
- `test_symbols`: Dictionary of test symbols by market (e.g., {"cn": "000002.SZ,600036.SH", "hk": "0700.HK"})
- `reference_standard`: Reference [OpenBB](https://docs.openbb.co/odp/python/reference) standard for comparison
- `output_format`: Format for test reports (default: "markdown")

### Optional Parameters
- `include_yfinance`: Include yfinance as a reference provider (default: true)
- `test_edge_cases`: Test edge cases (single symbol, cache usage) (default: true)
- `response_time_threshold`: Maximum acceptable response time in seconds (default: 10.0)
- `output_directory`: Directory to save test reports (default: "./tests")

## Execution Logic

### 1. Test Script Generation

The skill generates comprehensive test scripts that:

- **Import necessary dependencies**: pytest, pandas, numpy, OpenBB SDK
- **Define reference fields**: Based on OpenBB standard documentation
- **Implement test functions**:
  - `test_equity_quote_standard_usage()`: Tests standard usage scenario
  - `test_equity_quote_edge_cases()`: Tests single symbol and cache usage
  - `validate_field_compatibility()`: Validates field compatibility with OpenBB standards
  - `generate_comprehensive_test_report()`: Generates detailed test reports
  - Provider-specific test functions for different markets

### 2. Test Execution

The generated test script:

- Fetches data from each provider for specified test symbols
- Validates data type compatibility for each field
- Checks field completeness (non-null vs null counts)
- Identifies missing OpenBB standard fields
- Identifies extra fields not in OpenBB standard
- Measures response times

### 3. Report Generation

The skill generates detailed reports that include:

- **Provider comparison summary**: Overview of field coverage across providers
- **Detailed provider analysis**: Field completeness, data type compatibility, missing fields, extra fields
- **Cross-provider field comparison**: Common fields and provider-specific fields
- **Price comparison**: For common symbols across providers
- **Comprehensive field comparison table**: Systematic comparison across all data sources (standard, yfinance, and tested providers)

After generating the report, the skill automatically adds a comprehensive comparison table at the end of the report that systematically compares data fields across the standard, yfinance, and the tested data providers. The table includes column headers for each data source and row entries for each relevant field being compared, with "N/A" indicators for unavailable fields.

## Output Formats

### 1. Test Script

A Python test script saved as `tests/test_equity_quote.py` with:

- Proper test structure following pytest conventions
- Comprehensive test functions for each provider
- Field validation logic
- Report generation capabilities

### 2. Test Report

A markdown report saved as `tests/equity_quote_comprehensive_test_report.md` with:

- Structured sections for easy navigation
- Tables for clear data presentation
- Visual indicators (✅/❌) for field availability
- Key findings and insights

## Integration with Existing Frameworks

### Alignment with OpenBB Testing Patterns

- **Mocking**: Uses `unittest.mock` to mock external dependencies like TdxQuant client
- **Test Structure**: Follows the three-method fetcher pattern (`transform_query`, `extract_data`, `transform_data`)
- **Error Handling**: Properly handles `EmptyDataError` and other exceptions
- **Caching**: Tests cache usage scenarios

### Compatibility with CI/CD Pipelines

- **Test Discovery**: Follows pytest naming conventions for automatic discovery
- **Report Generation**: Produces machine-readable reports for CI integration
- **Exit Codes**: Returns appropriate exit codes for CI pipeline integration

## Usage Examples

### Basic Usage

```python
from openbb_tdx.skills.openbb_tests import DataExtensionCompatibilityEvaluator

# Initialize evaluator
evaluator = DataExtensionCompatibilityEvaluator(
    providers=["tdxquant", "akshare", "tushare"],
    test_symbols={"cn": "000002.SZ,600036.SH", "hk": "0700.HK"}
)

# Generate test script
evaluator.generate_test_script()

# Run tests and generate report
evaluator.run_tests()
```

### Advanced Usage with Custom Parameters

```python
evaluator = DataExtensionCompatibilityEvaluator(
    providers=["tdxquant", "akshare"],
    test_symbols={"cn": "000001.SZ,600519.SH"},
    include_yfinance=True,
    response_time_threshold=5.0,
    output_directory="./test_reports"
)

evaluator.generate_test_script()
evaluator.run_tests()
```

## Example Prompts

### Equity Quote Test Script Generation

```
Create a comprehensive test script in the tests/ directory to validate the compatibility of the `obb.equity.price.quote` method using the data providers "tdxquant", "akshare", and "tushare". The test script should: 
1) Implement test cases for each provider that cover standard usage scenarios; 
2) Retrieve and compare the output data from each provider against the reference standards and yfinance implementation as defined in `https://docs.openbb.co/odp/python/reference/equity/price/quote` ; 
3) Include assertions for data accuracy, field completeness, and response time; 
4) Generate detailed test reports that highlight discrepancies between provider outputs and the reference standards; 
5) Ensure the test script is compatible with the existing test framework and can be executed as part of the automated testing pipeline.
```

This prompt demonstrates how to use the skill to generate a comprehensive test script for validating the equity quote functionality across multiple data providers, ensuring compatibility with OpenBB standards and generating detailed comparison reports.

## Key Features

- **Automated Test Generation**: Creates comprehensive test scripts tailored to specific providers
- **Field Compatibility Validation**: Ensures data fields match OpenBB standards
- **Data Type Validation**: Verifies data types align with expected formats
- **Performance Measurement**: Monitors response times for each provider
- **Comprehensive Reporting**: Generates detailed, well-structured reports
- **Cross-Provider Comparison**: Identifies strengths and weaknesses of each provider

## Best Practices

1. **Run tests in isolation**: Each provider test should run independently
2. **Use appropriate test symbols**: Include symbols from different markets
3. **Validate edge cases**: Test single symbols and cache usage
4. **Monitor response times**: Ensure providers meet performance expectations
5. **Review generated reports**: Use insights to improve provider implementations

## Troubleshooting

### Common Issues

- **TdxQuant initialization errors**: Ensure TongDaXin client is running and logged in
- **API rate limits**: Implement proper error handling for rate-limited providers
- **Field mapping issues**: Verify field aliases and mappings are correct
- **Data type mismatches**: Check numpy type handling in validation logic

### Debugging Tips

- Use `pytest -v` for verbose test output
- Check generated reports for detailed error information
- Verify provider-specific requirements (e.g., API keys, client installation)
- Test with different symbols to identify provider-specific limitations

## Conclusion

This skill provides a structured, automated approach to evaluate data extension compatibility with OpenBB standards. By generating comprehensive test scripts and detailed reports, it helps ensure that data providers meet the required quality standards and provide consistent, reliable data to OpenBB users.
