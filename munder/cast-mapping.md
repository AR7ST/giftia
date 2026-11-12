# Munder Difflin エージェント割り振り（班員対応表）

班員ごとに、自分のPCでMunder Difflinを立ち上げ、下表の自分の行のエージェントをすべてimportしてください（`munder/agents/*.hire.json`）。

## 人数・構成の考え方

- Team18さんは「りじちょー＋スタッフ5名」の6人体制でしたが、タケチームは人間3名・画面(Next.js)とAPI(FastAPI)の2領域という規模のため、05の決定事項どおり**boss＋α体**の小さい構成を維持しています（Team18さんと同じ6人体制を丸ごと導入する必要はありません）。
- 一方で、**1人のPC上で複数プロバイダーを同時に動かすこと自体はMunderの標準機能**です（同じオフィス内でbossはClaude、別の担当はGeminiのように混在できます）。
- これを利用し、**各班員が「自分の使えるAIツールを全部」動かして、容量（利用上限）を分散**する構成にしました。Claude側の利用上限で全員の作業が止まることを防ぐねらいです。

## 編成（全8体）

司令塔（boss）は全員共通。それ以外は「メイン／サブ1／サブ2」として、空いているAIへ作業を振り分けるための同格の開発担当です（仕事内容はどれも同じ。AIエンジンだけが違います）。

### タケ（班長）

| | エージェント | AI | provider | モデル |
|---|---|---|---|---|
| 司令塔 | boss | クロード | `claude` | Claude Sonnet 5 |
| メイン | genemi | Gemini | `gemini` | Gemini 2.5 Pro系（要確認） |
| サブ1 | take-claude | クロード | `claude` | Claude Sonnet 5 |
| サブ2 | take-codex | Codex | `codex` | GPT-5.1 Codex系（要確認） |

### むっちゃん

| | エージェント | AI | provider | モデル |
|---|---|---|---|---|
| 司令塔 | boss | クロード | `claude` | Claude Sonnet 5 |
| メイン | mutchan-claude | クロード | `claude` | Claude Sonnet 5 |
| サブ1 | mutchan-codex | Codex | `codex` | GPT-5.1 Codex系（要確認） |

### まいまい

| | エージェント | AI | provider | モデル |
|---|---|---|---|---|
| 司令塔 | boss | クロード | `claude` | Claude Sonnet 5 |
| メイン | maimai-codex | Codex | `codex` | GPT-5.1 Codex系（要確認） |
| サブ1 | maimai-claude | クロード | `claude` | Claude Sonnet 5 |

**タケは4体（司令塔＋3）、むっちゃん・まいまいは各3体（司令塔＋2）**です（タケだけ3プロバイダー全部使えるため1体多い）。

**モデル名について**：Claude Sonnet 5は確実な現行モデルです。Gemini・Codexの「2.5 Pro」「GPT-5.1」は、2026年11月時点で実在するか確証が持てないため、**Munder導入時にアプリ側のモデル一覧を見て、実際にある最新のものを選んでください**（`hire.json`には`model`を決め打ちしていません）。

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
