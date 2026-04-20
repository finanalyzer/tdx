# openbb_tdx: A New Bridge Connecting TongDaXin and OpenBB for A-Share and Hong Kong Quantitative Data


---

## Introduction

In the field of financial quantitative analysis, data acquisition has always been a core component. As the world's leading open-source financial data platform, OpenBB provides a unified data access layer for global investors, but its native support for China's A-share market has been limited. Previously, the FinAnalyzer team successfully developed two extension plugins: openbb_akshare and openbb_tushare, connecting to two major domestic open-source financial databases.

Now, with TongDaXin officially launching the TdxQuant Python quantitative interface, a new data channel has opened. The openbb_tdx project has emerged - it deeply integrates TongDaXin's nearly 30 years of financial data accumulation with OpenBB's open architecture, bringing unprecedented data access experience to Chinese quantitative investors.

This article will comprehensively introduce the openbb_tdx project from multiple dimensions including project background, development motivation, core capabilities, and comparative analysis, helping readers deeply understand this new data bridge connecting TongDaXin and OpenBB.

---

## 1. Project Background

### 1.1 OpenBB: The Rise of Global Open-Source Financial Data Platform

OpenBB (OpenBB Platform) is an open-source financial data platform for global users, hosted on GitHub with over 61,000 stars, making it one of the most popular open-source financial data projects. By building a unified data access layer, it cleverly integrates proprietary data sources, authorized data sources, and public data sources to form standardized APIs.

OpenBB provides two core products:

- **Open Source Product Open Data Platform (ODP)**: As the backend engine, providing Python packages, command-line tools, and REST API services.
- **Enterprise Product OpenBB Workspace**: As the frontend interface, supporting teams to build customized AI-driven analysis applications.

The core value of ODP lies in its powerful scalability - users can freely install or uninstall data extension plugins, and all data is returned in Pandas DataFrame or JSON format, seamlessly compatible with Jupyter, Airflow, and various quantitative strategies.

### 1.2 Data Dilemma in the Chinese Market

Although OpenBB supports multi-source data interfaces, its access to Chinese market financial data mainly relies on Yahoo Finance. As a free basic data source, it can meet basic needs but has obvious deficiencies in coverage depth:

- Incomplete A-share market data coverage, lacking detailed financial indicators and sector data;
- Domestic users need VPN to access Yahoo Finance, creating high usage barriers;
- Real-time market data has significant delays, unable to meet intraday trading needs.

Domestic mainstream paid solutions (such as Wind, Choice, iFinD) mainly target institutional clients, making it difficult for individual investors and small/medium teams to afford high subscription costs. Among free solutions, while AKShare and Tushare are powerful, they still have room for improvement in real-time market data, data accuracy, and interface stability.

### 1.3 TongDaXin TdxQuant: A New Data Channel

At the end of 2025, TongDaXin (Shenzhen Wealth Trend Technology Co., Ltd.) officially launched TdxQuant - a Python quantitative strategy running framework built on the TongDaXin financial terminal. Relying on TongDaXin's nearly 30 years of financial technology accumulation, TdxQuant integrates complete real-time and historical market data, financial databases, and stable trading system infrastructure.

Core features of TdxQuant include:

- **High-Quality Data**: All historical and real-time data is provided using TongDaXin client data;
- **Real-Time Market Data**: Supports subscription and acquisition of real-time snapshots, K-lines, and tick data;
- **Comprehensive Coverage**: Includes A-shares, Hong Kong stocks, ETFs, convertible bonds, funds, and other securities;
- **Local Operation**: Strategies are developed and run in local IDE environments, ensuring code security and privacy.

The emergence of TdxQuant provides a new, high-quality data channel for OpenBB to access Chinese market data. The openbb_tdx project was born based on this background.

---

## 2. Development Motivation Analysis

### 2.1 Filling the Gap in OpenBB's Chinese Market Data Ecosystem

FinAnalyzer is committed to introducing OpenBB into Greater China's securities data analysis scenarios. Previously, two extension plugins were successfully developed: openbb_akshare (connecting to AKShare data source) and openbb_tushare (connecting to Tushare data source). However, these two solutions have certain limitations in real-time market data acquisition:

