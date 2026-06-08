import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db import get_driver

LABELS = ["Cipai", "Poet", "Alias", "Work", "Instrument", "CiStyle", "Period", "Context"]
RELS = ["REPRESENT", "HAS_ALIAS", "WROTE", "USES_CIPAI", "ACCOMPANIED_BY", "BELONGS_TO", "ACTIVE_IN", "RELATED_TO", "MENTIONED_IN"]

d = get_driver()
with d.session() as s:
    print("=== 宋词节点统计 ===")
    for label in LABELS:
        n = s.run(f"MATCH (n:{label}) RETURN count(n) AS c").single()["c"]
        print(f"  {label}: {n}")

    print("\n=== 宋词关系统计 ===")
    for rel in RELS:
        n = s.run(f"MATCH ()-[r:{rel}]->() RETURN count(r) AS c").single()["c"]
        if n:
            print(f"  {rel}: {n}")

    print("\n=== 念奴娇 扩展子图 ===")
    q = """
    MATCH (c:Cipai {name: '念奴娇'})
    OPTIONAL MATCH (c)-[:HAS_ALIAS]->(a:Alias)
    OPTIONAL MATCH (w:Work)-[:USES_CIPAI]->(c)
    OPTIONAL MATCH (p:Poet)-[:WROTE]->(w)
    RETURN c.name AS cipai, collect(DISTINCT a.name) AS aliases,
           collect(DISTINCT w.title) AS works,
           collect(DISTINCT p.name) AS poets
    """
    print(dict(s.run(q).single()))

    print("\n=== 完整路径数量 ===")
    q2 = """
    MATCH (p:Poet)-[:REPRESENT|WROTE*1..2]->(c:Cipai)
    WHERE c.type IS NOT NULL
    RETURN count(DISTINCT p) AS poets, count(DISTINCT c) AS cipai
    """
    print(dict(s.run(q2).single()))
d.close()
