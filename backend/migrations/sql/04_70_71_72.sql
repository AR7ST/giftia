-- 04：#70（税区分・価格履歴）・#71（生年・監査列・状態）・#72（属性表・評価の集計）
-- 実行の前に：右上の接続名を確かめる。本番は @@version が 8.4.9
SELECT @@version;
SET SQL_SAFE_UPDATES = 0;

-- ===== #70 税区分と価格履歴 =====
ALTER TABLE giftia_t503.products ADD COLUMN tax_category ENUM('standard_10', 'reduced_8') NULL;
CREATE TABLE giftia_t503.product_price_histories (
    product_id BIGINT UNSIGNED NOT NULL,
    effective_from DATETIME(6) NOT NULL,
    effective_to DATETIME(6) NULL,
    price BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (product_id, effective_from),
    CONSTRAINT fk_price_history_product FOREIGN KEY (product_id) REFERENCES giftia_t503.products (id),
    CONSTRAINT chk_price_history_period CHECK (effective_to IS NULL OR effective_to > effective_from)
) ENGINE=InnoDB;
START TRANSACTION;
-- 仮：カテゴリから決める（食品・飲料は軽減税率8%、ほかは10%。酒類も10%）
UPDATE giftia_t503.products p JOIN giftia_t503.categories c ON c.id = p.category_id
  SET p.tax_category = IF(c.name IN ('食品', '飲料'), 'reduced_8', 'standard_10');
-- 初回は今の価格を、切り替えた時刻（UTC）から登録する
SET @switch_at = UTC_TIMESTAMP(6);
INSERT INTO giftia_t503.product_price_histories (product_id, effective_from, effective_to, price)
  SELECT id, @switch_at, NULL, price FROM giftia_t503.products;
COMMIT;

-- ===== #71 生年・監査列・状態 =====
ALTER TABLE giftia_t503.users
    ADD COLUMN birth_year SMALLINT UNSIGNED NULL,
    ADD COLUMN recorded_at DATETIME(6) NULL,
    ADD COLUMN birth_year_is_estimated BOOLEAN NULL,
    ADD CONSTRAINT chk_users_birth_year_metadata CHECK (
        (birth_year IS NULL AND recorded_at IS NULL AND birth_year_is_estimated IS NULL)
        OR (birth_year IS NOT NULL AND recorded_at IS NOT NULL
            AND birth_year_is_estimated IS NOT NULL AND birth_year_is_estimated IN (0, 1)));
-- 監査列：元からある7表すべてに足す（旧行は根拠がないので NULL）
ALTER TABLE giftia_t503.products ADD COLUMN created_at DATETIME(6) NULL, ADD COLUMN updated_at DATETIME(6) NULL, ADD COLUMN updated_by VARCHAR(128) NULL;
ALTER TABLE giftia_t503.users ADD COLUMN created_at DATETIME(6) NULL, ADD COLUMN updated_at DATETIME(6) NULL, ADD COLUMN updated_by VARCHAR(128) NULL;
ALTER TABLE giftia_t503.orders ADD COLUMN created_at DATETIME(6) NULL, ADD COLUMN updated_at DATETIME(6) NULL, ADD COLUMN updated_by VARCHAR(128) NULL;
ALTER TABLE giftia_t503.order_items ADD COLUMN created_at DATETIME(6) NULL, ADD COLUMN updated_at DATETIME(6) NULL, ADD COLUMN updated_by VARCHAR(128) NULL;
ALTER TABLE giftia_t503.reviews ADD COLUMN created_at DATETIME(6) NULL, ADD COLUMN updated_at DATETIME(6) NULL, ADD COLUMN updated_by VARCHAR(128) NULL;
ALTER TABLE giftia_t503.product_scenes ADD COLUMN created_at DATETIME(6) NULL, ADD COLUMN updated_at DATETIME(6) NULL, ADD COLUMN updated_by VARCHAR(128) NULL;
ALTER TABLE giftia_t503.product_facts ADD COLUMN created_at DATETIME(6) NULL, ADD COLUMN updated_at DATETIME(6) NULL, ADD COLUMN updated_by VARCHAR(128) NULL;
-- 販売・注文の状態
ALTER TABLE giftia_t503.products ADD COLUMN status ENUM('active', 'inactive') NULL;
ALTER TABLE giftia_t503.orders ADD COLUMN order_status VARCHAR(32) NULL;
START TRANSACTION;
-- 今の検索で公開している商品（全商品）を active にする。非公開と確認できる商品はない
UPDATE giftia_t503.products SET status = 'active';
COMMIT;

