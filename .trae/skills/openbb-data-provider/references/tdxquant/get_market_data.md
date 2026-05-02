# 获取K线行情get_market_data

### [#](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1h10g60jt68sc.html#%E6%A0%B9%E6%8D%AE%E8%82%A1%E7%A5%A8-%E8%8E%B7%E5%8F%96%E5%8E%86%E5%8F%B2%E8%A1%8C%E6%83%85)根据股票，获取历史行情

```
get_market_data(field_list: List[str] = [],
                stock_list: List[str] = [],
                period: str = '',
                start_time: str = '',
                end_time: str = '',
                count: int = -1,
                dividend_type: Optional[str] = None,
                fill_data: bool = True) -> Dict:
```

### [#](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1h10g60jt68sc.html#%E8%BE%93%E5%85%A5%E5%8F%82%E6%95%B0)输入参数

| 参数            | 是否必选 | 参数类型      | 参数说明                                                                                                                                                  |
| ------------- | ---- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| field_list    | N    | List[str] | 字段筛选，传空则返回全部                                                                                                                                          |
| stock_list    | Y    | List[str] | 证券代码列表                                                                                                                                                |
| period        | Y    | str       | 周期                                                                                                                                                    |
| start_time    | N    | str       | 起始时间                                                                                                                                                  |
| end_time      | N    | str       | 结束时间                                                                                                                                                  |
| count         | N    | int       | 返回数据个数（每只股票）                                                                                                                                          |
| dividend_type | N    | str       | [复权类型 (opens new window)](https://help.tdx.com.cn/quant/docs/markdown/Dict.html#%E5%A4%8D%E6%9D%83%E7%B1%BB%E5%9E%8B "复权类型")：none不复权、front前复权、back后复权 |
| fill_data     | N    | bool      | 是否向后填充空缺数据                                                                                                                                            |

count小于等于0或者count为空：  
1、开始日期结束日期数据数据；  
2、开始日期无值， 从第一根k取到 结束日期  
3、结束日期无值，从开始日期取到最后一根  
4、都没值取全部本地数据  
count大于0时：  
1、结束日期往前n个数据  
2、结束日期无时从最后一根k线往前取n。

### [#](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1h10g60jt68sc.html#%E8%BF%94%E5%9B%9E%E6%95%B0%E6%8D%AE)返回数据

- 返回dict { field1 : value1, field2 : value2, ... }
- field1, field2, ... ：数据字段
- value1, value2, ... ：pd.DataFrame 数据集，index为stock_list，columns为time_list
- 各字段对应的DataFrame维度相同、索引相同
- 只有dividend_type传入为none时，会返回有效的前复权因子ForwardFactor
- 后复权数据与取的数据个数有关，只在返回的数据中进行后复权
- 一次最多返回24000条数据，要获取完整分钟线需要多次分批获取
- 返回复权数据时，若该组数据时间内未发生权息变动，则复权价与未复权价相同，

| 数据            | 默认返回 | 数据类型 | 数据说明                             |
| ------------- | ---- | ---- | -------------------------------- |
| Date          | Y    | str  | 日期                               |
| Time          | Y    | str  | 时间                               |
| Open          | Y    | str  | 开盘价                              |
| High          | Y    | str  | 最高价                              |
| Low           | Y    | str  | 最低价                              |
| Close         | Y    | str  | 收盘价                              |
| Volume        | Y    | str  | 成交量                              |
| Amount        | Y    | str  | 成交额                              |
| ForwardFactor | Y    | str  | 前复权因子，当dividend_type=none时候返回有效值 |
| VolInStock    | N    | str  | 持仓量                              |

- 期货数据时Amount为0，非期货数据时VolInStock为0

### [#](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1h10g60jt68sc.html#%E6%8E%A5%E5%8F%A3%E4%BD%BF%E7%94%A8)接口使用

> 获取688318.SH从2025-12-20到今为止最新一条日K线的不复权数据

```
from tqcenter import tq
tq.initialize(__file__)
df = tq.get_market_data(
        field_list=[],
        stock_list=['688318.SH'],
        start_time='20251220',
        end_time='',
        count=1,
        dividend_type='none',
        period='1d',
        fill_data=True
    )
print(df)
```

### [#](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1h10g60jt68sc.html#%E6%95%B0%E6%8D%AE%E6%A0%B7%E6%9C%AC)数据样本

```
{'Amount':             688318.SH
2025-12-24   29394.81,
'Low':             688318.SH
2025-12-24      128.0,
'Date':              688318.SH
2025-12-24  20251224.0,
'Volume':             688318.SH
2025-12-24  2257325.0,
'Close':             688318.SH
2025-12-24     131.58,
'Open':             688318.SH
2025-12-24     128.01,
'Time':             688318.SH
2025-12-24        0.0,
'High':             688318.SH
2025-12-24     131.87,
'ForwardFactor':             688318.SH
2025-12-24        1.0}
```
