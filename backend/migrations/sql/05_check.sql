-- 05：できあがりの照合。本番と PC で、この結果がすべて同じなら、同じ DB になっている
-- 列・索引・制約の作りと、主なデータを、表ごとに短い記号（MD5 の先頭10文字）にまとめる
SELECT @@version;
SELECT t.table_name AS 表,
  (SELECT COUNT(*) FROM information_schema.columns c WHERE c.table_schema = t.table_schema AND c.table_name = t.table_name) AS 列の数,
  LEFT(MD5((SELECT GROUP_CONCAT(column_name, ':', column_type, ':', is_nullable, ':', column_key ORDER BY ordinal_position SEPARATOR '|')
            FROM information_schema.columns c WHERE c.table_schema = t.table_schema AND c.table_name = t.table_name)), 10) AS 列の記号,
  LEFT(MD5(IFNULL((SELECT GROUP_CONCAT(index_name, ':', seq_in_index, ':', column_name, ':', non_unique, ':', index_type ORDER BY index_name, seq_in_index SEPARATOR '|')
            FROM information_schema.statistics s WHERE s.table_schema = t.table_schema AND s.table_name = t.table_name), '')), 10) AS 索引の記号,
  LEFT(MD5(IFNULL((SELECT GROUP_CONCAT(constraint_name, ':', constraint_type ORDER BY constraint_name SEPARATOR '|')
            FROM information_schema.table_constraints k WHERE k.table_schema = t.table_schema AND k.table_name = t.table_name), '')), 10) AS 制約の記号
FROM information_schema.tables t
WHERE t.table_schema = 'giftia_t503'
ORDER BY t.table_name;

SELECT '件数' AS 種類,
  (SELECT COUNT(*) FROM giftia_t503.products) AS products,
  (SELECT COUNT(*) FROM giftia_t503.users) AS users,
  (SELECT COUNT(*) FROM giftia_t503.orders) AS orders,
  (SELECT COUNT(*) FROM giftia_t503.order_items) AS order_items,
  (SELECT COUNT(*) FROM giftia_t503.reviews) AS reviews,
  (SELECT COUNT(*) FROM giftia_t503.product_scenes) AS scenes,
  (SELECT COUNT(*) FROM giftia_t503.product_facts) AS facts,
  (SELECT COUNT(*) FROM giftia_t503.product_attributes) AS attributes,
  (SELECT COUNT(*) FROM giftia_t503.product_price_histories) AS histories;

SET SESSION group_concat_max_len = 10000000;
SELECT 'データの記号' AS 種類,
  LEFT(MD5((SELECT GROUP_CONCAT(CONCAT_WS(':', id, product_id, category_id, brand_id, is_individually_wrapped, storage_method,
            shelf_life_days, quantity_value, quantity_unit, tax_category, status) ORDER BY id SEPARATOR '|') FROM giftia_t503.products)), 10) AS products,
  LEFT(MD5((SELECT GROUP_CONCAT(CONCAT_WS(':', id, name) ORDER BY id SEPARATOR '|') FROM giftia_t503.categories)), 10) AS categories,
  LEFT(MD5((SELECT GROUP_CONCAT(CONCAT_WS(':', id, name) ORDER BY id SEPARATOR '|') FROM giftia_t503.brands)), 10) AS brands,
  LEFT(MD5((SELECT GROUP_CONCAT(CONCAT_WS(':', order_id, line_no, product_numeric_id) ORDER BY order_id, line_no SEPARATOR '|') FROM giftia_t503.order_items)), 10) AS order_items,
  LEFT(MD5((SELECT GROUP_CONCAT(CONCAT_WS(':', product_id, fact_key, unit, bool_value, int_value) ORDER BY product_id, fact_key SEPARATOR '|') FROM giftia_t503.product_attributes)), 10) AS attributes;
