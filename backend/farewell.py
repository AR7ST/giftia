# farewell.py — 送別ギフト検索（mode=farewell）の部品。
# DB 接続（database）と .env（dotenv）は読まない。DB に問い合わせる関数 fetch は、呼ぶ側（main.py）から渡す。

import re

PRICE_MAX_LIMIT = 1_000_000
RESULT_LIMIT = 10  # 返す最大件数

# 並びの「有効な評価」。rating_status() の valid と同じ条件
VALID_RATING_SQL = "rating BETWEEN 1 AND 5 AND review_count >= 1"

DETAIL_COLUMNS = (
    "product_id, category, brand, product_name, price, rating, review_count, "
    "sales_count, description, size, gift_wrap, message_card, delivery_days"
)

GIFT_WRAP_STAMP = {"label": "ギフト包装可", "type": "positive"}
KEYWORD_STAMPS = (
    ("個包装", {"label": "個包装の記載あり", "type": "info"}),
    ("常温", {"label": "常温保存の記載あり", "type": "info"}),
    ("香り", {"label": "香りあり（好み確認）", "type": "caution"}),
    ("甘い", {"label": "甘いもの（好み確認）", "type": "caution"}),
)
NEGATIONS = ("ない", "なく", "なし", "ません", "不可", "不要", "できず", "無し")
UNCERTAIN = ("一部", "場合", "可能性", "かも", "もあります", "もある", "？", "?")
CLAUSE_SPLIT = re.compile(r"[。！？!?\n、,，]")


def parse_price_max(value) -> int:
    """price_max を確かめる。1〜1,000,000 の整数だけ通す（外れたら ValueError）"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("price_max は整数で指定してください")
    if value < 1 or value > PRICE_MAX_LIMIT:
        raise ValueError(f"price_max は 1〜{PRICE_MAX_LIMIT} の範囲で指定してください")
    return value


def build_condition(q: str, price_max: int) -> tuple[str, list]:
    """WHERE の中身と params。値は %s で渡し、SQL の文字列に直接つなげない"""
    where, params = ["stock > 0", "price <= %s"], [price_max]
    for word in (q or "").split():
        where.append("(product_name LIKE %s OR brand LIKE %s OR description LIKE %s)")
        params += [f"%{word}%"] * 3
    return " AND ".join(where), params


def build_candidate_query(condition: str) -> str:
    """上位の商品IDを並び順どおりに取る。最後の %s は件数"""
    return (
        f"SELECT product_id FROM products WHERE {condition} "
        f"ORDER BY sales_count DESC, CASE WHEN {VALID_RATING_SQL} THEN rating END DESC, product_id "
        "LIMIT %s"
    )


def build_detail_query(count: int) -> str:
    placeholders = ", ".join(["%s"] * count)
    return f"SELECT {DETAIL_COLUMNS} FROM products WHERE product_id IN ({placeholders})"


def rating_status(rating, review_count) -> str:
    """valid / no_reviews / unknown / inconsistent。評価なしを 0 点にしない"""
    if rating is None:
        if review_count == 0:
            return "no_reviews"
        return "unknown"  # 件数あり・件数不明
    if review_count is None:
        return "unknown"  # 評価はあるが件数が分からない
    if 1 <= float(rating) <= 5 and review_count >= 1:
        return "valid"
    return "inconsistent"  # 評価はあるのに件数0、範囲外 など


def _keyword_state(text: str, word: str) -> str:
    """'yes'（言い切り）/ 'no'（出てこない）/ 'maybe'（否定・あいまい）"""
    found = False
    for clause in CLAUSE_SPLIT.split(text):
        pos = clause.find(word)
        while pos != -1:
            found = True
            before = clause[max(0, pos - 1):pos]
            tail = clause[pos:]
            if before == "非" or any(m in tail for m in NEGATIONS) or any(m in clause for m in UNCERTAIN):
                return "maybe"
            pos = clause.find(word, pos + 1)
    return "yes" if found else "no"


def make_stamps(gift_wrap, description) -> list[dict]:
    """gift_wrap=1 と説明文の語からスタンプを作る。否定文・迷うときは付けない"""
    stamps = []
    if gift_wrap == 1:
        stamps.append(dict(GIFT_WRAP_STAMP))
    if isinstance(description, str):
        for word, stamp in KEYWORD_STAMPS:
            if _keyword_state(description, word) == "yes":
                stamps.append(dict(stamp))
    return stamps


def to_flag(value):
    """1 → True、0 → False、それ以外・NULL → None"""
    if value is None or isinstance(value, bool):
        return value
    if value == 1:
        return True
    if value == 0:
        return False
    return None


def to_farewell_gift(r: dict) -> dict:
    """DB の行 → 応答の1件。null は null のまま返す（0 にしない）"""
    return {
        "id": r["product_id"],
        "category": r["category"],
        "brand": r["brand"],
        "name": r["product_name"],
        "price": r["price"],
        "rating": float(r["rating"]) if r["rating"] is not None else None,
        "reviewCount": r["review_count"],
        "salesCount": r["sales_count"],
        "description": r["description"],
        "size": r["size"],
        "giftWrap": to_flag(r["gift_wrap"]),
        "messageCard": to_flag(r["message_card"]),
        "deliveryDays": r["delivery_days"],
        "ratingStatus": rating_status(r["rating"], r["review_count"]),
        "stamps": make_stamps(r["gift_wrap"], r["description"]),
    }


def farewell_search(fetch, q: str, price_max) -> dict:
    """送別ギフト検索。fetch(sql, params) は行（dict）のリストを返す関数"""
    price_max = parse_price_max(price_max)
    condition, params = build_condition(q, price_max)

    total = fetch(f"SELECT COUNT(*) AS n FROM products WHERE {condition}", tuple(params))[0]["n"]
    candidates = fetch(build_candidate_query(condition), (*params, RESULT_LIMIT))
    ids = [row["product_id"] for row in candidates]
    if not ids:
        return {"total": total, "shown": 0, "results": []}

    rows = {r["product_id"]: r for r in fetch(build_detail_query(len(ids)), tuple(ids))}
    results = [to_farewell_gift(rows[i]) for i in ids if i in rows]
    return {"total": total, "shown": len(results), "results": results}
