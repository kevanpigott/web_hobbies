import argparse
import sqlite3
from pathlib import Path

import pandas as pd


def delete_db(directory):
    db_path = Path(directory)
    db_files = list(db_path.glob("*.db"))

    if not db_files:
        print(f"No database files found in '{directory}'.")
        return

    for db_file in db_files:
        if db_file.is_file():
            db_file.unlink()
            print(f"Database '{db_file}' deleted successfully.")
        else:
            print(f"'{db_file}' is not a valid database file.")


def export_db_to_excel(directory, output_file):
    db_path = Path(directory) / "users.db"
    if not db_path.exists() or not db_path.is_file():
        print(f"Database '{db_path}' does not exist.")
        return

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Get the list of tables
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)

    # Write each table to a separate sheet in the Excel file
    with pd.ExcelWriter(output_file) as writer:
        for table_name in tables["name"]:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            df.to_excel(writer, sheet_name=table_name, index=False)

        # Export users with their hobbies
        users_hobbies_query = """
        SELECT u.id as user_id, u.username, h.id as hobby_id, h.name as hobby_name
        FROM user u
        LEFT JOIN hobby h ON u.id = h.user_id
        """
        users_hobbies = pd.read_sql_query(users_hobbies_query, conn)
        users_hobbies.to_excel(writer, sheet_name="Users_Hobbies", index=False)

    print(f"Database exported to '{output_file}' successfully.")

    # Close the connection
    conn.close()


def export_db_to_excel_old(directory, output_file):
    db_path = Path(directory) / "users.db"
    if not db_path.exists() or not db_path.is_file():
        print(f"Database '{db_path}' does not exist.")
        return

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Get the list of tables
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)

    # Write each table to a separate sheet in the Excel file
    with pd.ExcelWriter(output_file) as writer:
        for table_name in tables["name"]:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            df.to_excel(writer, sheet_name=table_name, index=False)

    print(f"Database exported to '{output_file}' successfully.")

    # Close the connection
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helper script for managing the database.")
    parser.add_argument(
        "--delete-db", type=str, help="Path to the directory containing the database file."
    )
    parser.add_argument(
        "--export-db",
        type=str,
        nargs=2,
        help="Path to the directory containing the database file and the output Excel file.",
    )

    args = parser.parse_args()

    if args.delete_db:
        delete_db(args.delete_db)
    elif args.export_db:
        export_db_to_excel(args.export_db[0], args.export_db[1])
