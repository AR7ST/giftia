# main.py の通常検索で「個包装」を指定したときのテスト（#88・#66）。
# .env と本物の DB は使わない。database は偽物に差し替え、標準の sqlite3（メモリ上・架空データ）で SQL を確かめる。
# 実行：backend フォルダで  python -B -m unittest discover -s tests

import importlib.util
import sqlite3
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


def load_main_module():
    """database（.env を読む）を偽物にして main.py を読み込む"""
    fake_database = types.ModuleType("database")
    fake_database.fetch_all = lambda sql, params=(): []
    path = Path(__file__).resolve().parents[1] / "main.py"
    spec = importlib.util.spec_from_file_location("giftia_test_main", path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"database": fake_database}), patch("dotenv.load_dotenv"):
        spec.loader.exec_module(module)
    return module


def make_fetch(products):
    """架空の商品を入れたメモリ上の DB を作り、fetch_all 風の関数を返す"""
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute(
        "CREATE TABLE products (product_id TEXT, category TEXT, brand TEXT, product_name TEXT, price INTEGER, "
        "rating REAL, review_count INTEGER, stock INTEGER, sales_count INTEGER, description TEXT, "
        "is_individually_wrapped INTEGER)"
    )
    for p in products:
        row = {"category": "c1", "brand": "b", "product_name": "n", "price": 1000, "rating": None,
               "review_count": 0, "stock": 5, "sales_count": 0, "description": "",
               "is_individually_wrapped": None}
        row.update(p)
        con.execute(
            "INSERT INTO products VALUES (:product_id, :category, :brand, :product_name, :price, :rating, "
            ":review_count, :stock, :sales_count, :description, :is_individually_wrapped)",
            row,
        )

    def fetch(sql, params=()):
        return [dict(r) for r in con.execute(sql.replace("%s", "?"), tuple(params)).fetchall()]

    return fetch


class SearchIndivWrapTest(unittest.TestCase):
    def setUp(self):
        self.main = load_main_module()
        products = [
            {"product_id": "T1", "description": "【個包装】あり", "sales_count": 3, "is_individually_wrapped": 1},
            {"product_id": "T2", "description": "【個包装】なし", "sales_count": 2, "is_individually_wrapped": 0},
            {"product_id": "T3", "description": "個包装でお届け", "sales_count": 1},  # 値がない（NULL）
            {"product_id": "T4", "description": "【包装】1個ずつ小袋入り", "sales_count": 0,
             "is_individually_wrapped": 1},
        ]
        self.main.fetch_all = make_fetch(products)

    def search(self, indiv_wrap):
        return self.main.search(q="", category="", indiv_wrap=indiv_wrap, price_min=None,
                                price_max=None, limit=20, mode="")

    def test_indiv_wrap_uses_column(self):
        result = self.search(True)
        ids = [g["id"] for g in result["results"]]
        # 「【個包装】なし」（T2）と、値がない商品（T3）は出ない。説明文に文字がなくても列が1なら出る（T4）
        self.assertEqual(ids, ["T1", "T4"])
        self.assertEqual(result["total"], 2)

    def test_without_indiv_wrap_returns_all(self):
        result = self.search(False)
        self.assertEqual(result["total"], 4)


if __name__ == "__main__":
    unittest.main()
