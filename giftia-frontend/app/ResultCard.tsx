// app/ResultCard.tsx — 結果カード（部品）。送別ギフトのときだけ farewell を渡すと、スタンプ・評価の状態などを追加で表示する
import type { FarewellGift, ResultCardGift } from "@/lib/api";
import { formatRating, ratingStatusOf } from "../lib/rating";
import { formatQuantity, formatTax } from "../lib/display";

type Props = {
  gift: ResultCardGift;
  rank: number;
  farewell?: FarewellGift;      // 送別タブのときだけ渡す
  selected?: boolean;           // 相談候補に選ばれているか
  selectDisabled?: boolean;     // 3件選択済みで、未選択のカードは押せない
  onToggleSelect?: () => void;  // 渡したときだけ「相談候補に選ぶ」ボタンを出す
};

function triText(v: boolean | null): string {
  return v === null ? "不明" : v ? "対応" : "非対応";
}

function excerpt(s: string | null): string {
  if (!s) return "";
  return s.length > 60 ? `${s.slice(0, 60)}…` : s;
}

export default function ResultCard({ gift, rank, farewell, selected, selectDisabled, onToggleSelect }: Props) {
  return (
    <div className={`card${selected ? " selected" : ""}`}>
      <p className="meta"><span className="rank">{rank}位</span>{gift.category}・{gift.brand}</p>
      <h3 className="name">{gift.name}</h3>
      <p className="price">{gift.price.toLocaleString()}円</p>
      {formatTax(gift.price, gift) && <p className="meta">{formatTax(gift.price, gift)}</p>}
      {formatQuantity(gift) && <p className="meta">数量：{formatQuantity(gift)}</p>}
      {!farewell && gift.storageMethod && <p className="meta">保存方法：{gift.storageMethod}</p>}
      {farewell ? (
        <>
          <p className="meta">{formatRating(farewell)}</p>
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
        // 送別以外も、送別・LINE 相談文と同じ形（★4.0（5件））で出す（#92）
        <p className="meta">
          {formatRating({ ...gift, ratingStatus: ratingStatusOf(gift.rating, gift.reviewCount) })}
        </p>
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
