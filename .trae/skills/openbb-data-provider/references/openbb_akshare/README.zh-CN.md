# 如何使用AKShare作为OpenBB的数据源

**OpenBB** 作为**开源金融数据平台**，致力于为投资者、分析师与开发者提供免费透明的金融数据接口。关于OpenBB的介绍以及如何使用，请参阅[OpenBB的介绍以及如何使用OpenBB助力A股港股的金融数据分析](https://blog.csdn.net/qq_29953771/article/details/148971007?fromshare=blogdetail&sharetype=blogdetail&sharerId=148971007&sharerefer=PC&sharesource=qq_29953771&sharefrom=from_link)。

OpenBB虽支持多个数据源，但中国区（含香港）金融数据获取主要依赖Yahoo Finance。该平台作为免费基础数据源虽能满足基本需求，但对中港市场的覆盖深度仍显不足。更关键的是，中国内地用户需借助VPN方可访问此服务，形成显著使用门槛。

要查询A股和港股数据，OpenBB亟待完善本地化金融数据源的接入。A股和港股数据，付费的主流方案包括Wind、东方财富Choice和同花顺iFind（主要面向机构客户）；免费数据则以开源的AKShare为主要替代方案。AKShare通过整合东财/同花顺/腾讯/新浪/雪球等平台的免费数据，已成为国内Python生态中数据覆盖最全面、更新最及时、开发者体验最优的金融数据聚合库之一。

`openbb_akshare`项目作为 OpenBB 的数据源扩展，可实现 AKShare 数据在 OpenBB 平台的无缝接入。以下为详细使用指南：

## 💻 环境搭建与安装流程

作为开发者，我们主要通过OpenBB Platform CLI与平台交互。要集成AKShare数据源，需按以下步骤配置开发环境：

1. 创建Python虚拟环境

   可以使用uv或者poetry来创建虚拟环境。在这里，我使用Python自带的组件venv来搭建虚拟环境。

   ```bash
   python3 -m venv .venv
   ```

   创建了虚拟环境后，可以用下面的命令使用这个虚拟环境。

   ```bash
   source .venv/bin/activate
   ```

   注：Windows系统执行`.venv\Scripts\activate`

2. 安装OpenBB Platform CLI

   在上面的虚拟环境中，我们需要先安装`openbb-cli`来使用OpenBB Platform CLI。

   ```bash
   pip install openbb-cli
   ```

   如果你在中国大陆，可以先设置下面的环境变量。这样可以使用阿里的镜像来加速安装过程。

   ```powershell
   set PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
   ```

3. 安装openbb_akshare

   接下来，我们需要安装`openbb_akshare`来使用AKShare数据源。

   ```bash
   pip install openbb_akshare
   ```

   安装`openbb_akshare`后，需要重新构建资源让安装生效。

   ```bash
   python -c "import openbb; openbb.build()"
   ```

## 🚀 使用 AKShare 数据源

### 案例 1：查询 A 股公司动态（以万科为例）

**Jupyter Notebook 代码示例**：

```Python
from openbb import obb
messages = obb.news.company("000002", provider="akshare")
for result in messages.results:
    print(f"{result.title}")
```

执行结果：

```plaintext
开源证券发布万科A研报，公司信息更新报告：销售均价有所提升，股东持续借款提供支持
万科A出售2086万股库存股，金额1.36亿元
万科A：已完成所有A股库存股出售 所得资金4.79亿元
...
```

**命令行查询方式**：

```bash
openbb
2025 Jun 26, 03:11 (🦋) /news/ $ company --symbol 000002 --provider akshare
```

输入上述命令，我们可以看到下面的结果。OpenBB CLI的结果会显示在一个WebView里，如下图所示：

![openbb04](docs/images/openbb04.png)

### 案例 2：获取港股历史股价（以香港电讯为例）

**命令行查询**:

AKShare也提供港股数据，我们可以使用下面的命令来查询"香港电讯"的股价历史。

```
2025 Jun 26, 03:28 (🦋) /equity/price/ $ historical --symbol 06823 --provider akshare
```

我们可以看到下面的WebView输出：![openbb05](docs/images/openbb05.png)

**Jupyter Notebook 代码示例**：

同样的，我们也可以用代码来查询"香港电讯"的股价，如下：

```Python
from openbb import obb
prices = obb.equity.price.historical(symbol='06823', start_date="2025-06-01", end_date="2025-06-10", provider="akshare")
prices.results[0].date, prices.results[0].open, prices.results[0].close, prices.results[0].high, prices.results[0].low, prices.results[0].volume
```

输出示例：

```
(datetime.date(2025, 6, 2), 11.28, 11.3, 11.3, 11.14, 10308375)
```

## 🌟 openbb_akshare 项目生态

目前`openbb_akshare`项目正处于活跃开发阶段，欢迎开源社区贡献力量：

**代码仓库**：

- GitHub：https://github.com/finanalyzer/openbb_akshare

- GitCode（国内镜像）：https://gitcode.com/finanalyzer/openbb_akshare

**参与方式**：

1. 提交 Issue 反馈数据需求或 Bug

2. 贡献 PR 优化数据源接口

3. 完善文档帮助更多用户

通过 AKShare 与 OpenBB 的集成，中国区用户可更便捷地获取 A 股、港股等市场的实时与历史数据，为量化分析、投资研究提供强有力的数据支撑。