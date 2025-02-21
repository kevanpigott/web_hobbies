import argparse
from pathlib import Path

import pandas as pd

from user_db import db


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

    # Connect to the database
    db_uri = f"sqlite:///{db_path}"
    db.engine.dispose()
    db.init_app(db_uri)

    # Query the data
    users = pd.read_sql_table("user", db.engine)
    hobbies = pd.read_sql_table("hobby", db.engine)

    # Write to Excel
    with pd.ExcelWriter(output_file) as writer:
        users.to_excel(writer, sheet_name="Users", index=False)
        hobbies.to_excel(writer, sheet_name="Hobbies", index=False)

    print(f"Database exported to '{output_file}' successfully.")


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
