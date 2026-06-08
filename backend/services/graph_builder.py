"""Convert Neo4j records to graph JSON for frontend."""

NODE_COLORS = {
    "Poet": "#4A90D9",
    "Cipai": "#C47A20",
    "Instrument": "#3A9E6A",
    "Period": "#8B5FBF",
    "CiStyle": "#C0392B",
    "Alias": "#7F8C8D",
    "Work": "#D4A017",
    "Context": "#5D6D7E",
}

GRAPH_RECORD_LINKS = [
    ("p2", "c", "REPRESENT"),
    ("c", "a", "HAS_ALIAS"),
    ("w", "c", "USES_CIPAI"),
    ("p", "w", "WROTE"),
    ("c", "i", "ACCOMPANIED_BY"),
    ("p2", "s", "BELONGS_TO"),
    ("p2", "per", "ACTIVE_IN"),
]


def node_label(node) -> str:
    labels = list(node.labels)
    return labels[0] if labels else "Unknown"


def node_name(node) -> str:
    for key in ("name", "title", "key"):
        if node.get(key):
            return str(node[key])
    return node_label(node)


def serialize_node(node) -> dict:
    label = node_label(node)
    return {
        "id": node.element_id,
        "label": node_name(node),
        "group": label,
        "color": NODE_COLORS.get(label, "#888888"),
        "properties": dict(node),
    }


def add_node(nodes: dict, node) -> None:
    if node is None:
        return
    nid = node.element_id
    if nid not in nodes:
        nodes[nid] = serialize_node(node)


def add_link(links: list, seen: set, src, tgt, rel_type: str) -> None:
    if src is None or tgt is None:
        return
    key = (src.element_id, tgt.element_id, rel_type)
    if key in seen:
        return
    seen.add(key)
    links.append({"source": src.element_id, "target": tgt.element_id, "type": rel_type})


def build_graph_from_records(records) -> dict:
    nodes: dict[str, dict] = {}
    links: list[dict] = []
    seen_links: set[tuple] = set()

    for record in records:
        if "seed" in record:
            seed = record["seed"]
            add_node(nodes, seed)
            for rel_key, node_key in [("r1", "n1"), ("r2", "n2")]:
                rel = record.get(rel_key)
                other = record.get(node_key)
                if rel is not None:
                    add_node(nodes, rel.start_node)
                    add_node(nodes, rel.end_node)
                    add_link(links, seen_links, rel.start_node, rel.end_node, rel.type)
                add_node(nodes, other)
            continue

        for key in record.keys():
            val = record[key]
            if val is None or key in ("outgoing", "incoming"):
                continue
            if hasattr(val, "labels"):
                add_node(nodes, val)
            elif hasattr(val, "type") and hasattr(val, "start_node"):
                add_node(nodes, val.start_node)
                add_node(nodes, val.end_node)
                add_link(links, seen_links, val.start_node, val.end_node, val.type)

        if "c" in record.keys():
            for src_key, tgt_key, rel_type in GRAPH_RECORD_LINKS:
                add_link(links, seen_links, record.get(src_key), record.get(tgt_key), rel_type)

    return {"nodes": list(nodes.values()), "links": links}


def serialize_node_detail(record) -> dict:
    node = record["n"]
    base = serialize_node(node)
    related = []
    for bucket in ("outgoing", "incoming"):
        for item in record.get(bucket) or []:
            rel_node = item.get("node")
            if rel_node is None:
                continue
            related.append({
                "direction": item.get("direction"),
                "relation": item.get("rel"),
                "node": serialize_node(rel_node),
            })
    base["related"] = related
    return base
