import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

import pymysql


def load_database_module():
    path = Path(__file__).resolve().parents[1] / "database.py"
    spec = importlib.util.spec_from_file_location("giftia_test_database", path)
    module = importlib.util.module_from_spec(spec)
    with patch("dotenv.load_dotenv"):
        spec.loader.exec_module(module)
    return module


class ConnectionPoolTest(unittest.TestCase):
    def setUp(self):
        self.database = load_database_module()
        self.addCleanup(self.close_pool)
        settings = patch.dict(os.environ, {
            "DB_HOST": "example.invalid",
            "DB_USER": "test",
            "DB_PASSWORD": "test",
            "DB_NAME": "test",
        }, clear=True)
        self.addCleanup(settings.stop)
        settings.start()

    def close_pool(self):
        if self.database._pool is not None:
            self.database._pool.close()

    def test_fetch_reuses_connection_and_returns_rows(self):
        connection = MagicMock()
        cursor = connection.cursor.return_value
        cursor.fetchall.return_value = [{"value": 1}]
        with patch.object(pymysql, "connect", return_value=connection) as connect:
            self.assertEqual(self.database.fetch_all("SELECT %s", (1,)), [{"value": 1}])
            self.assertEqual(self.database.fetch_all("SELECT %s", (1,)), [{"value": 1}])
        connect.assert_called_once()
        cursor.execute.assert_called_with("SELECT %s", (1,))
        self.assertEqual(cursor.close.call_count, 2)

    def test_query_failure_returns_connection_to_pool(self):
        connection = MagicMock()
        cursor = connection.cursor.return_value
        cursor.execute.side_effect = [ValueError("query failed"), None]
        cursor.fetchall.return_value = []
        with patch.object(pymysql, "connect", return_value=connection) as connect:
            with self.assertRaisesRegex(ValueError, "query failed"):
                self.database.fetch_all("SELECT 1")
            self.assertEqual(self.database.fetch_all("SELECT 1"), [])
        connect.assert_called_once()
        self.assertEqual(cursor.close.call_count, 2)

    def test_idle_timeout_replaces_connection(self):
        expired = MagicMock()
        replacement = MagicMock()
        expired.ping.side_effect = pymysql.OperationalError(2006, "connection expired")
        expired.cursor.return_value.fetchall.return_value = [{"value": 1}]
        replacement.cursor.return_value.fetchall.return_value = [{"value": 2}]
        with patch.object(pymysql, "connect", side_effect=[expired, replacement]) as connect:
            self.assertEqual(self.database.fetch_all("SELECT 1"), [{"value": 1}])
            self.assertEqual(self.database.fetch_all("SELECT 2"), [{"value": 2}])
        self.assertEqual(connect.call_count, 2)
        expired.close.assert_called_once()
