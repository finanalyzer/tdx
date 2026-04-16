# OpenBB TdxQuant Extension

This extension integrates financial data from the 通达信量化平台 (TdxQuant) into the OpenBB Platform.

## Features

- Historical price data for Chinese stocks
- Support for Shanghai and Shenzhen exchanges
- Seamless integration with OpenBB Platform

## Installation

### Prerequisites

- Python 3.9.21 or later
- OpenBB Platform
- pytdx library (cross-platform)

### Install the Extension

```bash
# From the extension directory
pip install -e .
```

### Install Dependencies

The extension will automatically install the required dependencies, including:
- pytdx: Python interface to TDX protocol
- pandas: For data manipulation

### Note

This implementation uses the pytdx library, which is a pure Python implementation of the TDX protocol. It does not require the official TdxQuant SDK and works on all platforms (Windows, macOS, Linux).

If you prefer to use the official TdxQuant SDK, you can modify the implementation to use it instead of pytdx.

## Usage

### Using the Extension

```python
from openbb import obb

# Get historical price data
price_data = obb.equity.price.historical(
    symbol="600000",
    provider="openbb_tdx",
    exchange="sh",  # Shanghai Stock Exchange
    interval="1d"  # Daily data
)

print(price_data)

# Get 5-minute data
price_data_5m = obb.equity.price.historical(
    symbol="000001",
    provider="openbb_tdx",
    exchange="sz",  # Shenzhen Stock Exchange
    interval="5m"  # 5-minute data
)

print(price_data_5m)
```

### Available Commands

- `obb.equity.price.historical` - Get historical price data

## Configuration

The extension does not require any additional configuration. However, you may need to set up the TdxQuant SDK according to your needs.

## Development

### Building the Extension

```bash
# From the extension directory
python -m openbb_tdx.openbb build
```

### Running Tests

```bash
# From the extension directory
pytest
```

## Notes

- This extension is only compatible with Windows systems, as TdxQuant SDK only supports Windows.
- The current implementation is a placeholder. In a real-world scenario, you would need to:
  1. Install and import the TdxQuant SDK
  2. Initialize the TdxQuant client
  3. Implement proper data fetching logic
  4. Handle authentication and error cases

## License

MIT
