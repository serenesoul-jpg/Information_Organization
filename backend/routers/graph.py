from fastapi import APIRouter, HTTPException, Query

from backend.cypher.graph import (
    CONTEXT_QUERY,
    GRAPH_QUERY,
    NODE_DETAIL_QUERY,
    SEARCH_QUERY,
    TIMELINE_QUERY,
)
from backend.db import get_driver
from backend.services.graph_builder import build_graph_from_records, serialize_node_detail

router = APIRouter(prefix="/api")


@router.get("/graph")
def get_graph(period: str | None = None, limit: int = Query(120, ge=10, le=300)):
    driver = get_driver()
    with driver.session() as session:
        result = session.run(GRAPH_QUERY, period=period, limit=limit)
        return build_graph_from_records(result)


@router.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(80, ge=10, le=200)):
    driver = get_driver()
    with driver.session() as session:
        result = session.run(SEARCH_QUERY, q=q, limit=limit)
        return build_graph_from_records(result)


@router.get("/node/{node_id}")
def get_node(node_id: str):
    driver = get_driver()
    with driver.session() as session:
        record = session.run(NODE_DETAIL_QUERY, node_id=node_id).single()
        if not record or record["n"] is None:
            raise HTTPException(status_code=404, detail="节点不存在")
        return serialize_node_detail(record)


@router.get("/timeline")
def get_timeline():
    driver = get_driver()
    with driver.session() as session:
        rows = session.run(TIMELINE_QUERY)
        return [{"period": r["period"], "count": r["count"]} for r in rows]


@router.get("/context")
def get_context():
    driver = get_driver()
    with driver.session() as session:
        record = session.run(CONTEXT_QUERY).single()
        return {"content": record["content"] if record else ""}
