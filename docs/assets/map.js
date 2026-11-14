/* コードの地図 共通の部品。
   行番号はこの LINES の表1か所にまとめる。giftia のコードが変わったら、ここだけ直す。
   （2026-11-12 時点の main：Merge pull request #12（評価なし→null化）・#10（AGENTS.md改訂）・#8（Issue/PRテンプレート）まで確認済み） */
const REPO = "https://github.com/AR7ST/giftia/blob/main/";
const F = {
  page: "giftia-frontend/app/page.tsx",
  card: "giftia-frontend/app/ResultCard.tsx",
  api: "giftia-frontend/lib/api.ts",
  css: "giftia-frontend/app/globals.css",
  main: "backend/main.py",
  db: "backend/database.py",
};
const SHORT = { page: "page.tsx", card: "ResultCard.tsx", api: "api.ts", css: "globals.css", main: "main.py", db: "database.py", layout: "layout.tsx" };
F.layout = "giftia-frontend/app/layout.tsx";
const LINES = {
  // page.tsx（画面）
  useClient: ["page", 5, 5], imports: ["page", 7, 9],
  sMode: ["page", 13, 13], sKeyword: ["page", 14, 14], sCategory: ["page", 15, 15], sIndiv: ["page", 16, 16],
  sPrice: ["page", 17, 17], sResults: ["page", 18, 18], sError: ["page", 19, 19],
  onSearch: ["page", 22, 35], prevent: ["page", 23, 23], condition: ["page", 26, 28], awaitSearch: ["page", 30, 30], catchErr: ["page", 31, 33],
  title: ["page", 40, 40], tabs: ["page", 43, 46], tabStd: ["page", 44, 44], tabBiz: ["page", 45, 45],
  form: ["page", 48, 48], input: ["page", 51, 51], select: ["page", 52, 57], options: ["page", 53, 56],
  check: ["page", 61, 61], priceSel: ["page", 62, 66], button: ["page", 69, 69],
  errorShow: ["page", 72, 72], resultsArea: ["page", 75, 82], summary: ["page", 77, 77], mapCards: ["page", 79, 79],
  // ResultCard.tsx（カードの型紙）
  card: ["card", 4, 12], cardMeta: ["card", 7, 7], cardName: ["card", 8, 8], cardPrice: ["card", 9, 9], cardRating: ["card", 10, 10],
  // api.ts（伝書鳩）
  giftType: ["api", 7, 15], condType: ["api", 18, 23], apiUrl: ["api", 26, 26], searchGifts: ["api", 29, 45],
  params: ["api", 31, 36], pQ: ["api", 32, 32], pCat: ["api", 33, 33], pIndiv: ["api", 34, 34], pPrice: ["api", 35, 36],
  fetch: ["api", 39, 39], okCheck: ["api", 40, 40], json: ["api", 43, 44],
  // globals.css（見た目）
  cssVars: ["css", 2, 2], cssPage: ["css", 5, 5], cssH1: ["css", 6, 6], cssModes: ["css", 7, 9], cssSummary: ["css", 10, 10],
  cssForm: ["css", 11, 15], cssSubmit: ["css", 15, 15], cssGrid: ["css", 16, 16], cssCard: ["css", 17, 20], cssPrice: ["css", 19, 19],
  // main.py（受付）
  dotenv: ["main", 18, 18], app: ["main", 20, 20], cors: ["main", 26, 27], health: ["main", 30, 34],
  route: ["main", 37, 45], aQ: ["main", 39, 39], aCat: ["main", 40, 40], aIndiv: ["main", 41, 41], aPrice: ["main", 42, 43], aLimit: ["main", 44, 44],
  where: ["main", 48, 64], whereInit: ["main", 48, 48], wQ: ["main", 49, 51], wCat: ["main", 52, 54], wIndiv: ["main", 55, 57], wPrice: ["main", 58, 63], join: ["main", 64, 64],
  count: ["main", 67, 67], sqlSelect: ["main", 68, 74], orderBy: ["main", 71, 71], limitSql: ["main", 72, 72], ret: ["main", 76, 76],
  toGift: ["main", 79, 89], tgName: ["main", 85, 85], tgPrice: ["main", 86, 86], tgRating: ["main", 87, 87],
  // database.py（倉庫係）
  conn: ["db", 19, 39], fetchAll: ["db", 42, 51], execute: ["db", 48, 48],
};
const WEEK1 = "https://github.com/AR7ST/giftia/commit/373f901";
const WEEK2 = "https://github.com/AR7ST/giftia/commit/2ba468a";
const WEEK2API = "https://github.com/AR7ST/giftia/commit/919b750";

