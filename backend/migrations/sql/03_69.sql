-- 03：#69 商品の主キーを数字の id に移す（子の4表：order_items・product_scenes・reviews・product_facts）
-- いちばん慎重に行う。直前のバックアップがあることを確かめてから実行する
SELECT @@version;

-- 段階1：商品に数値IDを足す（主キーはまだ product_id のまま）
ALTER TABLE giftia_t503.products
    ADD COLUMN id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    ADD UNIQUE KEY uq_products_numeric_id (id),
    ADD UNIQUE KEY uq_products_product_code (product_id);

-- 段階2：子の4表に数値IDの列を足し、値を入れる
ALTER TABLE giftia_t503.order_items ADD COLUMN product_numeric_id BIGINT UNSIGNED NULL;
ALTER TABLE giftia_t503.product_scenes ADD COLUMN product_numeric_id BIGINT UNSIGNED NULL;
ALTER TABLE giftia_t503.reviews ADD COLUMN product_numeric_id BIGINT UNSIGNED NULL;
ALTER TABLE giftia_t503.product_facts ADD COLUMN product_numeric_id BIGINT UNSIGNED NULL;
SET SQL_SAFE_UPDATES = 0;
START TRANSACTION;
UPDATE giftia_t503.order_items AS c JOIN giftia_t503.products AS p ON p.product_id = c.product_id SET c.product_numeric_id = p.id;
UPDATE giftia_t503.product_scenes AS c JOIN giftia_t503.products AS p ON p.product_id = c.product_id SET c.product_numeric_id = p.id;
UPDATE giftia_t503.reviews AS c JOIN giftia_t503.products AS p ON p.product_id = c.product_id SET c.product_numeric_id = p.id;
UPDATE giftia_t503.product_facts AS c JOIN giftia_t503.products AS p ON p.product_id = c.product_id SET c.product_numeric_id = p.id;
COMMIT;
ALTER TABLE giftia_t503.order_items ADD CONSTRAINT fk_order_items_product_numeric FOREIGN KEY (product_numeric_id) REFERENCES giftia_t503.products (id);
ALTER TABLE giftia_t503.product_scenes ADD CONSTRAINT fk_product_scenes_product_numeric FOREIGN KEY (product_numeric_id) REFERENCES giftia_t503.products (id);
ALTER TABLE giftia_t503.reviews ADD CONSTRAINT fk_reviews_product_numeric FOREIGN KEY (product_numeric_id) REFERENCES giftia_t503.products (id);
ALTER TABLE giftia_t503.product_facts ADD CONSTRAINT fk_product_facts_product_numeric FOREIGN KEY (product_numeric_id) REFERENCES giftia_t503.products (id);

-- 段階3：主キーを id に切り替える（旧 product_id は一意索引で残る。今の外部キーもそのまま使える）
ALTER TABLE giftia_t503.products DROP PRIMARY KEY, ADD PRIMARY KEY (id);

-- 確かめる：最後の表がすべて「OK」なら次へ。1つでも「NG」なら、そこで止める
SELECT
  IF((SELECT COUNT(DISTINCT id) FROM giftia_t503.products) = (SELECT COUNT(*) FROM giftia_t503.products), 'OK', 'NG') AS idが全商品に1つずつ,
  IF((SELECT column_key FROM information_schema.columns WHERE table_schema = 'giftia_t503' AND table_name = 'products' AND column_name = 'id') = 'PRI', 'OK', 'NG') AS 主キーがid,
  IF((SELECT COUNT(*) FROM giftia_t503.order_items c LEFT JOIN giftia_t503.products p ON p.product_id = c.product_id WHERE NOT (c.product_numeric_id <=> p.id)) = 0, 'OK', 'NG') AS 注文明細の食い違い0,
  IF((SELECT COUNT(*) FROM giftia_t503.product_scenes c LEFT JOIN giftia_t503.products p ON p.product_id = c.product_id WHERE NOT (c.product_numeric_id <=> p.id)) = 0, 'OK', 'NG') AS シーンの食い違い0,
  IF((SELECT COUNT(*) FROM giftia_t503.reviews c LEFT JOIN giftia_t503.products p ON p.product_id = c.product_id WHERE NOT (c.product_numeric_id <=> p.id)) = 0, 'OK', 'NG') AS レビューの食い違い0,
  IF((SELECT COUNT(*) FROM giftia_t503.product_facts c LEFT JOIN giftia_t503.products p ON p.product_id = c.product_id WHERE NOT (c.product_numeric_id <=> p.id)) = 0, 'OK', 'NG') AS factsの食い違い0;
