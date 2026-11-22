import type { FarewellGift, RatingStatus } from "./api";

// API の rating_status()（backend/farewell.py）と同じ決まりで、評価の状態を決める。
// 送別以外の検索は ratingStatus を返さないので、画面側で同じ判定をする（#92）
export function ratingStatusOf(rating: number | null, reviewCount: number | null): RatingStatus {
  if (rating === null) return reviewCount === 0 ? "no_reviews" : "unknown";
  if (reviewCount === null) return "unknown";
  if (rating >= 1 && rating <= 5 && reviewCount >= 1) return "valid";
  return "inconsistent";
}

// 評価の表示。3つのタブと LINE 相談文で同じ形にする。平均はいつも小数1けた（4 → 4.0。#92）
export function formatRating(gift: Pick<FarewellGift, "rating" | "reviewCount" | "ratingStatus">): string {
  const n = gift.reviewCount;
  if (n === null) return "評価不明（件数不明）";
  if (gift.ratingStatus === "valid" && gift.rating !== null) return `★${gift.rating.toFixed(1)}（${n}件）`;
  if (gift.ratingStatus === "no_reviews") return "評価なし（0件）";
  if (gift.ratingStatus === "unknown") return `評価不明（${n}件）`;
  return "評価不明（要確認）";
}
