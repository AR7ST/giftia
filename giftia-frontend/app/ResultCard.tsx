// app/ResultCard.tsx — 結果カード（部品）。送別ギフトのときだけ farewell を渡すと、スタンプ・評価の状態などを追加で表示する
import type { FarewellGift, ResultCardGift } from "@/lib/api";

type Props = {
  gift: ResultCardGift;
  rank: number;
  farewell?: FarewellGift;      // 送別タブのときだけ渡す
  selected?: boolean;           // 相談候補に選ばれているか
  selectDisabled?: boolean;     // 3件選択済みで、未選択のカードは押せない
  onToggleSelect?: () => void;  // 渡したときだけ「相談候補に選ぶ」ボタンを出す
};

function ratingText(g: FarewellGift): string {
  const n = g.reviewCount;
  if (g.ratingStatus === "valid") return `★${g.rating}（${n}件）`;
  if (g.ratingStatus === "no_reviews") return "評価なし（0件）";
  if (g.ratingStatus === "unknown") return n === null ? "評価不明（件数不明）" : `評価不明（${n}件）`;
  return "評価不明（要確認）";
}

function triText(v: boolean | null): string {
  return v === null ? "不明" : v ? "対応" : "非対応";
}

function excerpt(s: string | null): string {
  if (!s) return "";
  return s.length > 60 ? `${s.slice(0, 60)}…` : s;
}

export default function ResultCard({ gift, rank, farewell, selected, selectDisabled, onToggleSelect }: Props) {
  return (
    <div className="card">
      <p className="meta">{rank}位・{gift.category}・{gift.brand}</p>
      <h3 className="name">{gift.name}</h3>
      <p className="price">{gift.price.toLocaleString()}円</p>
      {farewell ? (
        <>
          <p className="meta">{ratingText(farewell)}</p>
          {farewell.stamps.length > 0 && (
            <p className="stamps">
              {farewell.stamps.map((s) => (
                <span key={s.label} className={`stamp stamp-${s.type}`}>{s.label}</span>
              ))}
            </p>
          )}
          <p className="meta">
            包装：{triText(farewell.giftWrap)}・カード：{triText(farewell.messageCard)}・
            発送目安：{farewell.deliveryDays === null ? "不明" : `${farewell.deliveryDays}日`}
          </p>
          <p className="meta">販売数：{farewell.salesCount === null ? "不明" : farewell.salesCount.toLocaleString()}</p>
          {farewell.description && <p className="meta">{excerpt(farewell.description)}</p>}
        </>
      ) : (
        <p className="meta">評価{gift.rating ?? " 不明"}（{gift.reviewCount === null ? "件数不明" : `${gift.reviewCount}件`}）</p>
      )}
      {onToggleSelect && (
        <button
          type="button"
          className={`pick${selected ? " on" : ""}`}
          disabled={!selected && selectDisabled}
          onClick={onToggleSelect}
        >
          {selected ? "相談候補から外す" : "相談候補に選ぶ"}
        </button>
      )}
    </div>
  );
}
