import os

from dotenv import load_dotenv
from pyTigerGraph import TigerGraphConnection

load_dotenv()


def create_schema():
    conn = TigerGraphConnection(
        host=os.getenv("TG_GSQL_HOST", "http://localhost"),
        graphname="",
        username=os.getenv("TG_USERNAME", "tigergraph"),
        password=os.getenv("TG_PASSWORD", "tigergraph"),
        restppPort=os.getenv("TG_RESTPP_PORT", "9000"),
        gsPort=os.getenv("TG_GSQL_PORT", "14240"),
    )

    graph = os.getenv("TG_GRAPH", "graphrag_benchmark")

    commands = [
        """
CREATE VERTEX BenchDocument (
  PRIMARY_ID doc_id STRING,
  title STRING
) WITH primary_id_as_attribute="true"
""",
        """
CREATE VERTEX BenchChunk (
  PRIMARY_ID chunk_id STRING,
  text STRING
) WITH primary_id_as_attribute="true"
""",
        """
CREATE VERTEX BenchEntity (
  PRIMARY_ID entity_id STRING,
  name STRING,
  entity_type STRING
) WITH primary_id_as_attribute="true"
""",
        "CREATE UNDIRECTED EDGE BenchHasChunk (FROM BenchDocument, TO BenchChunk)",
        "CREATE UNDIRECTED EDGE BenchMentions (FROM BenchChunk, TO BenchEntity)",
        "CREATE UNDIRECTED EDGE BenchRelated (FROM BenchEntity, TO BenchEntity)",
        f"CREATE GRAPH {graph} (BenchDocument, BenchChunk, BenchEntity, BenchHasChunk, BenchMentions, BenchRelated)",
    ]

    output = []
    for command in commands:
        try:
            result = conn.gsql(command)
        except Exception as exc:
            message = str(exc)
            if "already exists" not in message and "existed" not in message:
                raise
            result = message
        output.append(result)

    return "\n".join(output)


if __name__ == "__main__":
    print(create_schema())
