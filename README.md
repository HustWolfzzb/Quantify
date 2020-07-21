# Quantify
股票量化，包含股票知识图谱以及历史数据以及自动化交易

## 股票关系可视化

通过Neo4j来构建股票市场的知识图谱
`    paras2cn = {"code":"代码",
                "name":"名称",
                "industry":"细分行业",
                "area":"地区",
                "pe":"市盈率",
                "outstanding":"流通股本",
                "totals":"总股本(万)",
                "totalAssets":"总资产(万)",
                "liquidAssets":"流动资产",
                "fixedAssets":"固定资产",
                "reserved":"公积金",
                "reservedPerShare":"每股公积金",
                "esp":"每股收益",
                "bvps":"每股净资",
                "pb":"市净率",
                "timeToMarket":"上市日期"
             }`

## 股票历史数据存储

通过Mysql结构化存储每日交易信息
>keys = ['open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change', 'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20']

