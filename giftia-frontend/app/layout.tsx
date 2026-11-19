import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Giftia",
  description: "送別ギフトを、仲間と納得して決められるギフト検索",
};

// 文字はハブサイトと同じ丸ゴシック（M PLUS Rounded 1c）。ブラウザが Google Fonts から読み込む。
// next/font はビルドのときに日本語フォントを数百ファイル取りに行き、時間切れで失敗しやすいので使わない。
// 読み込めないときは globals.css の --font の続き（ヒラギノ・メイリオなど）で表示される
const FONT_URL = "https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;700;800&display=swap";

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ja">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="stylesheet" href={FONT_URL} />
      </head>
      <body>{children}</body>
    </html>
  );
}
