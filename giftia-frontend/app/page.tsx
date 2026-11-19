// app/page.tsx — Giftia 検索画面（2週目・穴埋め版）
// 【穴7】【穴8】を、対応表と公式ドキュメントを頼りに自分で埋める。
// 答えは 配布コード/答え合わせ/frontend/page.tsx（自分で埋めてから見る）。
// 1週目との違い：①searchGifts が FastAPI を呼ぶ（async/await）②入力した条件を渡す ③つながらないときの表示
"use client"; // ← ブラウザで動く合図。useState や onClick を使う画面に必要

import { useRef, useState } from "react";
import ResultCard from "./ResultCard";
import ConsultPanel from "./ConsultPanel";
import Skyline from "./Skyline";
import {
  FarewellApiError,
  searchFarewellGifts,
  searchGifts,
  type FarewellGift,
  type Gift,
} from "@/lib/api";

type Mode = "standard" | "business" | "farewell";
type FarewellStatus = "idle" | "loading" | "ok" | "empty" | "validation" | "error";

const MAX_SELECT = 3;
const BUDGET_MAX = 1_000_000;

export default function Home() {
  // ① 状態（変化するデータ）を覚える箱
  const [mode, setMode] = useState<Mode>("standard");                         // どのタブか
  const [keyword, setKeyword] = useState("");                             // 入力した言葉
  const [category, setCategory] = useState("");                           // 選んだカテゴリー
  const [indivWrap, setIndivWrap] = useState(false); // 個包装だけ（取引先へのお礼）
  const [priceBand, setPriceBand] = useState("");                         // 価格帯（取引先へのお礼）
  const [results, setResults] = useState<Gift[] | null>(null);            // 検索結果
  const [error, setError] = useState("");                                 // つながらないときの文言

  // 送別ギフトタブ
  const [budget, setBudget] = useState("4500");                           // 予算の上限（入力中の文字）
  const [fKeyword, setFKeyword] = useState("");
  const [fStatus, setFStatus] = useState<FarewellStatus>("idle");
  const [fResults, setFResults] = useState<FarewellGift[]>([]);
  const [fTotal, setFTotal] = useState(0);
  const [appliedPriceMax, setAppliedPriceMax] = useState<number | null>(null); // 結果を出したときの予算
  const [fMessage, setFMessage] = useState("");
  const [selected, setSelected] = useState<FarewellGift[]>([]);           // 相談候補（選んだ順・最大3件）
  const [recommendedId, setRecommendedId] = useState<string | null>(null); // おすすめ（1件）
  const [reason, setReason] = useState("");                               // おすすめの理由（任意）

  // 検索ごとの世代番号。最新の番号の結果だけを画面に反映する（古い応答の上書き防止）
  const generation = useRef(0);
  const controller = useRef<AbortController | null>(null);

  function startRequest(): number {
    controller.current?.abort();
    controller.current = null;
    generation.current += 1;
    return generation.current;
  }

  function resetSelection() {
    setSelected([]);
    setRecommendedId(null);
    setReason("");
  }

  function changeMode(next: Mode) {
    startRequest(); // 進行中の検索を中断し、古い完了を無効にする
    setMode(next);
    setResults(null);
    setError("");
    setFStatus("idle");
    setFResults([]);
    setFMessage("");
    resetSelection();
  }

  // ② 検索ボタンの処理（API に聞くので、結果が返るまで待つ＝async/await）
  async function onSearch(e: React.FormEvent) {
    e.preventDefault(); // ページの再読み込みを止める
    if (mode === "farewell") return onFarewellSearch();
    const myGen = startRequest();
    setError("");
    // いま開いているタブの条件だけを送る（もう一方のタブの入力は送らない）
    const condition = mode === "standard"
      ? { keyword, category, indivWrap: false, priceBand: "" }
      : { keyword: "", category: "", indivWrap, priceBand };
    try {
      const found = await searchGifts(condition);
      if (myGen !== generation.current) return;
      setResults(found);
    } catch (err) {
      if (myGen !== generation.current) return;
      setResults(null);
      setError(`APIにつながりません：${(err as Error).message}`); // 原因はブラウザの Console に出る
    }
  }

  async function onFarewellSearch() {
    const myGen = startRequest();
    resetSelection();
    const text = budget.trim();
    const priceMax = Number(text);
    if (!/^\d+$/.test(text) || priceMax < 1 || priceMax > BUDGET_MAX) {
      setFResults([]);
      setFStatus("validation");
      setFMessage(`予算の上限は、1〜${BUDGET_MAX.toLocaleString()}の整数（円）で入力してください。`);
      return;
    }
    const ac = new AbortController();
    controller.current = ac;
    setFStatus("loading");
    setFMessage("");
    try {
      const res = await searchFarewellGifts({ priceMax, keyword: fKeyword.trim() || undefined }, ac.signal);
      if (myGen !== generation.current) return;
      setFResults(res.results);
      setFTotal(res.total);
      setAppliedPriceMax(priceMax);
      setFStatus(res.results.length === 0 ? "empty" : "ok");
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      if (myGen !== generation.current) return;
      setFResults([]);
      if (err instanceof FarewellApiError && err.kind === "validation") {
        setFStatus("validation");
        setFMessage("条件が正しくありません。予算の上限とキーワードを確かめてください。");
      } else {
        setFStatus("error");
        setFMessage("検索できませんでした。しばらくしてから、もう一度試してください。");
      }
    }
  }

  function toggleSelect(g: FarewellGift) {
    const isSelected = selected.some((s) => s.id === g.id);
    if (isSelected) {
      setSelected(selected.filter((s) => s.id !== g.id));
      if (recommendedId === g.id) { // おすすめにした商品を外したら、おすすめと理由をリセット
        setRecommendedId(null);
        setReason("");
      }
    } else if (selected.length < MAX_SELECT) {
      setSelected([...selected, g]);
    }
  }

  // ③ 画面
  return (
    <main className="page">
      <header className="header">
        <div className="sun" aria-hidden="true" />
        <h1>Giftia</h1>
        <p className="tagline">送別ギフトを、仲間と納得して決められる。</p>
        <Skyline />
      </header>

      {/* タブ：state(mode)＋条件で出し分ける */}
      <nav className="modes">
        <button className={mode === "standard" ? "on" : ""} onClick={() => changeMode("standard")}>いまの検索</button>
        <button className={mode === "business" ? "on" : ""} onClick={() => changeMode("business")}>取引先へのお礼</button>
        <button className={mode === "farewell" ? "on" : ""} onClick={() => changeMode("farewell")}>送別ギフト</button>
      </nav>

      <form className="form" onSubmit={onSearch}>
        {mode === "standard" ? (
          <>
            <input className="q" value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="キーワード（例：送別 お菓子）" />
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">すべてのカテゴリー</option>
              <option value="コスメ">コスメ</option>
              <option value="食品">食品</option>
              <option value="生活雑貨">生活雑貨</option>
            </select>
          </>
        ) : mode === "business" ? (
          <>
            <label className="chk"><input type="checkbox" checked={indivWrap} onChange={(e) => setIndivWrap(e.target.checked)} /> 個包装</label>
            <select value={priceBand} onChange={(e) => setPriceBand(e.target.value)}>
              <option value="">すべての価格帯</option>
              <option value="3000">3,000〜5,000円</option>
              <option value="5000">5,000〜10,000円</option>
            </select>
          </>
        ) : (
          <>
            <label className="chk">
              予算の上限（合計・円）
              <input className="budget" inputMode="numeric" value={budget} onChange={(e) => setBudget(e.target.value)} />
            </label>
            <input className="q" value={fKeyword} onChange={(e) => setFKeyword(e.target.value)} placeholder="キーワード（任意）" />
          </>
        )}
        <button type="submit">検索</button>
      </form>

      {mode !== "farewell" && error && <p className="summary">{error}</p>}

      {/* 結果：同じ ResultCard を map で並べる（使い回し） */}
      {mode !== "farewell" && results && (
        <section>
          <p className="summary">上位 {results.length} 件</p>
          <div className="grid">
            {results.map((g, i) => <ResultCard key={g.id} gift={g} rank={i + 1} />)}
          </div>
        </section>
      )}

      {mode === "farewell" && (
        <section>
          {fStatus === "loading" && <p className="notice">検索中です…</p>}
          {(fStatus === "validation" || fStatus === "error") && <p className="notice err">{fMessage}</p>}
          {fStatus === "empty" && (
            <p className="notice">
              予算 {appliedPriceMax?.toLocaleString()} 円以下で、在庫のある商品は見つかりませんでした。予算は自動では広げていません。条件を変えて、もう一度検索してください。
            </p>
          )}
          {fStatus === "ok" && (
            <>
              <p className="summary">
                予算 {appliedPriceMax?.toLocaleString()} 円以下：該当 {fTotal} 件のうち、{fResults.length} 件を表示
              </p>

              {/* 見た目の並び：広い画面では結果を左、相談候補と LINE 相談文を右に置く（狭い画面では結果の下） */}
              <div className="farewell-layout">
                <div className="grid">
                  {fResults.map((g, i) => (
                    <ResultCard
                      key={g.id}
                      gift={g}
                      rank={i + 1}
                      farewell={g}
                      selected={selected.some((s) => s.id === g.id)}
                      selectDisabled={selected.length >= MAX_SELECT}
                      onToggleSelect={() => toggleSelect(g)}
                    />
                  ))}
                </div>

                <aside className="side">
                  {selected.length > 0 && (
                    <div className="consult">
                      <h2>相談候補（{selected.length}/{MAX_SELECT}件）</h2>
                      <ul>
                        {selected.map((g) => (
                          <li key={g.id}>
                            <span>{g.name}</span>
                            <button
                              type="button"
                              className={recommendedId === g.id ? "on" : ""}
                              onClick={() => { setRecommendedId(recommendedId === g.id ? null : g.id); setReason(""); }}
                            >
                              {recommendedId === g.id ? "おすすめを解除" : "おすすめにする"}
                            </button>
                          </li>
                        ))}
                      </ul>
                      {recommendedId && (
                        <label>
                          おすすめの理由（任意）
                          <textarea rows={2} value={reason} onChange={(e) => setReason(e.target.value)} />
                        </label>
                      )}
                    </div>
                  )}

                  {/* LINE 相談文（PR3b）。候補が0件のときは「候補を1件以上選んでください」と出て、コピーできない */}
                  <ConsultPanel candidates={selected} recommendedId={recommendedId} reason={reason} />
                </aside>
              </div>
            </>
          )}
        </section>
      )}
    </main>
  );
}