- AKShare relies on web crawlers to obtain data, which may trigger anti-crawling strategies during high-frequency calls, limiting interface stability;
- Tushare's real-time data requires advanced permissions (points), with limited free version functionality and call frequency restrictions.

As an official quantitative interface, TongDaXin TdxQuant provides professionally cleaned and standardized high-quality data, completely free for individual users. Integrating this data source into the OpenBB ecosystem can effectively compensate for the shortcomings of existing solutions, providing users with more stable, real-time, and accurate data services.

### 2.2 Key Problems Solved

The development of openbb_tdx aims to solve the following core problems:

**(1) Real-Time Market Data Acquisition**

As one of the most widely used securities market software in China, TongDaXin has real-time market servers covering the entire market. Through the TdxQuant interface, users can directly obtain real-time market data with very low latency, which is crucial for intraday trading strategies and real-time monitoring scenarios.

**(2) Data Quality and Consistency Issues**

Data provided by TdxQuant is uniformly cleaned and aligned by the server, with precise adjustment factors and high standardization in data formats. This avoids data inconsistency issues between different data sources and improves the reliability of quantitative strategy backtesting.

**(3) Usage Barriers and Cost Issues**

Compared to commercial data sources like Wind and Choice that cost tens or hundreds of thousands of yuan annually, TdxQuant is completely free. Meanwhile, accessing TongDaXin data through OpenBB's unified interface eliminates the need for users to learn TdxQuant's native API, lowering technical barriers.

### 2.3 Target User Groups

Target users of openbb_tdx mainly include:

- **Individual Quantitative Investors**: Need high-quality, low-cost A-share market data for strategy development and backtesting verification;
- **Fintech Developers**: Hope to integrate TongDaXin data in the OpenBB ecosystem to build customized analysis tools;
- **University Teachers and Students**: Use TongDaXin's free data interface for financial data analysis and quantitative trading teaching and research;
- **Small and Medium Quantitative Teams**: Need stable and reliable data infrastructure but cannot afford high costs of commercial data sources.

---

## 3. Core Capabilities

### 3.1 Data Access Capabilities

openbb_tdx achieves deep integration with TongDaXin data sources through OpenBB's Provider Framework. After installing the extension, users can access all TongDaXin data services through OpenBB's unified Python interface.

#### 3.1.1 Market Data

openbb_tdx supports obtaining the following market data types:

- **Historical K-Line Data**: Supports daily, weekly, monthly, minute lines, and other time dimensions;
- **Real-Time Market Snapshots**: Supports obtaining real-time prices, trading volumes, bid/ask data for all market stocks;
- **Tick Data**: Transaction records tick by tick, suitable for high-frequency strategies and microstructure analysis;
- **Adjusted Data**: Provides forward adjustment, backward adjustment, and other adjustment methods, as well as precise adjustment factors.

#### 3.1.2 Fundamental Data

- **Ex-Rights and Ex-Dividend Information**: Dividend, rights offering, stock dividend, and other corporate action data;
- **Financial Statement Data**: Basic financial indicators and professional financial data;
- **Stock Trading Data**: Limit up/down, turnover rate, P/E ratio, and other market indicators;
- **Sector Trading Data**: Rise/fall statistics for industry sectors and concept sectors.

#### 3.1.3 Classification and Instrument Information

- **Market Type Classification**: Main board, ChiNext, STAR Market, Beijing Stock Exchange, etc.;
- **Industry Classification**: Shenwan industry, TongDaXin industry, and other classification standards;
- **Custom Sectors**: Supports user-defined stock combinations and sector management;
- **Instrument Basic Information**: Stock codes, names, listing dates, industries, etc.

### 3.2 Technical Features

openbb_tdx has the following significant technical features in its architecture:

**(1) Standardized Interface Design**

Following the standard specifications of OpenBB Provider Framework, all data interfaces are presented in unified parameter formats and return formats. Users only need to switch the provider parameter to seamlessly switch between different data sources without modifying business logic code.

**(2) High-Performance Data Transmission**

