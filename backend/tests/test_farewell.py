# farewell.py のテスト。main.py・database.py は読み込まない（.env を読むため）。
# DB は使わず、標準の sqlite3（メモリ上・架空データ）で SQL の絞り込みと並びを確かめる。
# 実行：backend フォルダで  python -B -m unittest discover -s tests

import os
import sqlite3
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import farewell  # noqa: E402


def make_fetch(products):
    """架空の商品を入れたメモリ上の DB を作り、fetch(sql, params) 風の関数を返す"""
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute(
        "CREATE TABLE products (product_id TEXT, category TEXT, brand TEXT, product_name TEXT, price INTEGER, "
        "rating REAL, review_count INTEGER, stock INTEGER, sales_count INTEGER, description TEXT, size TEXT, "
        "gift_wrap INTEGER, message_card INTEGER, delivery_days INTEGER)"
    )
    for p in products:
        row = {
            "category": "c1", "brand": "b", "product_name": "n", "price": 1000, "rating": None,
            "review_count": 0, "stock": 5, "sales_count": 0, "description": None, "size": None,
            "gift_wrap": None, "message_card": None, "delivery_days": None,
        }
        row.update(p)
        con.execute(
            "INSERT INTO products VALUES (:product_id, :category, :brand, :product_name, :price, :rating, "
            ":review_count, :stock, :sales_count, :description, :size, :gift_wrap, :message_card, :delivery_days)",
            row,
        )
    calls = []

    def fetch(sql, params=()):
        calls.append((sql, tuple(params)))
        return [dict(r) for r in con.execute(sql.replace("%s", "?"), tuple(params)).fetchall()]

    fetch.calls = calls
    return fetch


def ids(result):
    return [r["id"] for r in result["results"]]


class PriceMaxTest(unittest.TestCase):
    def test_valid_range(self):
        self.assertEqual(farewell.parse_price_max(1), 1)
        self.assertEqual(farewell.parse_price_max(1_000_000), 1_000_000)

    def test_invalid_values(self):
        for bad in (None, 0, -1, 1_000_001, "4500", 4500.5, True, [], "abc"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    farewell.parse_price_max(bad)

    def test_search_rejects_before_touching_db(self):
        fetch = make_fetch([])
        with self.assertRaises(ValueError):
            farewell.farewell_search(fetch, "", 0)
        self.assertEqual(fetch.calls, [])


class BudgetTest(unittest.TestCase):
    def test_boundary_4500_in_4501_out(self):
        fetch = make_fetch([
            {"product_id": "A", "price": 4500},
            {"product_id": "B", "price": 4501},
            {"product_id": "C", "price": 4499},
        ])
        result = farewell.farewell_search(fetch, "", 4500)
        self.assertEqual(sorted(ids(result)), ["A", "C"])
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["shown"], 2)

    def test_out_of_stock_excluded(self):
        fetch = make_fetch([
            {"product_id": "A", "stock": 0},
            {"product_id": "B", "stock": 1},
        ])
        self.assertEqual(ids(farewell.farewell_search(fetch, "", 5000)), ["B"])

    def test_values_go_through_params(self):
        fetch = make_fetch([{"product_id": "A"}])
        farewell.farewell_search(fetch, "茶 菓子", 4500)
        for sql, params in fetch.calls:
            self.assertNotIn("4500", sql)
            self.assertNotIn("茶", sql)
            self.assertIn(4500, params)
        self.assertIn("%茶%", fetch.calls[0][1])

    def test_keywords_all_required(self):
        fetch = make_fetch([
            {"product_id": "A", "product_name": "お茶セット", "description": "クッキー付き"},
            {"product_id": "B", "product_name": "お茶セット", "description": "なし"},
        ])
        self.assertEqual(ids(farewell.farewell_search(fetch, "お茶 クッキー", 5000)), ["A"])


