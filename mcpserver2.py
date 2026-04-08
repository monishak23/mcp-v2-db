import json
import sys

from mcp.server.fastmcp import FastMCP
from database import excute_query

mcp = FastMCP("MCP server to connect database")

@mcp.tool()
def insert_record(table: str, columns: str, values: str):
    """
    Inserts a new row into the database.

    FOR THE 'todos' TABLE:
    - Use column 'name' for the task description.
    - Use column 'status' for the task state.

    Example: table='todos', columns='name, status', values='learn python, inprogress'
    """

    print("[DEBUG] FUNCTION CALLED")
    col_list = [c.strip() for c in columns.split(",")]
    val_list = [v.strip() for v in values.split(",")]
    col_str = ", ".join(col_list)
    placeholders = ", ".join(["%s"] * len(val_list))
    query = f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})"
    excute_query(query, val_list, False)
    return "Inserted successfully"

@mcp.tool()
def get_records(table: str):
    """List or show all records in the todos database."""
    # print("[DEBUG] FUNCTION CALLED",  file=sys.stderr)
    query =f"SELECT * FROM {table}"
    response = excute_query(query, None, True)
    # print(response,  file=sys.stderr)
    return json.dumps(response, indent=2)

@mcp.tool()
def delete_record(table: str, id: int):
    query = f"DELETE FROM {table} WHERE id = %s"
    excute_query(query, (id, ), False)
    return "Deleted successfully"


mcp.run()