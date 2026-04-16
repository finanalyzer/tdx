# OpenBB Data Provider Reference Guide

## Overview

This reference guide provides detailed information about OpenBB data provider architecture, implementation patterns, and best practices. It serves as a comprehensive resource for developers building custom data providers for the OpenBB platform.

## Provider Architecture

### Core Components

OpenBB data providers consist of several core components that work together:

1. **Provider Class**: The main entry point that registers fetchers and metadata
2. **Fetcher Classes**: Handle data extraction, transformation, and loading
3. **Query Parameter Models**: Define input validation and constraints
4. **Data Models**: Define the output structure and validation
5. **Models**: Business logic and data processing components

### Folder Structure

```
openbb_provider_example/
├── __init__.py               # Provider definition
├── pyproject.toml            # Package configuration
├── models/
│   ├── __init__.py
│   └── historical.py         # Endpoint implementation
├── fetcher/
│   ├── __init__.py
│   └── historical.py         # Fetcher implementation
└── views/
    ├── __init__.py
    └── historical.py         # Visualization implementation
```

## Data Model Standards

### Standard Models

OpenBB uses standardized data models to ensure consistency across providers:

```python
from openbb_core.provider.abstract.data import Data
from pydantic import Field

class PriceData(Data):
    """Standard price data model."""
    date: str = Field(description="Date of the price data")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price during the period")
    low: float = Field(description="Lowest price during the period")
    close: float = Field(description="Closing price")
    volume: Optional[float] = Field(default=None, description="Trading volume")
```

### Query Parameter Models

All query parameters must inherit from QueryParams:

```python
from openbb_core.provider.abstract.query import QueryParams
from pydantic import Field
from typing import Optional

class PriceHistoricalQueryParams(QueryParams):
    """Query parameters for historical price data."""
    symbol: str = Field(description="Symbol to get data for")
    start_date: Optional[date] = Field(
        default=None, 
        description="Start date for the data"
    )
    end_date: Optional[date] = Field(
        default=None, 
        description="End date for the data"
    )
```

## Fetcher Implementation Patterns

### Basic Fetcher Structure

```python
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.utils.helpers import amake_requests
from typing import Any, Dict, List

class ExampleFetcher(Fetcher[QueryParams, Data]):
    """Example fetcher implementation."""
    
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> QueryParams:
        """Transform query parameters before sending to the API."""
        return QueryParams(**params)
    
    @staticmethod
    async def aextract(data: QueryParams, **kwargs) -> Dict:
        """Extract raw data from the external API."""
        # Implementation to fetch data from external API
        url = f"https://api.example.com/data/{data.symbol}"
        return await amake_requests(url)
    
    @staticmethod
    def transform_data(response: Dict, data: QueryParams, **kwargs) -> List[Data]:
        """Transform raw API response to standardized data format."""
        # Transform the response to match the Data model
        return [Data(**item) for item in response['results']]
```

### Error Handling Patterns

```python
from openbb_core.provider.abstract.error import OpenBBError

class RobustFetcher(Fetcher[QueryParams, Data]):
    @staticmethod
    async def aextract(data: QueryParams, **kwargs) -> Dict:
        try:
            # Attempt to fetch data
            url = f"https://api.example.com/data/{data.symbol}"
            response = await amake_requests(url)
            
            # Validate response
            if not response or 'error' in response:
                raise OpenBBError(f"API returned error: {response.get('error')}")
                
            return response
            
        except Exception as e:
            # Log the error and raise OpenBBError
            logger.error(f"Error fetching data for {data.symbol}: {str(e)}")
            raise OpenBBError(f"Failed to fetch data from provider: {str(e)}")
```

## Configuration and Authentication

### API Key Management

Store API keys securely using OpenBB's configuration system:

```python
from openbb_core.config import Configuration

def get_api_key() -> str:
    """Retrieve API key from OpenBB configuration."""
    config = Configuration()
    api_key = config.api_keys.get("EXAMPLE_API_KEY")
    if not api_key:
        raise ValueError("Example API key not found in configuration")
    return api_key
```

### Environment Variables

Use environment variables for sensitive information:

```python
import os
from openbb_core.config import Configuration

def get_base_url() -> str:
    """Get base URL from configuration or environment."""
    config = Configuration()
    base_url = config.provider_settings.get("example", {}).get("base_url")
    if not base_url:
        base_url = os.getenv("EXAMPLE_BASE_URL", "https://api.example.com")
    return base_url
```

## Testing Guidelines

### Unit Testing Structure