class OrderAndDiversityTest(unittest.TestCase):
    def test_order_sales_then_valid_rating_then_id(self):
        fetch = make_fetch([
            {"product_id": "A", "category": "a", "sales_count": 10, "rating": 4.0, "review_count": 3},
            {"product_id": "B", "category": "b", "sales_count": 10, "rating": 4.5, "review_count": 3},
            {"product_id": "C", "category": "c", "sales_count": 10, "rating": 5.0, "review_count": 0},  # 不整合：有効な評価ではない
            {"product_id": "D", "category": "d", "sales_count": 10, "rating": None, "review_count": 0},
            {"product_id": "E", "category": "e", "sales_count": 50},
            {"product_id": "F", "category": "f", "sales_count": 10, "rating": 4.5, "review_count": 9},
        ])
        self.assertEqual(ids(farewell.farewell_search(fetch, "", 5000)), ["E", "B", "F", "A", "C", "D"])

    def test_max_three_per_category(self):
        products = [
            {"product_id": f"X{i}", "category": "x", "sales_count": 100 - i} for i in range(5)
        ] + [
            {"product_id": f"Y{i}", "category": "y", "sales_count": 10 - i} for i in range(5)
        ]
        result = farewell.farewell_search(make_fetch(products), "", 5000)
        self.assertEqual(ids(result), ["X0", "X1", "X2", "Y0", "Y1", "Y2"])
        self.assertEqual(result["total"], 10)
        self.assertEqual(result["shown"], 6)

    def test_max_ten_results(self):
        products = [
            {"product_id": f"P{i:02d}", "category": f"c{i % 5}", "sales_count": 100 - i} for i in range(30)
        ]
        result = farewell.farewell_search(make_fetch(products), "", 5000)
        self.assertEqual(result["shown"], 10)
        self.assertEqual(result["total"], 30)
        counts = {}
        for r in result["results"]:
            counts[r["category"]] = counts.get(r["category"], 0) + 1
        self.assertTrue(all(n <= 3 for n in counts.values()))

    def test_candidates_capped_at_500_and_detail_only_for_picked(self):
        products = [
            {"product_id": f"P{i:04d}", "category": f"c{i % 50}", "sales_count": 1000 - i} for i in range(600)
        ]
        fetch = make_fetch(products)
        result = farewell.farewell_search(fetch, "", 5000)
        self.assertEqual(result["total"], 600)
        self.assertEqual(fetch.calls[1][1][-1], 500)
        self.assertNotIn("description", fetch.calls[1][0])
        detail_sql, detail_params = fetch.calls[2]
        self.assertEqual(len(detail_params), 10)
        self.assertEqual(detail_sql.count("%s"), 10)

    def test_no_match(self):
        result = farewell.farewell_search(make_fetch([{"product_id": "A", "price": 9000}]), "", 100)
        self.assertEqual(result, {"total": 0, "shown": 0, "results": []})


class RatingStatusTest(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(farewell.rating_status(1, 1), "valid")
        self.assertEqual(farewell.rating_status(4.2, 10), "valid")
        self.assertEqual(farewell.rating_status(5, 1), "valid")

    def test_no_reviews(self):
        self.assertEqual(farewell.rating_status(None, 0), "no_reviews")

    def test_unknown(self):
        self.assertEqual(farewell.rating_status(None, 3), "unknown")
        self.assertEqual(farewell.rating_status(None, None), "unknown")

    def test_inconsistent(self):
        self.assertEqual(farewell.rating_status(4.0, 0), "inconsistent")
        self.assertEqual(farewell.rating_status(0, 5), "inconsistent")
        self.assertEqual(farewell.rating_status(5.5, 5), "inconsistent")
        self.assertEqual(farewell.rating_status(4.0, None), "inconsistent")


class StampTest(unittest.TestCase):
    def test_gift_wrap(self):
        self.assertEqual(farewell.make_stamps(1, None), ["ギフト包装可"])
        self.assertEqual(farewell.make_stamps(0, None), [])
        self.assertEqual(farewell.make_stamps(None, None), [])

    def test_keywords(self):
        self.assertEqual(
            farewell.make_stamps(None, "個包装で配りやすい。常温で保存できます。香りが良い。甘い味わい。"),
            ["個包装", "常温", "香り", "甘い"],
        )

    def test_negation_gets_no_stamp(self):
        for text in (
            "個包装ではありません",
            "個包装ではなく大袋です",
            "常温では配送できません",
            "香りはありません",
            "甘くはなく、甘いわけではない",
            "非個包装です",
            "個包装不可",
        ):
            with self.subTest(text=text):
                self.assertEqual(farewell.make_stamps(None, text), [])

    def test_uncertain_gets_no_stamp(self):
        for text in ("一部の商品は個包装です", "個包装の場合があります", "個包装かもしれません"):
            with self.subTest(text=text):
                self.assertEqual(farewell.make_stamps(None, text), [])

    def test_negation_in_other_clause_does_not_block(self):
        self.assertEqual(farewell.make_stamps(None, "個包装ではありませんが、甘い味です"), ["甘い"])

    def test_negated_wrap_keeps_gift_wrap_stamp(self):
        self.assertEqual(farewell.make_stamps(1, "個包装ではありません"), ["ギフト包装可"])

    def test_non_string_description(self):
        self.assertEqual(farewell.make_stamps(None, None), [])


class ResponseShapeTest(unittest.TestCase):
    def test_fields_and_nulls_kept(self):
        fetch = make_fetch([{"product_id": "A", "description": "個包装です", "gift_wrap": 1}])
        result = farewell.farewell_search(fetch, "", 5000)
        item = result["results"][0]
        self.assertEqual(
            set(item),
            {
                "id", "category", "brand", "name", "price", "rating", "reviewCount", "salesCount", "description",
                "size", "giftWrap", "messageCard", "deliveryDays", "ratingStatus", "stamps",
            },
        )
        self.assertIsNone(item["rating"])
        self.assertIsNone(item["size"])
        self.assertIsNone(item["messageCard"])
        self.assertIsNone(item["deliveryDays"])
        self.assertEqual(item["giftWrap"], 1)
        self.assertEqual(item["ratingStatus"], "no_reviews")
        self.assertEqual(item["stamps"], ["ギフト包装可", "個包装"])
        self.assertEqual(set(result), {"total", "shown", "results"})


if __name__ == "__main__":
    unittest.main()
