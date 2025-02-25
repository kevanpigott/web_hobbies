import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from helpers import hobby_similarity
from user_db import DbManager


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
    db_path = Path(directory) / DbManager.FILE_NAME
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


def calculate_all_hobby_relations():
    db_path = Path("instance") / DbManager.FILE_NAME
    if not db_path.exists() or not db_path.is_file():
        print(f"Database '{db_path}' does not exist.")
        return

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # get list of hobbies
    hobbies = pd.read_sql_query("SELECT id, name FROM hobby", conn).values

    for h1_id, h1_name in hobbies:
        for h2_id, h2_name in hobbies:
            if h1_id <= h2_id:
                continue

            similarity = hobby_similarity(h1_name, h2_name)

            # save the similarity score in the database in hobby_relations table
            conn.execute(
                "INSERT INTO hobby_relation (hobby_id1, hobby_id2, similarity) VALUES (?, ?, ?)",
                (h1_id, h2_id, similarity),
            )

    conn.commit()
    conn.close()


def import_excel_to_db(directory, input_file):
    db_path = Path(directory) / DbManager.FILE_NAME
    if not db_path.exists() or not db_path.is_file():
        print(f"Database '{db_path}' does not exist.")
        return

    input_file = Path(input_file)
    if not input_file.exists() or not input_file.is_file():
        print(f"Excel file '{input_file}' does not exist.")
        return

    # open the excel file
    df = pd.read_excel(input_file, sheet_name=None)

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Write each sheet to a separate table in the database
    for table_name, data in df.items():
        data.to_sql(table_name, conn, if_exists="append", index=False)

    print(f"Excel file imported to '{db_path}' successfully.")

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
    parser.add_argument(
        "--import-db",
        type=str,
        nargs=2,
        help="Path to the directory containing the database file and the input Excel file.",
    )
    parser.add_argument(
        "--calculate-all-hobby-relations",
        action="store_true",
        help="Calculate the similarity score between all hobbies.",
    )

    args = parser.parse_args()

    if args.delete_db:
        delete_db(args.delete_db)
    elif args.export_db:
        export_db_to_excel(args.export_db[0], args.export_db[1])
    elif args.import_db:
        import_excel_to_db(args.import_db[0], args.import_db[1])
    elif args.calculate_all_hobby_relations:
        calculate_all_hobby_relations()