-- ===== #72 型別の属性表と評価の集計 =====
CREATE TABLE giftia_t503.product_attributes (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT UNSIGNED NOT NULL,
    fact_key VARCHAR(64) NOT NULL,
    unit VARCHAR(24) NULL,
    bool_value TINYINT NULL,
    int_value BIGINT NULL,
    text_value VARCHAR(255) NULL,
    UNIQUE KEY uq_product_attribute (product_id, fact_key),
    CONSTRAINT fk_product_attribute_product FOREIGN KEY (product_id) REFERENCES giftia_t503.products (id),
    CONSTRAINT chk_product_attribute_value CHECK (
        ((bool_value IS NOT NULL) + (int_value IS NOT NULL) + (text_value IS NOT NULL)) = 1
        AND (bool_value IS NULL OR bool_value IN (0, 1))
        AND (unit IS NULL OR int_value IS NOT NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_ja_0900_as_cs;
START TRANSACTION;
-- product_facts を型ごとに移す：はい/いいえ → bool_value、日数・件数 → int_value と単位
INSERT INTO giftia_t503.product_attributes (product_id, fact_key, unit, bool_value, int_value)
  SELECT f.product_numeric_id, f.fact,
         CASE f.fact WHEN 'shelf_life_days' THEN 'day' WHEN 'office_orders' THEN 'order' END,
         IF(f.fact IN ('indiv_wrap', 'room_temp'), f.value, NULL),
         IF(f.fact IN ('indiv_wrap', 'room_temp'), NULL, f.value)
  FROM giftia_t503.product_facts f;
COMMIT;
-- 評価は reviews から同じ条件で計算する（0件は NULL）。丸める前の合計と件数を持つ
CREATE VIEW giftia_t503.product_rating_summary AS
  SELECT p.id AS product_id, p.product_id AS product_code,
         COUNT(r.review_id) AS review_count,
         SUM(r.rating) AS rating_sum,
         IF(COUNT(r.review_id) = 0, NULL, SUM(r.rating) / COUNT(r.review_id)) AS rating_avg
  FROM giftia_t503.products p
  LEFT JOIN giftia_t503.reviews r ON r.product_numeric_id = p.id AND r.rating BETWEEN 1 AND 5
  GROUP BY p.id, p.product_id;
-- 確かめる：最後の表がすべて「OK」なら完了。1つでも「NG」なら、そこで止める
SELECT
  IF((SELECT COUNT(*) FROM giftia_t503.products p JOIN giftia_t503.categories c ON c.id = p.category_id
        WHERE p.tax_category <> IF(c.name IN ('食品', '飲料'), 'reduced_8', 'standard_10')) = 0
     AND (SELECT COUNT(*) FROM giftia_t503.products WHERE tax_category IS NULL) = 0, 'OK', 'NG') AS 税区分,
  IF((SELECT COUNT(*) FROM giftia_t503.product_price_histories h JOIN giftia_t503.products p ON p.id = h.product_id AND h.price = p.price)
     = (SELECT COUNT(*) FROM giftia_t503.products), 'OK', 'NG') AS 価格履歴が全商品,
  IF((SELECT COUNT(*) FROM giftia_t503.products WHERE status = 'active') = (SELECT COUNT(*) FROM giftia_t503.products), 'OK', 'NG') AS 全商品が販売中,
  IF((SELECT COUNT(*) FROM giftia_t503.product_attributes) = (SELECT COUNT(*) FROM giftia_t503.product_facts), 'OK', 'NG') AS 属性の件数が元と同じ,
  IF((SELECT SUM(NOT (s.review_count <=> p.review_count)) + SUM(NOT (ROUND(s.rating_avg, 1) <=> p.rating))
        FROM giftia_t503.product_rating_summary s JOIN giftia_t503.products p ON p.id = s.product_id) = 0, 'OK', 'NG') AS 評価のずれ0;
