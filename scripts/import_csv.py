"""从 data/cipai_all.csv 导入词牌、词人、别称、作品关系到 Neo4j。"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db import get_driver
from parsers import clean_text, parse_classic_works, split_aliases

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "cipai_all.csv"


def ensure_constraints(session):
    session.run("CREATE CONSTRAINT cipai_name IF NOT EXISTS FOR (c:Cipai) REQUIRE c.name IS UNIQUE")
    session.run("CREATE CONSTRAINT poet_name IF NOT EXISTS FOR (p:Poet) REQUIRE p.name IS UNIQUE")
    session.run("CREATE CONSTRAINT alias_name IF NOT EXISTS FOR (a:Alias) REQUIRE a.name IS UNIQUE")
    session.run("CREATE CONSTRAINT work_key IF NOT EXISTS FOR (w:Work) REQUIRE w.key IS UNIQUE")


def import_aliases(session, cipai_name: str, alias_text: str, stats: dict):
    for alias in split_aliases(alias_text, cipai_name):
        session.run(
            """
            MATCH (c:Cipai {name: $cipai})
            MERGE (a:Alias {name: $alias})
            MERGE (c)-[:HAS_ALIAS]->(a)
            """,
            cipai=cipai_name,
            alias=alias,
        )
        stats["aliases"] += 1
        stats["alias_relations"] += 1


def import_works(
    session,
    cipai_name: str,
    classic_text: str,
    famous_line: str,
    default_poets: list[str],
    stats: dict,
):
    works = parse_classic_works(classic_text)
    if not works and famous_line:
        for poet in default_poets:
            key = f"{poet}::{cipai_name}"
            session.run(
                """
                MATCH (c:Cipai {name: $cipai})
                MERGE (w:Work {key: $key})
                SET w.title = $title,
                    w.famous_line = $line,
                    w.note = $note
                MERGE (p:Poet {name: $poet})
                MERGE (p)-[:WROTE]->(w)
                MERGE (w)-[:USES_CIPAI]->(c)
                """,
                key=key,
                cipai=cipai_name,
                poet=poet,
                title=cipai_name,
                line=famous_line,
                note="",
            )
            stats["works"] += 1
            stats["work_relations"] += 2
        return

    for work in works:
        poet = work["poet"] or (default_poets[0] if default_poets else "未知")
        title = work["title"]
        key = f"{poet}::{title}"
        line = famous_line if len(works) == 1 else work.get("note", "") or famous_line

        session.run(
            """
            MATCH (c:Cipai {name: $cipai})
            MERGE (w:Work {key: $key})
            SET w.title = $title,
                w.famous_line = $line,
                w.note = $note
            MERGE (p:Poet {name: $poet})
            MERGE (p)-[:WROTE]->(w)
            MERGE (w)-[:USES_CIPAI]->(c)
            """,
            key=key,
            cipai=cipai_name,
            poet=poet,
            title=title,
            line=line,
            note=work.get("note", ""),
        )
        stats["works"] += 1
        stats["work_relations"] += 2


def import_cipai_csv(driver, csv_path: Path) -> dict:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    stats = {
        "cipai": 0,
        "poets": 0,
        "represent_relations": 0,
        "aliases": 0,
        "alias_relations": 0,
        "works": 0,
        "work_relations": 0,
    }

    with driver.session() as session:
        ensure_constraints(session)

        for _, row in df.iterrows():
            name = clean_text(row["词牌"])
            if not name:
                continue

            alias_text = clean_text(row.get("别称", ""))
            classic = clean_text(row.get("经典篇目", ""))
            famous_line = clean_text(row.get("名句", ""))
            citype = clean_text(row.get("词体", ""))

            session.run(
                """
                MERGE (c:Cipai {name: $name})
                SET c.alias = $alias,
                    c.famous_line = $line,
                    c.classic_work = $classic,
                    c.type = $type
                """,
                name=name,
                alias=alias_text,
                line=famous_line,
                classic=classic,
                type=citype,
            )
            stats["cipai"] += 1

            poets = [p.strip() for p in clean_text(row["代表词人"]).split("、") if p.strip()]
            for poet in poets:
                session.run("MERGE (p:Poet {name: $poet})", poet=poet)
                session.run(
                    """
                    MATCH (p:Poet {name: $poet}), (c:Cipai {name: $name})
                    MERGE (p)-[:REPRESENT]->(c)
                    """,
                    poet=poet,
                    name=name,
                )
                stats["poets"] += 1
                stats["represent_relations"] += 1

            import_aliases(session, name, alias_text, stats)
            import_works(session, name, classic, famous_line, poets, stats)

    return stats


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"找不到 CSV: {CSV_PATH}")

    driver = get_driver()
    try:
        driver.verify_connectivity()
        stats = import_cipai_csv(driver, CSV_PATH)
        print(f"CSV 导入完成: {stats}")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
