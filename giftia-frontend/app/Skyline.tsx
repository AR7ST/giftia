// app/Skyline.tsx — ヘッダーの街並み（飾り）。東京タワー・レインボーブリッジ・スカイツリーの自作シルエット。
// 写真やロゴは使っていない。色は globals.css の --skyline-* で変えられる
export default function Skyline() {
  return (
    <svg className="skyline" viewBox="0 0 960 200" preserveAspectRatio="xMidYMax meet" aria-hidden="true" focusable="false">
      {/* ビル（左は低くして、タイトルの文字と重ならないようにする） */}
      <g className="skyline-bldg">
        <rect x="0" y="150" width="40" height="50" />
        <rect x="44" y="138" width="34" height="62" />
        <rect x="82" y="156" width="30" height="44" />
        <rect x="116" y="144" width="30" height="56" />
        <rect x="150" y="160" width="36" height="40" />
        <rect x="190" y="146" width="30" height="54" />
        <rect x="224" y="152" width="40" height="48" />
        <rect x="268" y="140" width="32" height="60" />
        <rect x="372" y="150" width="30" height="50" />
        <rect x="748" y="120" width="34" height="80" />
        <rect x="786" y="135" width="28" height="65" />
        <rect x="864" y="110" width="40" height="90" />
        <rect x="908" y="130" width="52" height="70" />
      </g>
      {/* 東京タワー */}
      <g className="skyline-tower">
        <path fillRule="evenodd" d="M316 200 L337 62 L343 62 L364 200 Z M328 200 L340 166 L352 200 Z" />
        <rect x="323" y="136" width="34" height="7" rx="2" />
        <rect x="330" y="96" width="20" height="6" rx="2" />
        <rect x="339" y="20" width="2" height="44" />
      </g>
      {/* レインボーブリッジ */}
      <g className="skyline-bridge-line" fill="none" strokeLinecap="round">
        <path d="M410 170 Q465 150 495 104" />
        <path d="M495 104 Q575 168 655 104" />
        <path d="M655 104 Q685 150 740 170" />
        <path d="M535 142 V170 M575 152 V170 M615 142 V170 M450 160 V170 M700 160 V170" strokeWidth="1.2" />
      </g>
      <g className="skyline-bridge">
        <rect x="410" y="170" width="330" height="5" rx="2" />
        <rect x="491" y="100" width="8" height="100" />
        <rect x="651" y="100" width="8" height="100" />
        <rect x="487" y="128" width="16" height="3" />
        <rect x="647" y="128" width="16" height="3" />
      </g>
      {/* 東京スカイツリー */}
      <g className="skyline-tree">
        <polygon points="824,200 856,200 843,38 837,38" />
        <rect x="828" y="96" width="24" height="9" rx="3" />
        <rect x="832" y="66" width="16" height="6" rx="2" />
        <rect x="839" y="0" width="2" height="40" />
      </g>
    </svg>
  );
}
