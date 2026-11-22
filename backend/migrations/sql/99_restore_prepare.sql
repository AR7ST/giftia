-- 99：元に戻すときの準備（「NG」が出て止めたときだけ使う。ふだんは実行しない）
-- giftia_t503 の中の表とビューを、すべて消す。そのあと、直前に取ったバックアップのファイルを読み込むと、実行前の状態に戻る
-- （新しくできた表へのつながりが残っていると、バックアップから表を作り直せないため、元からある表も消す）
-- ★ 必ず、直前のバックアップのファイルがあることを確かめてから実行する
SELECT @@version;
SET FOREIGN_KEY_CHECKS = 0;
DROP VIEW IF EXISTS giftia_t503.product_rating_summary;
DROP TABLE IF EXISTS giftia_t503.product_attributes, giftia_t503.product_price_histories,
    giftia_t503.categories, giftia_t503.brands,
    giftia_t503.order_items, giftia_t503.orders, giftia_t503.product_facts, giftia_t503.product_scenes,
    giftia_t503.products, giftia_t503.reviews, giftia_t503.users;
SET FOREIGN_KEY_CHECKS = 1;
SELECT COUNT(*) AS 残っている表の数 FROM information_schema.tables WHERE table_schema = 'giftia_t503';