TdxQuant adopts a local client-server architecture, with data transmitted through local inter-process communication, avoiding network delays. The performance advantage is particularly obvious for historical data batch acquisition scenarios.

**(3) Flexible Deployment Methods**

Supports accessing data through various methods including OpenBB CLI, Python API, REST API, and OpenBB Workspace, meeting different usage scenario needs.

### 3.3 Typical Usage Methods

> **Python API Call Example:**

```python
from openbb import obb

# Get historical stock price of Sinopec (600028)
df = obb.equity.price.historical(
    symbol="600028",
    start_date="2024-01-01",
    end_date="2025-12-31",
    provider="tdxquant"
).to_dataframe()

print(df.tail())
```

> **OpenBB CLI Call Example:**

```bash
# Start OpenBB command line environment
openbb

# Query historical K-line data
/equity/price/ $ historical --symbol 600028 \
    --start_date 2024-01-01 --end_date 2025-12-31 \
    --provider tdxquant
```

> **REST API Access:**

```bash
# Start local API service
openbb-api

# Get data through HTTP request
# GET http://127.0.0.1:6900/api/v1/equity/price/historical
#     ?symbol=600028&provider=tdx&start_date=2024-01-01
```

### 3.4 Application Scenarios

openbb_tdx can be widely applied to the following quantitative analysis scenarios:

- **Strategy Development and Backtesting**: Use TongDaXin's high-quality historical data to quickly verify the effectiveness of trading strategies;
- **Multi-Factor Analysis**: Combine fundamental data and market data for multi-factor stock selection model research;
- **AI Agent Integration**: Through OpenBB Workspace's MCP server, connect TongDaXin data with AI models to achieve natural language-driven intelligent analysis.

---

## 4. Systematic Comparative Analysis of Three Extension Plugins

As of now, FinAnalyzer has developed three OpenBB data extension plugins for the Chinese market: openbb_akshare, openbb_tushare, and openbb_tdx. Below is a systematic comparison from multiple dimensions.

### 4.1 Data Source Characteristics Comparison

| Comparison Dimension | openbb_akshare | openbb_tushare | openbb_tdx |
| ---------- | ----------------------------- | ----------------------- | ---------------------- |
| **Underlying Data Source** | AKShare (aggregating East Money, Tonghuashun, Tencent, Sina, Xueqiu, etc.) | Tushare Pro (professional financial data interface) | TongDaXin TdxQuant (official quantitative interface) |
| **Data Acquisition Method** | Web crawlers, scraping from multiple public websites | API calls, through Tushare server | Local client, connecting to TongDaXin terminal |
| **Data Coverage Range** | Extremely broad (A-shares, Hong Kong stocks, funds, futures, macro, sentiment, overseas markets, etc.) | Relatively broad (A-shares, Hong Kong stocks, indices, funds, futures, macro, etc.) | Focused (A-shares, Hong Kong stocks, ETFs, convertible bonds, funds, etc.) |
| **Data Quality** | Medium, depends on source websites, requires self-cleaning | High, standardized processing, XBRL financial report parsing | High, server-side unified cleaning and alignment |
| **Real-Time Data Support** | Partial support, depends on source website update frequency | Supported, requires advanced permissions (points) | Native support, low-latency real-time market data |
| **Historical Data Depth** | Medium, limited by source website data retention policies | Deep, traceable to early listing data | Deep, TongDaXin database complete history |
| **Data Update Frequency** | Minute-level updates | Daily updates (real-time requires advanced permissions) | Real-time updates (during trading hours) |

### 4.2 Interface Design and User Experience

| Comparison Dimension | openbb_akshare | openbb_tushare | openbb_tdx |
| ---------- | ---------------------------- | ---------------------------- | ------------------------ |
| **Installation Method** | `pip install openbb_akshare` | `pip install openbb_tushare` | `pip install openbb_tdx` |
| **Authentication Requirement** | Some data requires it, such as Xueqiu | Requires Tushare Token | Requires TongDaXin terminal running |
| **Usage Cost** | Completely free | Free version has limited functionality, advanced features require points | Free (requires TongDaXin terminal installation) |
| **Interface Stability** | Medium (affected by source website changes) | High (Pro API stable and reliable) | High (official interface, local communication) |
| **Call Frequency Limits** | Yes (need to control frequency to avoid anti-crawling) | Yes (varies by point level) | None (local communication, no frequency limits) |
| **Learning Cost** | Low | Low | Low (OpenBB unified interface) |

