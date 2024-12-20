import os
import sqlite3

DATABASE_PATH = r"C:\Users\ckemplen\POLICY_DEVELOPMENT_APP\db.sqlite"

def create_database(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

    
        sql_script = """
        CREATE TABLE  Documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filepath TEXT NOT NULL,
        filename TEXT NOT NULL,
        filetype TEXT,
        version INTEGER NOT NULL DEFAULT 1,
        previous_version_id INTEGER,
        last_modified_at DATETIME,
        last_modified_by DATETIME,
        created_at DATETIME,
        created_by DATETIME,
        processed_at DATETIME,
        summary TEXT,
        version_comment TEXT,
        UNIQUE (filepath, version),
        FOREIGN KEY (previous_version_id) REFERENCES Documents(id)
        );

        CREATE TABLE Comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        author TEXT,
        comment_text TEXT,
        comment_date DATETIME,
        FOREIGN KEY (document_id) REFERENCES Documents(id)
        );

        """
        cursor.executescript(sql_script)

        conn.commit()
        print("Database and tables created successfully!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        conn.close()

create_database(DATABASE_PATH)