# 宋词本体（Protégé）

> 源文件：`SongCi_Ontology.rdf`（由 Protégé 导出）  
> 命名空间：`http://www.semanticweb.org/liuch/ontologies/2026/5/untitled-ontology-2#`

---

## 一、本体概览

本本体采用 **Top-down（自上而下）** 方法构建，描述宋词领域中的主体、作品、词牌、乐器及形式格律等概念及其关系。概念层（T-Box）在 Protégé 中定义，实例数据（A-Box）由 Neo4j 中的 CSV / Word 导入脚本批量灌入。

答辩时建议顺序：**Protégé 类层次 → HermiT 推理截图 → Neo4j 实例图谱 → Web 交互**。

---

## 二、类（Classes）

```
LiteratureWork（文学作品）
├── Songci（宋词）
└── TangPoetry（唐诗）

Form_Metrics（形式格律）
├── Cipai（词牌）
└── PoetryForm（诗体）

Agent（主体）
LiteraryStyle（文学流派）
MusicalInstrument（乐器）
```

| 类名 | 中文 | 说明 |
|------|------|------|
| `Agent` | 主体 | 词人、作者等人物的上位类 |
| `LiteratureWork` | 文学作品 | 作品总类 |
| `Songci` | 宋词 | 宋词作品 |
| `TangPoetry` | 唐诗 | 可扩展的并行分支 |
| `Form_Metrics` | 形式格律 | 格律、词牌格式 |
| `Cipai` | 词牌 | 词牌名，如念奴娇 |
| `PoetryForm` | 诗体 | 与词牌并列的格律类 |
| `LiteraryStyle` | 文学流派 | 如豪放派、婉约派 |
| `MusicalInstrument` | 乐器 | 如笙、琵琶 |

---

## 三、对象属性（Object Properties）

| 属性 | Domain | Range | 含义 |
|------|--------|-------|------|
| `write` | `Agent` | `LiteratureWork` | 主体创作/书写作品 |
| `accompaniedBy` | `Songci` | `MusicalInstrument` | 宋词作品的伴奏乐器 |
| `hasMetrics` | `LiteratureWork` | `Form_Metrics` | 作品所遵循的形式格律 |

---

## 四、数据属性（Data Properties）

| 属性 | Domain | 类型 | 含义 |
|------|--------|------|------|
| `hasAlternativeName` | `Cipai` | string | 词牌别称 |
| `famousLine` | `LiteratureWork` | string | 名句 |

---

## 五、Demo 实例（Individuals）

Protégé 中手动录入的示例，用于 HermiT 推理验证：

| 个体 | 类型 | 关系 / 属性 |
|------|------|-------------|
| `SuShi` | `Agent` | `write` → `NianNujiao` |
| `NianNujiao` | `Cipai` | `hasAlternativeName` = 「百词令」 |

> **注意：** CSV 中念奴娇的别称为「百字令」，本体 Demo 中写作「百词令」，答辩时可说明 Demo 实例与批量数据分别维护，或以 CSV 为准统一修正。

---

## 六、HermiT 推理验证

使用 Protégé **Reasoner → HermiT → Start reasoner** 进行一致性检测。

截图见 `document/img/P1.png`（类层次概览）、`document/img/P2.png`（属性与推理细节）。

---

## 七、OWL 与 Neo4j 概念对照

| Protégé（OWL） | Neo4j 标签 / 关系 | 说明 |
|----------------|-------------------|------|
| `Agent` | `:Poet` | 实例层将词人具体化为 Poet 节点 |
| `Cipai` | `:Cipai` | 词牌，一致 |
| `LiteratureWork` / `Songci` | `:Work` | 具体篇目在 Neo4j 中为 Work 节点 |
| `hasAlternativeName` | `:Alias` + `HAS_ALIAS` | Neo4j 将别称拆为独立节点 |
| `MusicalInstrument` | `:Instrument` | 乐器 |
| `LiteraryStyle` | `:CiStyle` | 流派 |
| — | `:Period` | 朝代由 Word 文献补充，OWL 中可后续扩展 |
| `write` | `WROTE` | 词人 → 作品 |
| `accompaniedBy` | `ACCOMPANIED_BY` | 词牌/作品 → 乐器 |
| — | `REPRESENT` | 词人代表词牌，来自 CSV 业务关系 |

**设计说明：** OWL 侧重概念建模与推理；Neo4j 在保持一致语义的前提下，增加了 `REPRESENT`、`ACTIVE_IN`、`BELONGS_TO` 等面向检索与可视化的关系，便于 Cypher 查询和前端展示。

---

## 八、文件清单

| 文件 | 说明 |
|------|------|
| `SongCi_Ontology.rdf` | Protégé 导出的 OWL/RDF 本体 |
| `screenshots/` | 可存放 Protégé 界面截图备份 |

---

## 九、后续可选

1. 在 Protégé 中补充 `Period`（朝代）类及 `activeIn` 属性，与 Neo4j 对齐  
2. 将 `SuShi` 的类型细化为 `Poet`（作为 `Agent` 子类）  
3. 使用 Neo4j n10s 插件导入 RDF（见 `document/实现路线文档.md` §3.5）  
4. 修正 Demo 别称「百词令」→「百字令」，与 CSV 一致  
