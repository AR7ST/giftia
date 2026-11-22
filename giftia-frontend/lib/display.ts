// lib/display.ts — DB 改善で足した項目の表示（PC での試し）
import type { ProductExtras } from "./api";

const TAX_RATE = { standard_10: 0.1, reduced_8: 0.08 } as const;

// 税：「税込（8%）・税抜 約3,685円」。税区分がなければ空文字（表示しない）
// 税区分はカテゴリから決めた仮の値。税抜は税込からの逆算なので「約」を付ける
export function formatTax(price: number, extras: ProductExtras): string {
  if (!extras.taxCategory) return "";
  const rate = TAX_RATE[extras.taxCategory];
  const excluded = Math.round(price / (1 + rate));
  return `税込（${Math.round(rate * 100)}%）・税抜 約${excluded.toLocaleString()}円`;
}

// 数量：「15個入」「500g」「750ml」。数量がなければ空文字（表示しない）
export function formatQuantity(extras: ProductExtras): string {
  const v = extras.quantityValue;
  if (v === null || v === undefined || !extras.quantityUnit) return "";
  const n = Number.isInteger(v) ? v.toLocaleString() : String(v);
  if (extras.quantityUnit === "piece") return `${n}個入`;
  return `${n}${extras.quantityUnit}`;
}
