#!/usr/bin/env python3
"""
OpenBB Data Provider Helper Scripts

This collection of scripts provides utilities for common OpenBB data provider tasks:
- Creating new provider scaffolding
- Validating provider implementations
- Testing provider functionality
- Generating boilerplate code
"""

import argparse
import os
import sys
from pathlib import Path
import subprocess
from typing import Dict, List, Optional


def create_provider_scaffold(provider_name: str, output_dir: str = "./"):
    """
    Create a basic scaffold for a new OpenBB data provider.
    
    Args:
        provider_name: Name of the provider (e.g., "my_provider")
        output_dir: Output directory for the scaffold
    """
    print(f"Creating scaffold for provider: {provider_name}")
    
    # Create provider directory structure
    provider_path = Path(output_dir) / f"openbb_{provider_name}"
    provider_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (provider_path / "models").mkdir(exist_ok=True)
    (provider_path / "fetcher").mkdir(exist_ok=True)
    (provider_path / "views").mkdir(exist_ok=True)
    
    # Create __init__.py files
    for dir_path in [provider_path, provider_path / "models", provider_path / "fetcher", provider_path / "views"]:
        (dir_path / "__init__.py").touch()
    
    # Create basic provider file
    provider_content = f'''from openbb_core.provider.abstract.provider import Provider

provider = Provider(
    name="{provider_name}",
    fetcher_dict={{}},
    repr_count=3,
    full_name="OpenBB {provider_name.title()} Provider"
)
'''
    (provider_path / "__init__.py").write_text(provider_content)
    
    # Create pyproject.toml
    toml_content = f'''[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "openbb-{provider_name}"
version = "0.1.0"
description = "OpenBB provider for {provider_name}"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"
openbb-core = "^1.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-asyncio = "^0.18.0"

[tool.poetry.plugins."openbb-extension"]
"{provider_name}" = "openbb_{provider_name}.provider:provider"
'''
    (provider_path / "pyproject.toml").write_text(toml_content)
    
    # Create README
    readme_content = f"""# OpenBB {provider_name.title()} Provider

This provider integrates {provider_name.title()} data into the OpenBB platform.

## Installation

```bash
pip install openbb-{provider_name}
```

## Usage

```python
from openbb import obb

# Example usage
data = await obb.some.endpoint(symbol="AAPL", provider="{provider_name}")
print(data)
```

## Development

To develop this provider:

1. Install in editable mode:
   ```bash
   pip install -e .
   ```

2. Build the extension:
   ```bash
   openbb-build
   ```

3. Test the provider:
   ```python
   from openbb import obb
   print(obb.registered_providers)
   ```
"""
    (provider_path / "README.md").write_text(readme_content)
    
    print(f"Scaffold created at: {provider_path}")


