# Munder Difflin エージェント割り振り（班員対応表）

班員ごとに、自分のPCでMunder Difflinを立ち上げ、下表の自分の行のエージェントをすべてimportしてください（`munder/agents/*.hire.json`）。

## 人数・構成の考え方

- Team18さんは「りじちょー＋スタッフ5名」の6人体制でしたが、タケチームは人間3名・画面(Next.js)とAPI(FastAPI)の2領域という規模のため、05の決定事項どおり**boss＋α体**の小さい構成を維持しています（Team18さんと同じ6人体制を丸ごと導入する必要はありません）。
- 一方で、**1人のPC上で複数プロバイダーを同時に動かすこと自体はMunderの標準機能**です（同じオフィス内でbossはClaude、別の担当はGeminiのように混在できます）。
- これを利用し、**各班員が「自分の使えるAIツールを全部」動かして、容量（利用上限）を分散**する構成にしました。Claude側の利用上限で全員の作業が止まることを防ぐねらいです。

## 編成（全8体）

| 班員 | エージェント | provider | モデル | 備考 |
|---|---|---|---|---|
| タケ（班長） | boss | `claude` | Claude Sonnet 5 | 統括・Issue整理・PRレビュー補助・ハブ保守 |
| タケ（班長） | genemi | `gemini` | 最新版（Munder起動時に選択） | 開発作業全般 |
| タケ（班長） | take-codex | `codex` | 最新版（Munder起動時に選択） | 開発作業全般（容量分散） |
| タケ（班長） | take-claude | `claude` | Claude Sonnet 5 | 開発作業全般（容量分散。bossとClaude枠を共有） |
| むっちゃん | mutchan-claude | `claude` | Claude Sonnet 5 | 開発作業全般 |
| むっちゃん | mutchan-codex | `codex` | 最新版（Munder起動時に選択） | 開発作業全般（容量分散） |
| まいまい | maimai-codex | `codex` | 最新版（Munder起動時に選択） | 開発作業全般 |
| まいまい | maimai-claude | `claude` | Claude Sonnet 5 | 開発作業全般（容量分散） |

**タケは4体、むっちゃん・まいまいは各2体**です（タケだけ3プロバイダー全部使えるため1体多い）。

## import するファイル

| 班員 | importするファイル |
|---|---|
| タケ | `munder/agents/boss.hire.json`・`genemi.hire.json`・`take-codex.hire.json`・`take-claude.hire.json` |
| むっちゃん | `munder/agents/boss.hire.json`・`mutchan-claude.hire.json`・`mutchan-codex.hire.json` |
| まいまい | `munder/agents/boss.hire.json`・`maimai-codex.hire.json`・`maimai-claude.hire.json` |

## 補足・注意

- `boss`は班員全員が自分のMunderにそれぞれimportします（同じ定義ファイルを、各自のPC上で個別に動かす形です。1つを共有するわけではありません）。
- **容量分散の限界**：bossと「〜-claude」系のエージェントは同じClaudeの利用枠（サブスクリプション）を共有します。完全に別枠になるのは、プロバイダーが異なる場合（Gemini・Codex）だけです。Claude側が詰まったら、Gemini／Codex側のエージェントに作業を回してください。
- `provider`の値（`gemini`・`claude`・`codex`）は、Munder Difflin v0.5.7での正式な指定方法を実機未確認のため、importしてエラーになる場合はMunder側の設定画面でプロバイダーを選び直してください（検証前の候補値です）。
- 役割（画面・API・ハブ）は分けず、全エージェント共通で「開発作業全般」を担当する形にしています。分担が必要な場合は、Issue単位で割り振ってください。
- 一度に複数エージェントへ同時に指示を出すと、同じファイルを複数エージェントが同時に編集して衝突する可能性があります。`isolate: true`（Worktree分離）を設定済みですが、できるだけ**1つのIssueには1エージェント**で進めてください。
