# openbb_akshare

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-AGPL--3.0-green.svg)](LICENSE)

## How to Use AKShare as a Data Source for OpenBB

**OpenBB**, as an open-source financial data platform, is dedicated to providing free and transparent financial data interfaces for investors, analysts, and developers. For a detailed introduction to OpenBB and its usage, please refer to [Introduction to OpenBB and How to Use It to Aid Financial Data Analysis of China A-share and Hong Kong Stocks](https://medium.com/@shugaoye/introduction-to-openbb-and-how-to-use-it-to-aid-financial-data-analysis-of-china-a-share-and-hong-f4bbe480399a).

Although OpenBB supports multi-source data interfaces, the acquisition of financial data in China (including Hong Kong) mainly relies on Yahoo Finance. As a free basic data source, it can meet basic needs, but its coverage depth for the Chinese and Hong Kong markets is still insufficient. More importantly, mainland Chinese users need to use a VPN to access this service, creating significant usage barriers.

To enhance service capabilities in Greater China, OpenBB urgently needs to improve the implementation of localized financial data sources. The mainstream paid solutions include Wind, Eastmoney Choice, and 同花顺 iFind (mainly for institutional clients), while the free solutions focus on the open-source tool AKShare as the core solution. By integrating data interfaces from platforms such as Eastmoney, 同花顺, Tencent, Sina, and 雪球, AKShare has become one of the most comprehensive, up-to-date, and developer-friendly financial data aggregation libraries in the domestic Python ecosystem.

The `openbb_akshare` project, as a data source extension for OpenBB, enables seamless integration of AKShare data into the OpenBB platform. Below is a detailed usage guide:

## Table of Contents

- [Environment Setup and Installation](#-environment-setup-and-installation-process)
- [Using the AKShare Data Source](#-using-the-akshare-data-source)
  - [Query A-Share Company News](#case-1-query-a-share-company-news-vanke-as-an-example)
  - [Obtain Historical Stock Prices](#case-2-obtain-historical-stock-prices-of-hong-kong-stocks-hong-kong-telecom-as-an-example)
- [Project Ecosystem](#-openbb_akshare-project-ecosystem)
- [Run as Web Service](#-run-openbb-akshare-as-a-web-service)
- [Requirements](#requirements)
- [Troubleshooting](#troubleshooting)

## 💻 Environment Setup and Installation Process

As developers, we primarily interact with the platform through the OpenBB Platform CLI. To integrate the AKShare data source, follow these steps to configure the development environment:

1. **Create a Python Virtual Environment**

   You can use `venv`, `uv`, or `poetry` to create a virtual environment. Here, we use venv (built into Python):

   ```bash
   # Create a virtual environment
   python3 -m venv .venv

   # Activate the virtual environment (Linux/Mac)
   source .venv/bin/activate

   # For Windows
   .venv\Scripts\activate  
   ```

2. **Install OpenBB Platform CLI**

   Install the core OpenBB CLI via pip. Users in mainland China can configure a mirror for faster installation:

   ```bash
   # (Optional) Set a domestic mirror for pip
   # For Linux/Mac
   export PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple

   # Install OpenBB CLI
   pip install openbb-cli
   ```

3. **Install openbb_akshare**

   Next, install the `openbb_akshare` extenstion to use the AKShare data source:

   ```bash
   # Install the AKShare data source extension
      pip install openbb_akshare
   
      # Rebuild OpenBB resources to activate the plugin
      python -c "import openbb; openbb.build()"   ```

## 🚀 Using the AKShare Data Source

### Case 1: Query A-Share Company News (Vanke as an Example)

**Jupyter Notebook**：

```Python
from openbb import obb
messages = obb.news.company("000002", provider="akshare")
for result in messages.results:
    print(f"{result.title}")
```

Output：

```plaintext
开源证券发布万科A研报，公司信息更新报告：销售均价有所提升，股东持续借款提供支持
万科A出售2086万股库存股，金额1.36亿元
万科A：已完成所有A股库存股出售 所得资金4.79亿元
...
```

**Using OpenBB CLI**：

```bash
openbb
2025 Jun 26, 03:11 (🦋) /news/ $ company --symbol 000002 --provider akshare
```

After entering the command, the results will be displayed in a WebView, as shown below：

![openbb04](docs/images/openbb04.png)

### Case 2: Obtain Historical Stock Prices of Hong Kong Stocks (Hong Kong Telecom as an Example)

**Using OpenBB CLI**:

```
2025 Jun 26, 03:28 (🦋) /equity/price/ $ historical --symbol 06823 --provider akshare
```

Results in WebView：![openbb05](docs/images/openbb05.png)

**Jupyter Notebook**：

```Python
from openbb import obb
prices = obb.equity.price.historical(symbol='06823', start_date="2025-06-01", end_date="2025-06-10", provider="akshare")
prices.results[0].date, prices.results[0].open, prices.results[0].close, prices.results[0].high, prices.results[0].low, prices.results[0].volume
```

Output：

```
(datetime.date(2025, 6, 2), 11.28, 11.3, 11.3, 11.14, 10308375)
```

## 🌟 openbb_akshare Project Ecosystem

The `openbb_akshare` project is currently in an active development phase, and contributions from the open-source community are welcome:

### Code Repositories

- **GitHub**: https://github.com/finanalyzer/openbb_akshare

- **GitCode (Domestic Mirror)**: https://gitcode.com/finanalyzer/openbb_akshare

### Ways to Contribute

1. Submit Issues to report data needs or bugs.

2. Contribute PRs to optimize data source interfaces.

3. Improve documentation to help more users.

Through the integration of AKShare and OpenBB, users in China can more conveniently access real-time and historical data for markets such as A-Shares and Hong Kong Stocks, providing strong data support for quantitative analysis and investment research.

## Run openbb-akshare as a web service

You can also run openbb-akshare as a FastAPI web service:

```bash
uvicorn openbb_platform_api.main:app --port 8001
```

To start the instance in VSCode, update your `launch.json` configuration as below:

```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "OpenBB Debugger: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "openbb_platform_api.main:app",
                "--port",
                "8001"
            ],
            "jinja": true
        },
        {
            "name": "Python Debugger: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ]
}
```

## Requirements

- Python 3.11 or higher
- OpenBB Platform 4.6.0 or higher
- AKShare 1.18.19 or higher

## Troubleshooting

If you encounter issues during installation or usage:

1. **Build issues**: Make sure to run `python -c "import openbb; openbb.build()"` after installing the extension
2. **Data not loading**: Verify your internet connection and that AKShare APIs are accessible
3. **Import errors**: Ensure all dependencies are installed correctly in your virtual environment
4. **For more help**: Visit the [project issues page](https://github.com/finanalyzer/openbb_akshare/issues)