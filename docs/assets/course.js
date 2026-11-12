/* 読む順番のチェックは、このブラウザにだけ保存する。外部通信なし。 */
(() => {
  "use strict";
  const root = document.getElementById("learning-course");
  if (!root) return;
  const key = "giftia-hub:learning-course:v1";
  const checks = Array.from(root.querySelectorAll("[data-course-step]"));
  const count = root.querySelector("[data-course-count]");
  const progress = root.querySelector("progress");
  const next = root.querySelector("[data-course-next]");
  const note = root.querySelector("[data-course-storage]");
  const reset = root.querySelector("[data-course-reset]");
  let canSave = true;
  let done = new Set();
  try {
    const saved = JSON.parse(localStorage.getItem(key) || "[]");
    if (Array.isArray(saved)) {
      const valid = new Set(checks.map(input => input.dataset.courseStep));
      done = new Set(saved.filter(id => typeof id === "string" && valid.has(id)));
    }
  } catch (_) {
    canSave = false;
  }
  function render() {
    checks.forEach(input => { input.checked = done.has(input.dataset.courseStep); });
    count.textContent = done.size + " / " + checks.length + " ステップを確認済み";
    progress.max = checks.length;
    progress.value = done.size;
    const pending = checks.find(input => !input.checked);
    if (pending) {
      const link = pending.closest("li").querySelector("a");
      next.href = link.getAttribute("href");
      next.textContent = "次に読む：" + link.textContent;
    } else {
      next.href = "change.html";
      next.textContent = "全ステップ確認済み！変える地図で実践する";
    }
    note.textContent = canSave
      ? "チェックはこの端末・ブラウザに保存します。別の端末とは共有されません。閲覧履歴や班の課題進捗とは連動しません。"
      : "このブラウザでは保存できません。チェックはこのページを開いている間だけ使えます。";
    reset.disabled = done.size === 0;
  }
  function save() {
    try {
      localStorage.setItem(key, JSON.stringify(Array.from(done)));
      canSave = true;
    } catch (_) { canSave = false; }
    render();
  }
  checks.forEach(input => input.addEventListener("change", () => {
    if (input.checked) done.add(input.dataset.courseStep);
    else done.delete(input.dataset.courseStep);
    save();
  }));
  reset.addEventListener("click", () => {
    if (!window.confirm("このブラウザの学習チェックをすべて外しますか？")) return;
    done.clear();
    try {
      localStorage.removeItem(key);
      canSave = true;
    } catch (_) { canSave = false; }
    render();
  });
  render();
  root.querySelector("[data-course-controls]").hidden = false;
})();
