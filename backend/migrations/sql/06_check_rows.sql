-- 06：データの照合（行ごとに小さな数にして足し合わせる。長い文字を作らないので、サーバーの設定に左右されない）。読むだけ
SELECT @@version, @@group_concat_max_len AS つなげる長さの上限, @@max_allowed_packet AS 送れる大きさの上限,
       IF(@@sql_mode LIKE '%NO_BACKSLASH_ESCAPES%', 'あり', 'なし') AS バックスラッシュを文字として読む設定;
SELECT 'products' AS 表, COUNT(*) AS 件数,
  SUM(id * (CRC32(product_id) % 1000)) AS idとコードの組み合わせ,
  SUM(CRC32(IFNULL(storage_method, ''))) AS 保存方法の記号,
  SUM(LOCATE(CHAR(10), IFNULL(storage_method, '')) > 0) AS 保存方法に改行が入った件数,
  MAX(CHAR_LENGTH(storage_method)) AS 保存方法のいちばん長い文字数,
  SUM(CRC32(CONCAT_WS(':', is_individually_wrapped, shelf_life_days, quantity_value, quantity_unit, tax_category, status))) AS そのほかの列の記号,
  SUM(CRC32(CONCAT_WS(':', id, category_id, brand_id))) AS idとマスタの記号
FROM giftia_t503.products;
SELECT 'order_items' AS 表, COUNT(*) AS 件数, SUM(CRC32(CONCAT_WS(':', order_id, line_no, product_numeric_id))) AS 行の記号の合計 FROM giftia_t503.order_items
UNION ALL
SELECT 'product_attributes', COUNT(*), SUM(CRC32(CONCAT_WS(':', product_id, fact_key, unit, bool_value, int_value))) FROM giftia_t503.product_attributes;
