# 获取指定日期专业财务数据get_financial_data_by_date

### [#](https://help.tdx.com.cn/quant/docs/markdown/TdxQuant.md/mindoc-1h10mdt617qss.html#%E6%A0%B9%E6%8D%AE%E8%82%A1%E7%A5%A8-%E8%8E%B7%E5%8F%96%E6%8C%87%E5%AE%9A%E6%97%A5%E6%9C%9F%E7%9A%84%E4%B8%93%E4%B8%9A%E8%B4%A2%E5%8A%A1%E6%95%B0%E6%8D%AE-%E4%B8%8E%E5%9F%BA%E7%A1%80%E8%B4%A2%E5%8A%A1%E6%95%B0%E6%8D%AE%E4%B8%8D%E5%90%8C-%E9%9C%80%E8%A6%81%E5%85%88%E5%9C%A8%E5%AE%A2%E6%88%B7%E7%AB%AF%E4%B8%AD%E4%B8%8B%E8%BD%BD%E4%B8%93%E4%B8%9A%E8%B4%A2%E5%8A%A1%E6%95%B0%E6%8D%AE)根据股票，获取指定日期的专业财务数据，与基础财务数据不同，需要先在客户端中下载专业财务数据

```
get_financial_data_by_date(stock_list: List[str] = [],
                            field_list: List[str] = [],
                            year: int = 0,
                            mmdd: int = 0) -> Dict:
```

### [#](https://help.tdx.com.cn/quant/docs/markdown/TdxQuant.md/mindoc-1h10mdt617qss.html#%E8%BE%93%E5%85%A5%E5%8F%82%E6%95%B0)输入参数

| 参数         | 是否必选 | 参数类型      | 参数说明                 |
| ---------- | ---- | --------- | -------------------- |
| stock_list | Y    | List[str] | 证券代码列表               |
| field_list | Y    | List[str] | 字段筛选，不能为空（如 `FN193`） |
| year       | Y    | int       | 指定年份                 |
| mmdd       | Y    | int       | 指定月日                 |

- 如果year和mmdd都为0,表示最新的财报;
- 如果year为0,mmdd为小于300的数字,表示最近一期向前推mmdd期的数据,如果是331,630,930,1231这些,表示最近一期的对应季报的数据;
- 如果mmdd为0,year为一数字,表示最近一期向前推year年的同期数据;
- 季报分界点为:0331,0630,0930,1231
- 需要先在客户端中下载财务数据包

### [#](https://help.tdx.com.cn/quant/docs/markdown/TdxQuant.md/mindoc-1h10mdt617qss.html#%E8%BE%93%E5%87%BA%E6%95%B0%E6%8D%AE)输出数据

同get_financial_data一样。

### [#](https://help.tdx.com.cn/quant/docs/markdown/TdxQuant.md/mindoc-1h10mdt617qss.html#%E6%8E%A5%E5%8F%A3%E4%BD%BF%E7%94%A8)接口使用

```
from tqcenter import tq

tq.initialize(__file__)

fd = tq.get_financial_data_by_date(
        stock_list=['688318.SH'],
        field_list=['Fn193','Fn194','Fn195','Fn196','Fn197'],
        year=0,
        mmdd=0)
print(fd)
```

### [#](https://help.tdx.com.cn/quant/docs/markdown/TdxQuant.md/mindoc-1h10mdt617qss.html#%E6%95%B0%E6%8D%AE%E6%A0%B7%E6%9C%AC)数据样本

```
{'600519.SH':
{'FN193': '162.47',
'FN194': '69.67',
'FN195': '16.07',
'FN196': '8.71',
'FN197': '25.14'}}
```