def validate_provider(provider_path: str):
    """
    Validate an OpenBB provider implementation.
    
    Args:
        provider_path: Path to the provider directory
    """
    path = Path(provider_path)
    
    print(f"Validating provider at: {path.absolute()}")
    
    # Check required files
    required_files = [
        "__init__.py",
        "pyproject.toml",
        "models/__init__.py",
        "fetcher/__init__.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (path / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
    else:
        print("✅ All required files present")
    
    # Check pyproject.toml for proper plugin registration
    toml_path = path / "pyproject.toml"
    if toml_path.exists():
        toml_content = toml_path.read_text()
        if 'plugins."openbb-extension"' in toml_content:
            print("✅ Plugin registration found in pyproject.toml")
        else:
            print("❌ Plugin registration not found in pyproject.toml")
    
    # Check provider definition
    init_path = path / "__init__.py"
    if init_path.exists():
        init_content = init_path.read_text()
        if "Provider(" in init_content:
            print("✅ Provider class definition found")
        else:
            print("❌ Provider class definition not found")


def generate_model_boilerplate(model_name: str, fields: List[str], output_file: str):
    """
    Generate boilerplate code for an OpenBB data model.
    
    Args:
        model_name: Name of the model
        fields: List of field definitions in format "name:type:description"
        output_file: Output file path
    """
    print(f"Generating model boilerplate: {model_name}")
    
    # Parse fields
    field_defs = []
    imports_needed = set(['Field'])
    
    for field_def in fields:
        parts = field_def.split(':', 2)
        if len(parts) != 3:
            print(f"⚠️ Invalid field format: {field_def}. Expected: name:type:description")
            continue
            
        name, field_type, description = parts
        
        # Add import if needed
        if field_type.lower() in ['optional']:
            imports_needed.add('Optional')
        
        field_defs.append({
            'name': name.strip(),
            'type': field_type.strip(),
            'description': description.strip()
        })
    
    # Generate imports
    imports = ["from openbb_core.provider.abstract.data import Data"]
    if imports_needed:
        imports.append(f"from pydantic import {', '.join(sorted(imports_needed))}")
    
    # Generate class
    class_lines = [
        "",
        f"class {model_name}(Data):",
        f'    """{model_name} data model."""'
    ]
    
    for field in field_defs:
        class_lines.append(f'    {field["name"]}: {field["type"]} = Field(description="{field["description"]}")')
    
    # Combine everything
    content = "\n".join(imports + class_lines) + "\n"
    
    # Write to file
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    Path(output_file).write_text(content)
    
    print(f"Model boilerplate written to: {output_file}")


def test_provider_connection(provider_name: str, test_endpoint: str = None):
    """
    Test connection to a provider.
    
    Args:
        provider_name: Name of the provider to test
        test_endpoint: Specific endpoint to test (optional)
    """
    print(f"Testing provider: {provider_name}")
    
    try:
        # Import OpenBB
        import openbb
        
        # Check if provider is registered
        registered_providers = openbb.obb.registered_providers
        if provider_name in registered_providers:
            print(f"✅ Provider '{provider_name}' is registered")
            
            # Show provider details
            provider_info = registered_providers[provider_name]
            print(f"   Provider details: {provider_info}")
        else:
            print(f"❌ Provider '{provider_name}' is not registered")
            print("   Available providers:", list(registered_providers.keys()))
            return
        
        # If a test endpoint is provided, try to access it
        if test_endpoint:
            print(f"\nTesting endpoint: {test_endpoint}")
            try:
                # This is a simplified test - actual implementation would depend on the endpoint
                print(f"   Endpoint '{test_endpoint}' exists in provider")
            except Exception as e:
                print(f"   ❌ Error accessing endpoint: {str(e)}")
    
    except ImportError:
        print("❌ OpenBB not found. Please install it first.")
    except Exception as e:
        print(f"❌ Error testing provider: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="OpenBB Data Provider Helper Scripts")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Scaffold command
    scaffold_parser = subparsers.add_parser("scaffold", help="Create a new provider scaffold")
    scaffold_parser.add_argument("provider_name", help="Name of the provider")
    scaffold_parser.add_argument("--output-dir", default="./", help="Output directory for scaffold")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a provider implementation")
    validate_parser.add_argument("provider_path", help="Path to the provider directory")
    
    # Model generator command
    model_parser = subparsers.add_parser("generate-model", help="Generate model boilerplate")
    model_parser.add_argument("model_name", help="Name of the model to generate")
    model_parser.add_argument("--fields", nargs="+", required=True, 
                             help="Fields in format: name:type:description")
    model_parser.add_argument("--output", default="model.py", help="Output file path")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test a provider connection")
    test_parser.add_argument("provider_name", help="Name of the provider to test")
    test_parser.add_argument("--endpoint", help="Specific endpoint to test")
    
    args = parser.parse_args()
    
    if args.command == "scaffold":
        create_provider_scaffold(args.provider_name, args.output_dir)
    elif args.command == "validate":
        validate_provider(args.provider_path)
    elif args.command == "generate-model":
        generate_model_boilerplate(args.model_name, args.fields, args.output)
    elif args.command == "test":
        test_provider_connection(args.provider_name, args.endpoint)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

def main():
    print("This is an example script for openbb-data-provider")
    # TODO: Add actual script logic here
    # This could be data processing, file conversion, API calls, etc.

if __name__ == "__main__":
    main()
