import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "grocery_recipe.db"

tables = [
    "recipes",
    "grocery_lists",
    "grocery_items",
    "pantry_items",
    "meal_plans",
]

def has_column(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info('{table}')")
    cols = [r[1] for r in cur.fetchall()]
    return column in cols

def add_column(conn, table, column_sql):
    print(f"Altering {table}: adding {column_sql}")
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_sql}")

def main():
    if not DB_PATH.exists():
        print(f"DB not found at {DB_PATH}, nothing to do.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        for t in tables:
            if not has_column(conn, t, "user_id"):
                add_column(conn, t, "user_id INTEGER")
            else:
                print(f"{t} already has user_id")
        conn.commit()
        print("Done")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