### 4.3 Functional Focus and Applicable Scenarios

| Comparison Dimension | openbb_akshare | openbb_tushare | openbb_tdx |
|---------|---------------|---------------|-----------|
| **Core Advantages** | Wide data coverage, many interfaces (800+) | High data quality, good standardization | Strong real-time market data, high data precision |
| **Best Scenarios** | Data exploration, multi-market analysis, academic research | Fundamental analysis, quantitative backtesting, institutional research | Intraday trading, real-time monitoring, high-frequency strategies |
| **Suitable Users** | Students, individual developers, beginners | Professional researchers, fintech companies | Intraday traders, real-time strategy developers |
| **Financial Data** | Basic financial data | Detailed financial statements (including XBRL parsing) | Basic and professional financial data |
| **Special Features** | Sentiment data, macro data, overseas markets | Index data, capital flow, dragon-tiger list | Tick data, sector data, custom sectors |

### 4.4 Performance Comparison

| Comparison Dimension | openbb_akshare | openbb_tushare | openbb_tdx |
|---------|---------------|---------------|-----------|
| **Data Acquisition Speed** | Medium (network requests, affected by network conditions) | Relatively fast (API calls, server response) | Fast (local communication, no network delay) |
| **Batch Data Acquisition** | Relatively slow (requires individual requests) | Medium (supports batch interfaces) | Fast (local batch reading) |
| **Real-Time Data Latency** | Second to minute level | Second level (advanced permissions) | Millisecond level (local real-time push) |
| **Stability** | Medium (source website changes may cause interface failures) | High (professional maintenance) | High (official product, local operation) |
| **Concurrency Capability** | Low (limited by anti-crawling strategies) | Medium (limited by points) | High (no local restrictions) |

### 4.5 Technical Architecture Comparison

| Comparison Dimension | openbb_akshare | openbb_tushare | openbb_tdx |
| --------- | ------------------------------ | ----------------------------- | ------------------------------ |
| **Architecture Pattern** | OpenBB Provider + AKShare SDK | OpenBB Provider + Tushare SDK | OpenBB Provider + TdxQuant SDK |
| **Communication Protocol** | HTTPS (web crawler) | HTTPS (RESTful API) | Local IPC (inter-process communication) |
| **Runtime Dependencies** | Python 3.11+, AKShare library, Xueqiu Token | Python 3.11+, Tushare library, Token | Python 3.13+, TongDaXin terminal |
| **Deployment Complexity** | Low (pip installation + Xueqiu Token configuration) | Low (pip installation + Token configuration) | Medium (requires TongDaXin terminal installation) |
| **Cross-Platform Support** | Windows / Linux / macOS | Windows / Linux / macOS | Windows only |


### 4.6 Selection Recommendations

Based on different usage scenarios and needs, we provide the following selection recommendations:

> **Scenarios recommending openbb_akshare:**
> - Comprehensive data analysis requiring coverage of multiple markets (A-shares, Hong Kong stocks, overseas markets, commodities, etc.);
> - Academic research and teaching scenarios requiring free and rich data interfaces;
> - Data exploration and prototype development stages requiring quick access to various types of data.
> - Cross-platform installation needs (supports Windows, macOS, and Linux)

> **Scenarios recommending openbb_tushare:**
> - Need high-quality, standardized fundamental data, especially detailed financial statement analysis;
> - Professional quantitative research and institutional-level applications with high data quality requirements;
> - Need special data like index data and capital flow.
> - Cross-platform installation needs (supports Windows, macOS, and Linux)

> **Scenarios recommending openbb_tdx:**
> - Intraday trading strategy development requiring low-latency real-time market data;
> - High-frequency data analysis and microstructure research requiring tick data;
> - Real-time monitoring and signal alert systems requiring stable and reliable real-time data push;
> - Already a TongDaXin user hoping to integrate existing workflows with the OpenBB ecosystem.
> - Requires TongDaXin client support, so only supports Windows

