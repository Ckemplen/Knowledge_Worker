import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import core.config as config

Base = declarative_base()

engine = create_engine(f"sqlite:///{config.DATABASE_PATH}", echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

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
        text TEXT,
        html_text TEXT,
        version INTEGER NOT NULL DEFAULT 1,
        previous_version_id INTEGER,
        last_modified_at DATETIME,
        last_modified_by DATETIME,
        created_at DATETIME,
        created_by DATETIME,
        processed_at DATETIME,
        summary TEXT,
        version_comment TEXT,
        revision INTEGER DEFAULT 1,
        UNIQUE (filepath, version),
        FOREIGN KEY (previous_version_id) REFERENCES Documents(id)
        );

        CREATE TABLE Comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        author TEXT,
        reference_text TEXT,
        comment_text TEXT,
        comment_date DATETIME,
        FOREIGN KEY (document_id) REFERENCES Documents(id)
        );

        CREATE TABLE RawTopics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        topic_name TEXT,
        topic_description TEXT,
        topic_prevalence INTEGER
        );

        CREATE TABLE Topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_name TEXT,
        topic_description TEXT
        );

        CREATE TABLE DocumentTopics (
        document_id INTEGER NOT NULL,
        topic_id INTEGER NOT NULL,
        PRIMARY KEY (document_id, topic_id),
        FOREIGN KEY (document_id) REFERENCES Documents(id),
        FOREIGN KEY (topic_id) REFERENCES Topics(id)
        );

        CREATE TABLE TopicsRawTopics (
        topic_id INTEGER NOT NULL,
        raw_topic_id INTEGER NOT NULL,
        PRIMARY KEY (topic_id, raw_topic_id),
        FOREIGN KEY (topic_id) REFERENCES Topics(id),
        FOREIGN KEY (raw_topic_id) REFERENCES RawTopics(id)
        );

        CREATE TABLE RawEntities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        entity_name TEXT,
        entity_description TEXT,
        entity_prevalence INTEGER
        );

        CREATE TABLE Entities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_name TEXT,
        entity_description TEXT
        );

        CREATE TABLE DocumentEntities (
        document_id INTEGER NOT NULL,
        entity_id INTEGER NOT NULL,
        PRIMARY KEY (document_id, entity_id),
        FOREIGN KEY (document_id) REFERENCES Documents(id),
        FOREIGN KEY (entity_id) REFERENCES Entities(id)
        );

        CREATE TABLE EntitiesRawEntities (
        entity_id INTEGER NOT NULL,
        raw_entity_id INTEGER NOT NULL,
        PRIMARY KEY (entity_id, raw_entity_id),
        FOREIGN KEY (entity_id) REFERENCES Entities(id),
        FOREIGN KEY (raw_entity_id) REFERENCES RawEntities(id)
        );

        """
        cursor.executescript(sql_script)

        conn.commit()
        print("Database and tables created successfully!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        conn.close()

