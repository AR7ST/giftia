# Munder Difflin エージェント割り振り（班員対応表）

班員ごとに、自分のPCでMunder Difflinを立ち上げ、下記2つのエージェントをimportしてください（`munder/agents/*.hire.json`）。

## 人数について

Team18さんは「りじちょー＋スタッフ5名」の6人体制でしたが、タケチームは人間3名・画面(Next.js)とAPI(FastAPI)の2領域という規模のため、05の決定事項どおり**boss＋3体（計4体）の小さい構成**を維持しています。Team18さんと同じ6人体制を丸ごと導入する必要はありません（必要になれば後から増やせます）。

## 編成

| 班員 | エージェント | provider | モデル |
|---|---|---|---|
| タケ（班長） | boss（統括・Issue整理・PRレビュー補助・ハブ保守） | `claude` | Claude Sonnet 5 |
| タケ（班長） | genemi（開発サポート全般） | `gemini` | 最新版（Munder起動時に選択） |
| むっちゃん | claude-code（開発作業全般） | `claude` | Claude Sonnet 5 |
| まいまい | codex（開発作業全般） | `codex` | 最新版（Munder起動時に選択） |

**考え方**：タケさんだけがGemini・Codex・Claude Codeの3つ全部使えるため、班の統括役（boss）と独自ツール（Gemini）の2体を担当。むっちゃん・まいまいさんは1人1体に絞り、3プロバイダーが重複なく揃う形にしています。

モデルは、Claude Sonnet 5は確実な現行モデルのため明記していますが、Gemini・Codexの正確な最新モデル名はここでは確認できないため、`hire.json`には`model`を決め打ちせず、Munder起動時にご自身で最新版を選ぶ運用にしています。

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