function url(key) {
  const [f, a, b] = LINES[key];
  return REPO + F[f] + "#L" + a + (b > a ? "-L" + b : "");
}
function label(key) {
  const [f, a, b] = LINES[key];
  return SHORT[f] + " " + a + (b > a ? "〜" + b : "") + "行";
}
function ref(key, text) {
  return `<a class="ref" href="${url(key)}" target="_blank" rel="noopener">${label(key)}${text ? "｜" + text : ""} ↗</a>`;
}
/* 表にない行は、ファイル名と行番号で直接リンクする */
function refL(f, a, b, text) {
  const u = REPO + F[f] + "#L" + a + (b > a ? "-L" + b : "");
  return `<a class="ref" href="${u}" target="_blank" rel="noopener">${SHORT[f]} ${a}${b > a ? "〜" + b : ""}行${text ? "｜" + text : ""} ↗</a>`;
}
function esc(s) { return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

/* 説明用の例の商品（班の DB のデータではない） */
const SAMPLE = [
  { id: "EX01", category: "食品", brand: "みなと製菓", name: "ありがとうの焼き菓子 12個入", price: 3240, rating: 4.6, reviewCount: 128, sales: 920, wrap: true, words: "焼き菓子 お菓子 送別 個包装" },
  { id: "EX02", category: "生活雑貨", brand: "ふわり織", name: "今治のフェイスタオル 2枚", price: 3850, rating: 4.4, reviewCount: 86, sales: 870, wrap: false, words: "タオル 今治" },
  { id: "EX03", category: "コスメ", brand: "Lumi", name: "ハンドクリーム 3本セット", price: 2980, rating: 4.2, reviewCount: 64, sales: 760, wrap: false, words: "ハンドクリーム 送別" },
  { id: "EX04", category: "食品", brand: "茶の間", name: "季節の緑茶ティーバッグ", price: 2160, rating: 4.7, reviewCount: 41, sales: 640, wrap: true, words: "お茶 個包装" },
  { id: "EX05", category: "生活雑貨", brand: "TOKIO", name: "名入れタンブラー", price: 4980, rating: 4.1, reviewCount: 210, sales: 610, wrap: false, words: "タンブラー 名入れ 送別" },
  { id: "EX06", category: "食品", brand: "夜景珈琲", name: "ドリップコーヒー 20袋", price: 3600, rating: 4.5, reviewCount: 172, sales: 580, wrap: true, words: "コーヒー 個包装 お礼" },
  { id: "EX07", category: "コスメ", brand: "Lumi", name: "入浴剤ギフト 8個入", price: 2420, rating: 3.9, reviewCount: 33, sales: 450, wrap: true, words: "入浴剤 個包装" },
  { id: "EX08", category: "生活雑貨", brand: "ふわり織", name: "バスタオル 1枚", price: 5500, rating: 4.8, reviewCount: 19, sales: 300, wrap: false, words: "タオル バスタオル" },
  { id: "EX09", category: "食品", brand: "みなと製菓", name: "ひとくちバウムクーヘン 10個", price: 4320, rating: 4.3, reviewCount: 95, sales: 540, wrap: true, words: "お菓子 個包装 送別 お礼" },
  { id: "EX10", category: "生活雑貨", brand: "TOKIO", name: "ガーゼタオルセット", price: 6200, rating: 4.6, reviewCount: 58, sales: 260, wrap: false, words: "タオル ガーゼ" },
  { id: "EX11", category: "食品", brand: "夜景珈琲", name: "新作ドリップバッグ お試し5袋", price: 1680, rating: null, reviewCount: 0, sales: 40, wrap: true, words: "コーヒー 新商品 個包装" },
];

/* 例の商品で、本物と同じ考え方の検索をする（在庫あり・キーワードは全部を含む・人気順） */
function searchSample(c, opt = {}) {
  const limit = opt.limit ?? 20;
  const order = opt.order ?? "sales";
  let r = SAMPLE.filter(g => {
    const hay = g.name + " " + g.brand + " " + g.words;
    if (c.keyword && !c.keyword.split(/\s+/).filter(Boolean).every(w => hay.includes(w))) return false;
    if (c.category && g.category !== c.category) return false;
    if (c.indivWrap && !g.wrap) return false;
    if (c.priceBand === "3000" && !(g.price >= 3000 && g.price <= 4999)) return false;
    if (c.priceBand === "5000" && !(g.price >= 5000 && g.price <= 9999)) return false;
    return true;
  });
  const by = { sales: (x, y) => y.sales - x.sales, price: (x, y) => x.price - y.price, rating: (x, y) => (y.rating ?? -1) - (x.rating ?? -1), reviews: (x, y) => y.reviewCount - x.reviewCount }[order];
  return { total: r.length, results: r.sort(by).slice(0, limit) };
}

function cardHTML(g, i, opt = {}) {
  const yen = opt.price === "plain" ? g.price + "円" : opt.price === "yen" ? "¥" + g.price.toLocaleString() : g.price.toLocaleString() + "円";
  return `<div class="gc"><p class="gmeta">${i + 1}位・${esc(g.category)}・${esc(g.brand)}</p><p class="gn">${esc(g.name)}</p><p class="gp">${yen}</p><p class="gmeta">評価${g.rating ?? " 不明"}（${g.reviewCount}件）</p>${opt.extra ? opt.extra(g) : ""}</div>`;
}

/* ページ下の地図ナビ */
const PAGES = [
  ["map.html", "🗺 地図の入口"], ["setup.html", "💻 初回セットアップ"], ["overview.html", "アプリの全体像"], ["vision.html", "目指すアプリの姿"], ["screen.html", "画面の地図"], ["flow.html", "動きの地図"], ["change.html", "変える地図"],
  ["data.html", "データの地図"], ["files.html", "ファイルの地図"], ["words.html", "ことばの地図"],
  ["trouble.html", "困ったときの地図"], ["git.html", "GitHub の地図"], ["assignments.html", "📋 課題まとめ"], ["callback-map.html", "mapとコールバック関数"],
];
document.addEventListener("DOMContentLoaded", () => {
  const nav = document.getElementById("mapnav");
  if (nav) nav.insertAdjacentHTML("beforebegin", `<p class="muted">giftia は2026/11/12からPublic（公開）。行のリンクが開けないときは、コードの変更で行番号がずれていないか <span class="mono">assets/map.js</span> の LINES 表を確認してください。</p>`);
  if (nav) nav.innerHTML = PAGES.map(([h, t]) => `<a class="btn${location.pathname.endsWith(h) ? " pink" : ""}" href="${h}">${t}</a>`).join(" ") + ` <a class="btn" href="./">ハブにもどる</a>`;
});
