"use client";

// app/ConsultPanel.tsx — LINE 相談文のプレビューとコピー（部品）。page.tsx への組み込みは PR3b
import { useEffect, useMemo, useRef, useState } from "react";
import { buildConsultText, type ConsultInput } from "@/lib/consult";
import styles from "./ConsultPanel.module.css";

type CopyStatus = "idle" | "copying" | "success" | "error";

export default function ConsultPanel({ candidates, recommendedId, reason }: ConsultInput) {
  const text = useMemo(
    () => buildConsultText({ candidates, recommendedId, reason }),
    [candidates, recommendedId, reason],
  );
  const [status, setStatus] = useState<CopyStatus>("idle");

  // 文面が変わったら、コピー結果の表示を消す（描画中に前回の文面と比べる、React の推奨のやり方）
  const [shownText, setShownText] = useState(text);
  if (shownText !== text) {
    setShownText(text);
    setStatus("idle");
  }

  // コピーが終わったときに、今の文面と比べるための控え
  const latestText = useRef(text);
  useEffect(() => {
    latestText.current = text;
  }, [text]);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  async function handleCopy() {
    if (text === null) return;
    const startedText = text; // コピーを始めた時点の文面
    setStatus("copying");
    let ok = false;
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(startedText);
        ok = true;
      }
    } catch {
      ok = false;
    }
    // コピー中に文面が変わっていたら、古い結果で上書きしない
    if (latestText.current !== startedText) return;
    setStatus(ok ? "success" : "error");
    if (!ok) textareaRef.current?.select(); // 手動でコピーしやすいよう、文を選んでおく
  }

  return (
    <section className={styles.panel} aria-label="LINE 相談文">
      <h2 className={styles.title}>LINE 相談文</h2>
      {text === null ? (
        <p className={styles.hint}>候補を1件以上選んでください</p>
      ) : (
        <textarea
          ref={textareaRef}
          className={styles.preview}
          value={text}
          readOnly
          rows={Math.min(16, text.split("\n").length + 1)}
          aria-label="相談文のプレビュー"
        />
      )}
      <button
        type="button"
        className={styles.copyButton}
        onClick={handleCopy}
        disabled={text === null || status === "copying"}
      >
        コピー
      </button>
      <p className={styles.status} aria-live="polite">
        {status === "success" && <span className={styles.success}>コピーしました</span>}
        {status === "error" && (
          <span className={styles.error}>コピーできませんでした。下の文を選んで手動でコピーしてください</span>
        )}
      </p>
    </section>
  );
}
