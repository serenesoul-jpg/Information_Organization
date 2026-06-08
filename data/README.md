# 数据目录说明

## 文件一览

| 文件 | 说明 | 记录数 |
|------|------|--------|
| `cipai_all.csv` | **推荐导入用**：三份原始表合并、字段统一、已清洗 | 30 |
| `cipai_xiaoling.csv` | 小令词牌 | 11 |
| `cipai_zhongdiao.csv` | 中调词牌 | 8 |
| `cipai_changdiao.csv` | 长调/慢词词牌 | 11 |
| `raw/` | 原始导出备份，不参与脚本导入 | — |

## 字段说明（清洗后统一格式）

| 列名 | 含义 | 示例 |
|------|------|------|
| `词牌` | 词牌正名 | 念奴娇 |
| `别称` | 别名，多个以顿号分隔 | 百字令、酹江月 |
| `代表词人` | 代表词人，多个以顿号分隔 | 苏轼、辛弃疾 |
| `词体` | 小令 / 中调 / 长调 | 长调 |
| `经典篇目` | 代表作品及篇名 | 苏轼《赤壁怀古》：大江东去 |
| `名句` | 名句摘录 | 大江东去，浪淘尽，千古风流人物 |

## 原始文件来源

三份 CSV 原位于 `document/`，由同一批数据按词体长度拆分导出：

- `raw/code_20260606_02_小令.csv` — 原 `code_20260606(2).csv`，含「名句」列
- `raw/code_20260606_04_中调.csv` — 原 `code_20260606(4).csv`，无独立「名句」列
- `raw/code_20260606_06_长调.csv` — 原 `code_20260606(6).csv`，「名篇」列对应清洗后的「经典篇目」

## 清洗规则

1. 去除 `[__LINK_ICON]` 等导出残留标记
2. 将「名篇」列统一为「经典篇目」
3. 中调/长调表中无「名句」时，尝试从「经典篇目」冒号后提取
4. 新增「词体」列，标记小令 / 中调 / 长调

## 导入 Neo4j 时注意

- `代表词人` 含多人时，需按 `、` 拆分后分别建立 `(Poet)-[:REPRESENT]->(Cipai)` 关系
- `别称` 会拆分为独立 `:Alias` 节点，建立 `(Cipai)-[:HAS_ALIAS]->(Alias)`
- `经典篇目` 会解析为 `:Work` 节点，建立 `(Poet)-[:WROTE]->(Work)-[:USES_CIPAI]->(Cipai)`
- 乐器、朝代、流派等关系由 `scripts/extract_docx.py` 从 Word 补充

**导入后预期规模（约）：** 30 词牌 + 20 词人 + 33 别称 + 32 作品 + 3 乐器 + 3 流派 + 4 朝代

## 待补充

- `宋词.docx`：词风、乐器、朝代背景文献，由 `scripts/generate_docx.py` 生成，`scripts/extract_docx.py` 解析入库

## 导入命令

```bash
# 1. 启动 Neo4j
docker compose up -d

# 2. 一键导入（CSV + Word 补充数据）
python scripts/run_import.py
```

默认连接：`bolt://localhost:7687`，用户名 `neo4j`，密码 `neo4j`（本机）或 `songci2026`（Docker，见 `docker-compose.yml`）。

## Neo4j 演示查询

```cypher
// 词牌 + 别称 + 作品 + 词人 + 乐器（推荐）
MATCH (c:Cipai)-[:HAS_ALIAS]->(a:Alias)
MATCH (w:Work)-[:USES_CIPAI]->(c)
MATCH (p:Poet)-[:WROTE]->(w)
OPTIONAL MATCH (c)-[:ACCOMPANIED_BY]->(i:Instrument)
RETURN c, a, w, p, i
LIMIT 100

// 念奴娇完整子图
MATCH (c:Cipai {name: '念奴娇'})
OPTIONAL MATCH (c)-[r1]->(n1)
OPTIONAL MATCH (n2)-[r2]->(c)
RETURN c, r1, n1, r2, n2
```