Of course, the three extension plugins are not mutually exclusive. In actual projects, users can flexibly combine and use multiple data sources according to different module data needs, fully leveraging their respective advantages. OpenBB's unified interface design makes multi-data source switching exceptionally simple.

---

## 5. Latest Status

### 5.1 Project Development Progress

The openbb_tdx project is currently in active development. As the third piece of FinAnalyzer's Chinese market data ecosystem layout, the project is rapidly iterating. Because it draws on the development experience of openbb_akshare and openbb_tushare, comprehensive optimizations have been made in interface design, data models, and test coverage.

### 5.2 Version Information

openbb_tdx follows semantic versioning and plans to distribute through PyPI. Users can install it through the following command:

```bash
pip install openbb_tdx

# Rebuild OpenBB resources to activate the plugin
python -c "import openbb; openbb.build()"
```

### 5.3 Technical Environment Requirements

Using openbb_tdx requires meeting the following environment requirements:

- **Python Version**: 3.13+ (3.13 recommended);
- **OpenBB Platform CLI**: Latest version;
- **TongDaXin Financial Terminal**: Version supporting TQ strategy functionality (such as Financial Terminal V7.72 and above).

Note that before running openbb_tdx programs, the TongDaXin financial terminal must be started first, which is a prerequisite for data acquisition.

#### Installing TongDaXin Financial Terminal
After installing the TongDaXin financial terminal, replace the `<TongDaXin installation directory>/PYPlugins/user/` directory with the following content:
https://github.com/finanalyzer/tdxquant
The purpose of this project is to replace the code in the original `user` directory with an installable Python project.

#### Installing openbb_tdx Plugin

Install the openbb_tdx project from the GitHub repository:
```cmd
git clone https://github.com/finanalyzer/tdx
cd tdx
poetry install
.venv\Scripts\activate
cd <TongDaXin installation directory>/PYPlugins/user/
pip install -e .
```

After installing the openbb_tdx plugin, rebuild OpenBB resources to activate the plugin.

```cmd
python -c "import openbb; openbb.build()"
```

---

## 6. Summary and Outlook

The birth of the openbb_tdx project marks an important step in OpenBB's Chinese market data ecosystem layout. By deeply integrating TongDaXin TdxQuant's official data interface with OpenBB's open architecture, openbb_tdx provides a new, high-quality data channel for Chinese quantitative investors.

Compared with the previously launched openbb_akshare and openbb_tushare, openbb_tdx has unique advantages in real-time market data acquisition. The three extension plugins each have their own focus and complement each other, together forming OpenBB's complete data solution for the Chinese market. Users can flexibly choose or combine them according to their own needs and scenarios.

OpenBB is redefining financial analysis - it is not only a financial terminal but also an integrated development environment (IDE) for the financial field. Its powerful data abstraction layer and scalable architecture provide unprecedented flexibility for AI-enhanced investment, localized data integration, and personalized analysis.

We sincerely invite developers and quantitative analysts to join the open-source ecosystem of openbb_tdx to jointly improve this data bridge connecting TongDaXin and OpenBB, and work together to promote the construction and development of China's open financial data ecosystem.

---

## Related Links

- OpenBB Official Website: https://openbb.co
- OpenBB GitHub: https://github.com/OpenBB-finance/OpenBB
- TdxQuant GitHub: https://github.com/finanalyzer/tdxquant
- openbb_tdx GitHub: https://github.com/finanalyzer/tdx
- openbb_akshare GitHub: https://github.com/finanalyzer/openbb_akshare
- openbb_tushare GitHub: https://github.com/finanalyzer/openbb_tushare
- openbb-hka GitHub: https://github.com/finanalyzer/openbb-hka
- TongDaXin Quantitative Help Documentation: https://help.tdx.com.cn/quant
- TongDaXin Download Center: https://www.tdx.com.cn/soft.html
- FinAnalyzer GitHub: https://github.com/finanalyzer

---

*Disclaimer: This article is for technical exchange and learning reference only and does not constitute any investment advice. Financial data analysis and quantitative trading involve risks, please investors make decisions carefully.*
