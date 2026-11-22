# search_sql.py — 通常検索と送別検索で共通に使う SQL の部品（PC での試し：#63・#68）
# DB 接続（database）と .env（dotenv）は読まない。

import re

# 全文検索（#68）を使うか。テスト（sqlite）では MATCH が使えないので False にする
FULLTEXT_ENABLED = True
_HAS_ASCII_LETTER = re.compile(r"[A-Za-z]")

# 商品からカテゴリ・ブランドのマスタを ID で左結合する（#63）。マスタ名を category / brand として返す
MASTER_JOIN = "LEFT JOIN categories c ON c.id = p.category_id LEFT JOIN brands b ON b.id = p.brand_id"
CATEGORY_NAME = "COALESCE(c.name, p.category)"
BRAND_NAME = "COALESCE(b.name, p.brand)"

# 画面に出す追加の列：税区分（#70）、数量・単位（#67）、保存方法（#65）
EXTRA_COLUMNS = "p.tax_category, p.quantity_value, p.quantity_unit, p.storage_method"


def extra_fields(r: dict) -> dict:
    """DB の行 → 応答に足す項目。値がなければ null のまま返す"""
    q = r.get("quantity_value")
    return {
        "taxCategory": r.get("tax_category"),
        "quantityValue": float(q) if q is not None else None,
        "quantityUnit": r.get("quantity_unit"),
        "storageMethod": r.get("storage_method"),
    }


def keyword_condition(word: str, alias: str = "") -> tuple[str, list]:
    """1語ぶんの WHERE と params。値は %s で渡す。

    2文字以上で英字を含まない語は全文検索（ngram）。1文字の語と英字を含む語は、
    全文検索と結果が同じにならない（1文字は当たらない・英字は大文字小文字を区別しない）ので、従来の LIKE を使う。
    """
    a = alias
    phrase = word.replace('"', "")
    if FULLTEXT_ENABLED and len(phrase) >= 2 and not _HAS_ASCII_LETTER.search(phrase):
        return (
            f"MATCH({a}product_name, {a}brand, {a}description) AGAINST (%s IN BOOLEAN MODE)",
            [f'"{phrase}"'],
        )
    return f"({a}product_name LIKE %s OR {a}brand LIKE %s OR {a}description LIKE %s)", [f"%{word}%"] * 3
