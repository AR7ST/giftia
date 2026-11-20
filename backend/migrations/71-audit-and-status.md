# Issue #71 生年・監査列・販売／注文状態の移行案

## 適用前

DB管理者が検証環境で表一覧と `SHOW CREATE TABLE` を確認し、既存の同名列、注文処理と状態の対応、書き込み元を洗い出す。バックアップと復元を確認し、DDL は段階ごとに記録する。MySQL では DDL が暗黙にコミットされるため、中断した場合は定義を確認して再開する。

## 生年

```sql
ALTER TABLE users
    ADD COLUMN birth_year SMALLINT UNSIGNED NULL,
    ADD COLUMN recorded_at DATETIME(6) NULL,
    ADD COLUMN birth_year_is_estimated BOOLEAN NULL,
    ADD CONSTRAINT chk_users_birth_year_metadata CHECK (
        (birth_year IS NULL AND recorded_at IS NULL AND birth_year_is_estimated IS NULL)
        OR (birth_year IS NOT NULL AND recorded_at IS NOT NULL
            AND birth_year_is_estimated IS NOT NULL AND birth_year_is_estimated IN (0, 1))
    );
```

既存の `age_group` は切り戻し用に維持し、年代だけしかない行は3列とも NULL とする。根拠を確認できた生年だけ登録し、記録日時は UTC、推定が明示された情報はフラグ1、確認済みの情報は0とする。登録側で妥当な年の範囲を検証する。生年や記録日時を公開検索 API に追加しない。

## 監査列

以下は既存の同名列がない場合の例。管理者が把握した対象表ごとに適用し、既存列があれば型と意味を確認して再利用する。

```sql
ALTER TABLE products
    ADD COLUMN created_at DATETIME(6) NULL,
    ADD COLUMN updated_at DATETIME(6) NULL,
    ADD COLUMN updated_by VARCHAR(128) NULL;
```

旧行の日時・更新者は根拠がなければ NULL とする。導入後は、書き込み処理が認証済みの内部担当者IDまたは固定のサービスIDから更新者を設定し、同一トランザクションで UTC の更新日時と共に記録する。新規行には作成日時も設定する。移行処理を行う場合は移行用サービスIDを記録する。ブラウザから渡された値を更新者としてそのまま採用しない。

## 販売・注文状態

```sql
ALTER TABLE products ADD COLUMN status ENUM('active', 'inactive') NULL;
ALTER TABLE orders ADD COLUMN order_status VARCHAR(32) NULL;
```

商品は従来の在庫条件と公開状態を比較し、現行検索で公開対象のものを `active` とする。既存の業務情報から非公開と確認できる商品は `inactive` とする。未分類が残っていないことを確認し、書き込み側に状態設定を追加してから商品状態を必須化する。通常検索の件数照会と明細の両方に `status = %s`（値は `active`）を加え、在庫・予算の既存条件も使う。送別検索は本 Issue の指定範囲に含まれない。

注文は業務上の状態と遷移を管理者が確定する。既存注文は根拠がある状態だけを登録し、それ以外は NULL にする。既存処理が遷移表と一致するまで、注文の検索や集計への条件追加は保留する。

## 検証と切り戻し

- 検証環境で、架空の在庫あり商品を `active` と `inactive` に分け、通常検索の件数と明細に `active` だけが出ることを確認する。在庫切れと価格の境界、新規・既存注文の動作も比較する。
- 生年不明・確認済み・推定の各レコードと、複数の書き込み元で監査日時と更新者の記録を確認する。
- 切り戻す場合は書き込みを止め、状態を参照する検索と書き込み処理を旧版へ戻す。移行後に記録した値は表ごとの主キーとともに退避する。追加した列は残したまま復旧できる。撤去する場合は参照する後続処理を先に外し、生年のチェック制約、今回追加した状態列・監査列・生年関連列の順に削除する。既存の列は対象外とし、旧版の検索と注文処理を再確認する。
