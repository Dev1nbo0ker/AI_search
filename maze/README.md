1.项目结构:

```
run_maze.py                  # 主程序入口

maze/
  __init__.py                # 把常用函数统一导出
  models.py                  # 数据结构：MazeProblem、SearchResult
  parser.py                  # 解析迷宫字符串
  grid_utils.py              # 判断边界、是否可走、找邻居
  path_utils.py              # 回溯路径、合并双向搜索路径
  render.py                  # 打印搜索结果、把路径画出来
  runner.py                  # 统一运行所有算法

  algorithms/
    bfs.py                   # 广度优先搜索
    dfs.py                   # 深度优先搜索
    dls.py                   # 深度受限搜索
    ids.py                   # 迭代加深搜索
    bidirectional.py         # 双向搜索
```

2.`run_maze.py` 主程序写入了示例迷宫

```
maze_lines = [
    "111111111111111111111111111111111111",
    "1000000000000000000000000000000000S1",
    ...
    "1E0000000001111111111111111000000001",
    "111111111111111111111111111111111111",
]
```

3.`models.py` 数据结构

```
@dataclass
class SearchResult:
    algorithm: str
    found: bool
    path: list[Pos]
    visited_count: int
    status: Literal["success", "failure", "cutoff"]
    depth: int
```

`@dataclass`: 是一个装饰器, 用于只装数据的类. 不需要手写`__init__`和`__repr__`等, 装饰器会自动生成下面的方法

| **功能**     | **参数设置**         | **描述**                                                     |
| ------------ | -------------------- | ------------------------------------------------------------ |
| **只读属性** | `frozen=True`        | 使类变为不可变（Immutable），类似 `namedtuple`。             |
| **排序**     | `order=True`         | 自动生成 `__lt__`, `__gt__` 等，让对象可以直接比较大小（按字段顺序）。 |
| **默认值**   | `price: float = 0.0` | 可以直接给字段赋默认值。                                     |

使用 `dataclass` 时，**类型注解**（Type Hints）是必须的。虽然运行过程中 Python 不会强制检查类型，但装饰器是根据这些注解来识别哪些变量需要被处理成字段的。

`Literal`: 限制`status`字段为字面量, 可以提前暴露拼写错误. 但如果拼错, 运行时不会报错.



4.`parser.py` 迷宫解析

```python
row = [ch for ch in raw.strip().replace(" ", "")]
```

`raw.strip()`: 去除字符串最左边和最右边的所有空白字符(包括空格、换行符 `\n`、制表符 `\t` 等).

`.replace(" ", "")`: 把中间所有的空格(Space)替换成空字符(即删除掉所有的空格).

`[ch for ch in ...]`: 这是一个列表推导式(List Comprehension).它会遍历上一步得到的字符串, 把每一个字符(`ch`)拿出来，塞进一个新的列表里.

改进写法:

```python
row = list("".join(raw.split()))
```

字符串在 Python 中本身就是可迭代的(Iterable), 不需要用 `for` 循环手动去“装填”列表, 直接使用内置的 `list()` 函数转换会更快、更简洁

`.replace(" ", "")` 只能删掉普通的空格. 如果字符串里夹杂了制表符（`\t`）或换行符（`\n`）, 它们会被保留下来.

`raw.split()` 在不传参数时, 会自动以任何空白字符(空格、换行、制表符)为分隔符将字符串切成片段, 然后用 `"".join()` 把纯文本片段无缝拼接起来. 最后用 `list()` 打散成单字符.

5.`grid_utils.py` 网格工具

6.`path_utils.py` 路径回溯

搜索时，程序不会每一步都保存完整路径, 而是保存一个 `parent` 字典.

例如：

```
parent[(1, 2)] = (1, 1)
parent[(1, 3)] = (1, 2)
parent[(2, 3)] = (1, 3)
```

意思是：

```
(1,2) 是从 (1,1) 来的
(1,3) 是从 (1,2) 来的
(2,3) 是从 (1,3) 来的
```

如果终点是 `(2, 3)`，就可以倒着找：

```
(2,3) -> (1,3) -> (1,2) -> (1,1)
```

再反转一下，就得到从起点到终点的路径：

```
(1,1) -> (1,2) -> (1,3) -> (2,3)
```

7.`render.py` 输出渲染

把找到的路径用`*`标出来

8.五种搜索算法

8.1 DFS: 注意在`neighbor`中找下一个入栈的节点时, 要反转. DFS不保证找到的路径最短

8.2 BFS: 节点在入队时就标记`visited`, 以防同一个节点被多个父节点重复加入队列. BFS保证找到的路径是最短的

8.3 DLS: 注意区分`cutoff`:因达到深度限制而被截断 `failure`: 确定找不到

8.4 ILS: 迭代加深搜索, 反复调用DLS, 逐渐增加深度

8.5 双向搜索: 起点终点同时BFS.

9.`runner.py`：统一运行所有算法

10.整体执行流程

```
运行 run_maze.py
        ↓
读取 maze_lines
        ↓
parse_maze() 解析迷宫
        ↓
得到 MazeProblem
        ↓
run_all(problem)
        ↓
依次执行 DFS / BFS / DLS / IDS / 双向搜索
        ↓
每个算法返回 SearchResult
        ↓
print_result() 打印结果
        ↓
render_path() 用 * 画出路径
```