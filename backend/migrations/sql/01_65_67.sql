-- 01：#65（保存方法・賞味期限・個包装）と #67（数量・単位）
-- 実行の前に：右上の接続名が Tech0_Step3-1、下の @@version が 8.4.9 であることを確かめる
SELECT @@version;
SELECT COUNT(*) AS products_before FROM giftia_t503.products;

-- ① 列を足す（#65 の3列 ＋ #67 の2列。実行したその場で確定する）
ALTER TABLE giftia_t503.products
    ADD COLUMN storage_method VARCHAR(255) NULL DEFAULT NULL,
    ADD COLUMN shelf_life_days INT UNSIGNED NULL DEFAULT NULL,
    ADD COLUMN is_individually_wrapped TINYINT UNSIGNED NULL DEFAULT NULL,
    ADD COLUMN quantity_value DECIMAL(12,3) NULL DEFAULT NULL,
    ADD COLUMN quantity_unit VARCHAR(8) CHARACTER SET ascii COLLATE ascii_bin NULL DEFAULT NULL,
    ADD CONSTRAINT chk_products_individually_wrapped CHECK (is_individually_wrapped IN (0, 1)),
    ADD CONSTRAINT chk_products_quantity CHECK (
        (quantity_value IS NULL AND quantity_unit IS NULL)
        OR (quantity_value IS NOT NULL AND quantity_unit IS NOT NULL AND quantity_value > 0
            AND quantity_unit IN ('piece', 'g', 'ml')
            AND (quantity_unit <> 'piece' OR quantity_value = FLOOR(quantity_value))));

-- ② 値を入れる（COMMIT するまで確定しない）
SET SQL_SAFE_UPDATES = 0;
START TRANSACTION;
-- #65 個包装：product_facts の indiv_wrap を写す
UPDATE giftia_t503.products p
  JOIN giftia_t503.product_facts f ON f.product_id = p.product_id AND f.fact = 'indiv_wrap'
  SET p.is_individually_wrapped = f.value;
-- #65 保存方法：説明文の【保存方法】の文章を入れる
UPDATE giftia_t503.products
  SET storage_method = TRIM(SUBSTRING_INDEX(SUBSTRING(description,
        LOCATE('【保存方法】', description) + CHAR_LENGTH('【保存方法】')), '\n', 1))
  WHERE LOCATE('【保存方法】', description) > 0;
-- #67 数量・単位：「15g」「2kg」「750ml」「1.8L」「5個入」の形だけ（容量○ml は入れ物の大きさなので入れない）
UPDATE giftia_t503.products SET quantity_value = CAST(CONVERT(REGEXP_SUBSTR(size, '^[0-9]+([.][0-9]+)?') USING ascii) AS DECIMAL(12,3)), quantity_unit = 'g' WHERE size REGEXP '^[0-9]+([.][0-9]+)?g$';
UPDATE giftia_t503.products SET quantity_value = CAST(CONVERT(REGEXP_SUBSTR(size, '^[0-9]+([.][0-9]+)?') USING ascii) AS DECIMAL(12,3)) * 1000, quantity_unit = 'g' WHERE size REGEXP '^[0-9]+([.][0-9]+)?kg$';
UPDATE giftia_t503.products SET quantity_value = CAST(CONVERT(REGEXP_SUBSTR(size, '^[0-9]+([.][0-9]+)?') USING ascii) AS DECIMAL(12,3)), quantity_unit = 'ml' WHERE size REGEXP '^[0-9]+([.][0-9]+)?ml$';
UPDATE giftia_t503.products SET quantity_value = CAST(CONVERT(REGEXP_SUBSTR(size, '^[0-9]+([.][0-9]+)?') USING ascii) AS DECIMAL(12,3)) * 1000, quantity_unit = 'ml' WHERE size REGEXP '^[0-9]+([.][0-9]+)?L$';
UPDATE giftia_t503.products SET quantity_value = CAST(CONVERT(REGEXP_SUBSTR(size, '^[0-9]+') USING ascii) AS DECIMAL(12,3)), quantity_unit = 'piece' WHERE size REGEXP '^[0-9]+個入$';

COMMIT;

-- ③ 確かめる：最後の表がすべて「OK」なら次へ。1つでも「NG」なら、そこで止める
-- （本当の件数は書かず、元のデータと数が合っているかで確かめる）
SELECT
  IF((SELECT COUNT(*) FROM giftia_t503.products WHERE is_individually_wrapped IS NOT NULL)
     = (SELECT COUNT(*) FROM giftia_t503.product_facts WHERE fact = 'indiv_wrap'), 'OK', 'NG') AS 個包装の件数が元と同じ,
  IF((SELECT COUNT(*) FROM giftia_t503.products p JOIN giftia_t503.product_facts f
        ON f.product_id = p.product_id AND f.fact = 'indiv_wrap' WHERE NOT (p.is_individually_wrapped <=> f.value)) = 0, 'OK', 'NG') AS 個包装の値が元と同じ,
  IF((SELECT COUNT(storage_method) FROM giftia_t503.products)
     = (SELECT COUNT(*) FROM giftia_t503.products WHERE LOCATE('【保存方法】', description) > 0), 'OK', 'NG') AS 保存方法の件数,
  IF((SELECT COUNT(*) FROM giftia_t503.products WHERE quantity_unit IS NOT NULL
        AND quantity_value <> CAST(CONVERT(REGEXP_SUBSTR(size, '^[0-9]+([.][0-9]+)?') USING ascii) AS DECIMAL(12,3))
                              * (CASE WHEN size REGEXP '(kg|L)$' THEN 1000 ELSE 1 END)) = 0, 'OK', 'NG') AS 数量が元の書き方と同じ,
  IF((SELECT COUNT(*) FROM giftia_t503.products WHERE size LIKE '容量%' AND quantity_unit IS NOT NULL) = 0, 'OK', 'NG') AS 容量は入れていない,
  IF((SELECT COUNT(*) FROM giftia_t503.products WHERE quantity_unit IS NOT NULL) > 0, 'OK', 'NG') AS 数量が入った;
