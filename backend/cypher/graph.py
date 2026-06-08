"""Cypher queries for graph API."""

GRAPH_QUERY = """
MATCH (p2:Poet)-[:REPRESENT]->(c:Cipai)
WHERE c.type IS NOT NULL
  AND ($period IS NULL OR EXISTS {
    MATCH (p2)-[:ACTIVE_IN]->(:Period {name: $period})
  })
OPTIONAL MATCH (c)-[:HAS_ALIAS]->(a:Alias)
OPTIONAL MATCH (w:Work)-[:USES_CIPAI]->(c)
OPTIONAL MATCH (p:Poet)-[:WROTE]->(w)
OPTIONAL MATCH (c)-[:ACCOMPANIED_BY]->(i:Instrument)
OPTIONAL MATCH (p2)-[:BELONGS_TO]->(s:CiStyle)
OPTIONAL MATCH (p2)-[:ACTIVE_IN]->(per:Period)
RETURN c, a, w, p, p2, i, s, per
LIMIT $limit
"""

SEARCH_QUERY = """
CALL {
  MATCH (p:Poet)
  WHERE p.name CONTAINS $q
  RETURN p AS seed
  UNION
  MATCH (c:Cipai)
  WHERE c.name CONTAINS $q OR c.alias CONTAINS $q
  RETURN c AS seed
  UNION
  MATCH (a:Alias)
  WHERE a.name CONTAINS $q
  RETURN a AS seed
  UNION
  MATCH (i:Instrument)
  WHERE i.name CONTAINS $q
  RETURN i AS seed
}
WITH DISTINCT seed
OPTIONAL MATCH (seed)-[r1]->(n1)
OPTIONAL MATCH (n2)-[r2]->(seed)
RETURN seed, r1, n1, r2, n2
LIMIT $limit
"""

NODE_DETAIL_QUERY = """
MATCH (n)
WHERE elementId(n) = $node_id
OPTIONAL MATCH (n)-[r1]->(out)
OPTIONAL MATCH (in_node)-[r2]->(n)
RETURN n,
       collect(DISTINCT {rel: type(r1), node: out, direction: 'out'}) AS outgoing,
       collect(DISTINCT {rel: type(r2), node: in_node, direction: 'in'}) AS incoming
"""

TIMELINE_QUERY = """
MATCH (p:Poet)-[:ACTIVE_IN]->(per:Period)
RETURN per.name AS period, count(DISTINCT p) AS count
ORDER BY
  CASE per.name
    WHEN '唐五代' THEN 1
    WHEN '北宋' THEN 2
    WHEN '南宋' THEN 3
    WHEN '宋末' THEN 4
    ELSE 5
  END
"""

CONTEXT_QUERY = """
MATCH (ctx:Context {title: '南宋声乐背景'})
RETURN ctx.content AS content
LIMIT 1
"""