```python
import pytest
from unittest.mock import AsyncMock, patch
from openbb_provider_example.fetcher.historical import ExampleFetcher
from openbb_provider_example.models.historical import (
    PriceHistoricalQueryParams,
    PriceHistoricalData,
)

@pytest.mark.asyncio
async def test_fetcher_success():
    """Test successful fetcher execution."""
    # Mock parameters
    params = PriceHistoricalQueryParams(symbol="AAPL")
    
    # Mock API response
    mock_response = {
        "results": [
            {"date": "2023-01-01", "close": 150.0, "volume": 1000000}
        ]
    }
    
    # Create fetcher instance
    fetcher = ExampleFetcher()
    
    # Mock the extraction method
    with patch.object(fetcher, 'aextract', new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = mock_response
        
        # Execute fetch
        result = await fetcher.fetch(params)
        
        # Assertions
        assert len(result) == 1
        assert result[0].date == "2023-01-01"
        assert result[0].close == 150.0
```

### Integration Testing

```python
import asyncio
from openbb import obb

async def test_integration():
    """Test provider integration with OpenBB platform."""
    try:
        # Test with a known symbol
        result = await obb.stock.price.historical(
            symbol="AAPL", 
            provider="example"
        )
        
        # Verify result structure
        assert hasattr(result, 'to_df')
        df = result.to_df()
        assert not df.empty
        assert 'close' in df.columns
        
    except Exception as e:
        pytest.fail(f"Integration test failed: {str(e)}")
```

## Performance Optimization

### Caching Strategies

Implement intelligent caching to improve performance:

```python
import asyncio
from functools import wraps
from typing import Callable, Any

def cached_result(ttl: int = 300):  # 5 minutes default TTL
    """Decorator to cache fetcher results."""
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from arguments
            cache_key = str(args) + str(sorted(kwargs.items()))
            current_time = asyncio.get_event_loop().time()
            
            # Check if result is in cache and not expired
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl:
                    return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            return result
            
        return wrapper
    return decorator
```

### Rate Limiting

Handle API rate limits gracefully:

```python
import time
import asyncio
from typing import Dict, Any

class RateLimitedFetcher(Fetcher[QueryParams, Data]):
    def __init__(self):
        self.last_request_time = 0
        self.min_interval = 0.1  # 100ms between requests
    
    async def aextract(self, data: QueryParams, **kwargs) -> Dict[Any, Any]:
        # Enforce minimum interval between requests
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            await asyncio.sleep(self.min_interval - time_since_last)
        
        # Make the actual request
        url = f"https://api.example.com/data/{data.symbol}"
        result = await amake_requests(url)
        
        # Update last request time
        self.last_request_time = time.time()
        
        return result
```

## Security Considerations

### Input Sanitization

Always validate and sanitize inputs:

```python
from pydantic import field_validator
import re

class SecureQueryParams(QueryParams):
    symbol: str = Field(description="Stock symbol")
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        # Only allow alphanumeric characters and certain symbols
        if not re.match(r'^[A-Z]{1,10}$', v.upper()):
            raise ValueError('Invalid symbol format')
        return v.upper()
```

### API Security

Secure API interactions:

```python
import aiohttp
from typing import Dict, Any

async def secure_api_call(url: str, headers: Dict[str, str], timeout: int = 30) -> Dict[Any, Any]:
    """Make secure API calls with proper timeout and error handling."""
    timeout_config = aiohttp.ClientTimeout(total=timeout)
    
    async with aiohttp.ClientSession(timeout=timeout_config) as session:
        try:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()  # Raises exception for bad status codes
                return await response.json()
        except aiohttp.ClientResponseError as e:
            raise OpenBBError(f"API request failed with status {e.status}: {e.message}")
        except asyncio.TimeoutError:
            raise OpenBBError(f"API request timed out after {timeout} seconds")
        except Exception as e:
            raise OpenBBError(f"Unexpected error during API request: {str(e)}")
```

## Common Patterns and Anti-Patterns

### Recommended Patterns

1. **Asynchronous Operations**: Always use async/await for I/O operations
2. **Input Validation**: Validate all inputs using Pydantic models
3. **Error Handling**: Catch and wrap exceptions appropriately
4. **Resource Cleanup**: Properly manage connections and resources
5. **Logging**: Implement appropriate logging for debugging

### Anti-Patterns to Avoid

1. **Synchronous Network Calls**: Blocking I/O operations in async contexts
2. **Hardcoded Values**: Embedding API keys or URLs directly in code
3. **Insufficient Error Handling**: Not handling API failures gracefully
4. **Poor Resource Management**: Not closing connections or files properly
5. **Inadequate Input Validation**: Not validating user inputs thoroughly

## Troubleshooting Common Issues

### Provider Registration Issues

If your provider isn't recognized:

1. Verify the `pyproject.toml` configuration is correct
2. Ensure the provider is properly installed in editable mode
3. Run `openbb-build` after making changes to the provider
4. Check that the provider name matches across all files

### Data Model Mismatch

If data doesn't match expected format:

1. Verify your Data model inherits from the correct base class
2. Check that field names match OpenBB's expected format
3. Ensure data types are consistent between your model and the API
4. Validate that your transformer correctly maps API fields to model fields

### Performance Problems

If your provider is slow:

1. Implement appropriate caching strategies
2. Optimize API calls (batch requests when possible)
3. Use connection pooling for multiple requests
4. Consider rate limiting to avoid API throttling
