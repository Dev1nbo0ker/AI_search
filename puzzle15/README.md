1.项目结构

```
run_puzzle15.py              # 主入口

puzzle15/
  __init__.py                # 包入口，导出常用函数
  types.py                   # 类型定义和 SearchResult
  constants.py               # 常量：棋盘大小、目标状态、反向移动、PDB 分组
  board.py                   # 棋盘合法性、可解性、邻居生成、执行移动
  cases.py                   # 默认测试样例
  experiment.py              # 实验运行和结果表格输出

  heuristics/
    __init__.py              # 启发函数统一导出
    basic.py                 # 曼哈顿距离、线性冲突
    pdb.py                   # Pattern Database 启发函数

  search/
    __init__.py              # 搜索算法统一导出
    astar.py                 # A* 搜索
    idastar.py               # IDA* 搜索
```

