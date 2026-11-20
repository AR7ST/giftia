import type { FarewellGift } from "./api";

export function formatRating(gift: Pick<FarewellGift, "rating" | "reviewCount" | "ratingStatus">): string {
  const n = gift.reviewCount;
  if (n === null) return "評価不明（件数不明）";
  if (gift.ratingStatus === "valid") return `★${gift.rating}（${n}件）`;
  if (gift.ratingStatus === "no_reviews") return "評価なし（0件）";
  if (gift.ratingStatus === "unknown") return `評価不明（${n}件）`;
  return "評価不明（要確認）";
}
