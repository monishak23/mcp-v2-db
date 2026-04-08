import sys

import mysql.connector
import os

def excute_query(query: str, params: tuple, fetch: bool):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="javadbms",
        database="activity_logs"
    )

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()
            # print(f"[DEBUG] result: {result}",  file=sys.stderr)
            return result
        else:
            conn.commit()
            return cursor.rowcount
    finally:
        cursor.close()
        conn.close()

