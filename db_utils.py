import sqlite3
import os
from typing import Optional, Dict, Any
from datetime import datetime
from enum import IntEnum

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.DB_FOLDER = "data"
            self.DB_FILE = "model_state.db"
            self._init_database()
            self._initialized = True

    def _init_database(self):
        """Initialize the database and create necessary tables"""
        os.makedirs(self.DB_FOLDER, exist_ok=True)
        db_path = os.path.join(self.DB_FOLDER, self.DB_FILE)
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # models table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    model_id TEXT PRIMARY KEY,
                    download_status INTEGER CHECK(download_status IN (0,1,2)),
                    modified_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def _get_connection(self):
        """Get a database connection"""
        db_path = os.path.join(self.DB_FOLDER, self.DB_FILE)
        return sqlite3.connect(db_path)


class ModelsDAO:
    _instance = None

    class DownloadStatus(IntEnum):
        PENDING = -1
        DOWNLOADING = 0
        READY = 1

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.db_manager = DatabaseManager()
            self._initialized = True

    def get_model_state(self, model_id: str) -> dict:
        with self.db_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT download_status FROM models WHERE model_id = ?
            ''', (model_id,))
            result = cursor.fetchone()
            return result[0]

    def insert_model_state(self, model_id: str, status: DownloadStatus):
        with self.db_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO models (model_id, download_status) VALUES (?, ?)
            ''', (model_id, status.value))
            conn.commit()

    def update_model_state(self, model_id: str, status: DownloadStatus):
        with self.db_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE models SET download_status = ? WHERE model_id = ?
            ''', (status.value, model_id))
            conn.commit()

    def get_model_states(self, model_ids: list[str] | None = None) -> list[dict]:
        with self.db_manager._get_connection() as conn:
            cursor = conn.cursor()
            if model_ids is None:
                cursor.execute('''
                    SELECT model_id, download_status FROM models
                ''')
            else:
                cursor.execute('''
                    SELECT model_id, download_status FROM models WHERE model_id IN ({})
                '''.format(', '.join(['?'] * len(model_ids))), model_ids)
            data = cursor.fetchall()
            return [{"model_id": row[0], "download_status": row[1]} for row in data]

    def clear_model_states(self, model_ids: list[str] ):
        with self.db_manager._get_connection() as conn:
            cursor = conn.cursor()
            if len(model_ids) > 0:
                cursor.execute('''
                    DELETE FROM models WHERE model_id IN ({})
                '''.format(', '.join(['?'] * len(model_ids))), model_ids)
                conn.commit()
