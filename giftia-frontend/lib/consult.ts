// lib/consult.ts — 選んだ1〜3商品から、LINE に貼る相談文を作る（FR-04）。画面を持たない関数だけ
// 商品の URL は作らない。代わりに「商品ID：」を書く

// 相談文に使う商品の項目を共通の型 FarewellGift から取り出す
// FarewellGift[] をそのまま candidates に渡せる
import type { FarewellGift } from "./api";
import { formatRating } from "./rating";
export type ConsultCandidate = Pick<FarewellGift, "id" | "name" | "brand" | "category" | "price" | "description" | "rating" | "reviewCount" | "ratingStatus">;

export type ConsultInput = {
  candidates: ConsultCandidate[]; // 選択順。使うのは先頭 MAX_CANDIDATES 件まで
  recommendedId: string | null; // null = おすすめ未指定
  reason: string; // 任意。空・空白だけなら理由の文を出さない
};

export const MAX_CANDIDATES = 3;
// 相談文に載せる説明の最大文字数。超えたら切って「…」を付ける
export const DESCRIPTION_MAX = 60;

// 説明：改行・連続した空白を1つの空白にまとめ、長ければ切る。null・空なら null（行を出さない）
export function formatDescription(description: string | null): string | null {
  if (description === null) return null;
  const text = description.replace(/\s+/g, " ").trim();
  if (text === "") return null;
  const chars = Array.from(text); // 絵文字などを途中で切らないよう、1文字ずつに分ける
  return chars.length > DESCRIPTION_MAX ? chars.slice(0, DESCRIPTION_MAX).join("") + "…" : text;
}

// 相談文を作る。候補が0件なら null（コピーさせない）
export function buildConsultText(input: ConsultInput): string | null {
  const candidates = input.candidates.slice(0, MAX_CANDIDATES);
  if (candidates.length === 0) return null;

  const lines: string[] = [];

  // おすすめは候補の中にあるときだけ書く（無ければ自動で決めない）
  const recommended = candidates.find((c) => c.id === input.recommendedId);
  if (recommended) {
    lines.push(`私は${recommended.name}がおすすめです。`);
    const reason = input.reason.trim();
    // 文末に句点が無ければ「。」を足す
    if (reason !== "") lines.push(`理由は${reason}${/[。．.！!？?]$/.test(reason) ? "" : "。"}`);
    lines.push("");
  }

  lines.push(`送別ギフトの候補（${candidates.length}件）`);
  candidates.forEach((c, i) => {
    lines.push("");
    lines.push(`${i + 1}. ${c.name}`);
    lines.push(`${c.brand}・${c.price.toLocaleString("ja-JP")}円・${formatRating(c)}`);
    const description = formatDescription(c.description);
    if (description !== null) lines.push(description);
    lines.push(`商品ID：${c.id}`);
  });

  return lines.join("\n");
}
