# OpenBB-TDX 复权功能实现 - 产品需求文档

## Overview
- **Summary**: 为openbb_tdx的股票历史价格接口添加复权处理功能，支持前复权(qfq)和后复权(hfq)两种模式。
- **Purpose**: 解决当前openbb_tdx在获取历史股价时不支持复权的问题，使数据更准确地反映股票真实收益。
- **Target Users**: 使用openbb_tdx获取中国A股历史价格数据的开发者和量化分析师。

## Goals
- 在`TdxQuantEquityHistoricalQueryParams`中添加`adjustment`参数，支持`qfq`(前复权)、`hfq`(后复权)和`None`(不复权)三种选项
- 在`tdx_download_without_cache()`函数中实现复权参数到TdxQuant API的映射
- 在`tdx_download()`函数中传递复权参数
- 更新Fetcher的`extract_data()`方法以支持复权参数

## Non-Goals (Out of Scope)
- 不修改其他数据模型(如equity_quote, equity_profile等)
- 不修改AKShare或Tushare提供商的实现
- 不涉及前端界面修改

## Background & Context
- TdxQuant API的`get_market_data()`方法支持`dividend_type`参数，可设置为`none`、`front`、`back`
- OpenBB标准接口使用`adjustment`参数，支持`qfq`(前复权)和`hfq`(后复权)
- 当前实现中`dividend_type`硬编码为`'none'`，不支持复权

## Functional Requirements
- **FR-1**: 添加`adjustment`查询参数，类型为`Optional[Literal["qfq", "hfq"]]`，默认值为`None`
- **FR-2**: 实现`adjustment`到`dividend_type`的映射：`qfq`→`front`，`hfq`→`back`，`None`→`none`
- **FR-3**: 在数据获取链路中传递复权参数

## Non-Functional Requirements
- **NFR-1**: 向后兼容，不修改现有调用方式
- **NFR-2**: 错误处理，对于无效的adjustment值应抛出清晰的错误信息
- **NFR-3**: 代码风格符合项目规范

## Constraints
- **Technical**: Python 3.11+，遵循OpenBB Platform规范
- **Dependencies**: TdxQuant SDK (`tqcenter.tq`)

## Assumptions
- TdxQuant API的`dividend_type`参数正常工作
- 用户了解前复权和后复权的区别

## Acceptance Criteria

### AC-1: adjustment参数定义正确
- **Given**: 查询参数包含adjustment字段
- **When**: 创建`TdxQuantEquityHistoricalQueryParams`实例
- **Then**: adjustment参数应为`Optional[Literal["qfq", "hfq"]]`类型，默认值为`None`
- **Verification**: `programmatic`

### AC-2: 复权参数映射正确
- **Given**: adjustment参数为`qfq`
- **When**: 调用`tdx_download_without_cache()`
- **Then**: TdxQuant API的`dividend_type`参数应为`front`
- **Verification**: `programmatic`

### AC-3: 复权参数映射正确(hfq)
- **Given**: adjustment参数为`hfq`
- **When**: 调用`tdx_download_without_cache()`
- **Then**: TdxQuant API的`dividend_type`参数应为`back`
- **Verification**: `programmatic`

### AC-4: 不复权参数映射正确
- **Given**: adjustment参数为`None`
- **When**: 调用`tdx_download_without_cache()`
- **Then**: TdxQuant API的`dividend_type`参数应为`none`
- **Verification**: `programmatic`

### AC-5: 向后兼容性
- **Given**: 不传递adjustment参数(默认值)
- **When**: 调用历史价格接口
- **Then**: 行为与修改前一致(不复权)
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要为缓存机制添加复权类型的区分？(当前缓存不区分复权类型，可能导致数据不一致)

---

**参数定义规范**:
```python
adjustment: Optional[Literal["qfq", "hfq"]] = Field(
    default=None,
    description="Adjustment type for historical prices. 'qfq' for forward-adjusted (前复权), 'hfq' for backward-adjusted (后复权). None means no adjustment.",
)
```

**映射关系**:
| OpenBB adjustment | TdxQuant dividend_type |
|-------------------|----------------------|
| None              | none                 |
| qfq               | front                |
| hfq               | back                 |