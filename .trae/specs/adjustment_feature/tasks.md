# OpenBB-TDX 复权功能实现 - 任务分解

## [ ] Task 1: 在TdxQuantEquityHistoricalQueryParams中添加adjustment参数
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 在`openbb_tdx/models/equity_historical.py`中，为`TdxQuantEquityHistoricalQueryParams`类添加`adjustment`字段
  - 使用指定的参数定义格式
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 验证adjustment参数类型为Optional[Literal["qfq", "hfq"]]，默认值为None
  - `programmatic` TR-1.2: 验证adjustment参数描述正确
- **Notes**: 需要导入Literal类型

## [ ] Task 2: 修改tdx_download_without_cache()函数支持adjustment参数
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 在`openbb_tdx/utils/helpers.py`中，为`tdx_download_without_cache()`函数添加`adjustment`参数
  - 实现adjustment到dividend_type的映射逻辑
  - 在调用`tq.get_market_data()`时使用映射后的dividend_type值
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-2.1: 验证adjustment=None时dividend_type='none'
  - `programmatic` TR-2.2: 验证adjustment='qfq'时dividend_type='front'
  - `programmatic` TR-2.3: 验证adjustment='hfq'时dividend_type='back'
- **Notes**: 需要处理参数的可选性

## [ ] Task 3: 修改tdx_download()函数传递adjustment参数
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 在`openbb_tdx/utils/helpers.py`中，为`tdx_download()`函数添加`adjustment`参数
  - 将adjustment参数传递给`tdx_download_without_cache()`
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: 验证adjustment参数能正确传递到底层函数
- **Notes**: 需要考虑缓存机制是否需要区分复权类型

## [ ] Task 4: 修改Fetcher的extract_data()方法传递adjustment参数
- **Priority**: P0
- **Depends On**: Task 1, Task 3
- **Description**: 
  - 在`openbb_tdx/models/equity_historical.py`的`TdxQuantEquityHistoricalFetcher.extract_data()`方法中，将`query.adjustment`传递给`tdx_download()`函数
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: 验证Fetcher能正确传递adjustment参数
- **Notes**: 需要确保参数名一致

## [x] Task 5: 添加单元测试验证复权功能
- **Priority**: P1
- **Depends On**: Task 1-4
- **Description**: 
  - 在`tests/test_equity_historical.py`中添加测试用例
  - 测试adjustment参数的各种取值情况
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 测试adjustment参数的有效性验证
  - `programmatic` TR-5.2: 测试不同adjustment值对应的行为
- **Notes**: 测试应使用mock来避免实际调用API

## [ ] Task 6: 更新check_cache()函数支持adjustment参数(可选)
- **Priority**: P2
- **Depends On**: Task 2
- **Description**: 
  - 在`check_cache()`函数中添加adjustment参数
  - 考虑是否需要为不同复权类型维护独立的缓存
- **Acceptance Criteria Addressed**: N/A
- **Test Requirements**:
  - `human-judgement` TR-6.1: 检查缓存机制是否正确处理不同复权类型
- **Notes**: 当前缓存不区分复权类型，这可能导致数据不一致，需要评估是否需要修改