# Munder Difflin エージェント割り振り（班員対応表）

班員ごとに、自分のPCでMunder Difflinを立ち上げ、下記2つのエージェントをimportしてください（`munder/agents/*.hire.json`）。

| 班員 | エージェント1（共通） | エージェント2（担当AI） | provider |
|---|---|---|---|
| タケ | boss | genemi | gemini |
| むっちゃん | boss | claude-code | claude |
| まいまい | boss | codex | codex |

## import するファイル

- 全員共通：`munder/agents/boss.hire.json`
- タケ：`munder/agents/genemi.hire.json`
- むっちゃん：`munder/agents/claude-code.hire.json`
- まいまい：`munder/agents/codex.hire.json`

## 補足

- `boss`は班員全員が自分のMunderにそれぞれimportします（同じ定義ファイルを、各自のPC上で個別に動かす形です。1つを共有するわけではありません）。
- `genemi`・`claude-code`・`codex`の3つは、担当する人のPCにのみimportしてください。
- `provider`の値（`gemini`・`claude`・`codex`）は、Munder Difflin v0.5.7での正式な指定方法を実機未確認のため、importしてエラーになる場合はMunder側の設定画面でプロバイダーを選び直してください（検証前の候補値です）。
- 役割（画面・API・ハブ）は分けず、担当AIごとに開発作業全般を担当する形にしています。分担が必要な場合は、Issue単位で割り振ってください。
