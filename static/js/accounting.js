(function () {
  if (typeof XLSX === "undefined") return;

  const cards = Array.from(document.querySelectorAll(".table-card"));
  const fromInput = document.getElementById("acc-from");
  const toInput = document.getElementById("acc-to");
  const downloadAllBtn = document.getElementById("download-all");

  const env = downloadAllBtn ? downloadAllBtn.dataset.env || "" : "";

  const pad = (n) => ("0" + n).slice(-2);
  const iso = (d) => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());

  function slug(s) {
    return (s || "")
      .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .toLowerCase().trim()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function fileName(base) {
    return base + (env ? "-" + env : "") + ".xlsx";
  }

  const today = new Date();
  const from = new Date();
  from.setDate(from.getDate() - 14);
  if (fromInput) fromInput.value = iso(from);
  if (toInput) toInput.value = iso(today);

  function visibleRowCount(card) {
    const table = card.querySelector("table");
    if (!table) return 0;
    let count = 0;
    table.querySelectorAll("tbody tr").forEach(function (tr) {
      if (tr.style.display !== "none") count++;
    });
    return count;
  }

  function applyFilter() {
    const f = fromInput ? fromInput.value : "";
    const t = toInput ? toInput.value : "";
    cards.forEach(function (card) {
      const table = card.querySelector("table");
      let count = 0;
      if (table) {
        table.querySelectorAll("tbody tr").forEach(function (tr) {
          const d = tr.dataset.fecha;
          const show = !d || ((!f || d >= f) && (!t || d <= t));
          tr.style.display = show ? "" : "none";
          if (show) count++;
        });
      }
      const badge = card.querySelector(".row-count");
      if (badge) badge.textContent = count;
      const btn = card.querySelector(".download-one");
      if (btn) btn.disabled = count === 0;
    });
  }

  function sheetName(title) {
    return title.replace(/[\[\]:*?/\\]/g, "").slice(0, 31);
  }

  function tableToAOA(table) {
    const headers = Array.from(table.querySelectorAll("thead th")).map((th) => th.textContent.trim());
    const numeric = [];
    headers.forEach(function (h, i) {
      if (h === "DEBE" || h === "HABER") numeric.push(i);
    });
    const aoa = [headers];
    table.querySelectorAll("tbody tr").forEach(function (tr) {
      if (tr.style.display === "none") return;
      const cells = Array.from(tr.children).map(function (td, i) {
        const text = td.textContent.trim();
        if (numeric.indexOf(i) !== -1) {
          const n = parseFloat(text.replace(/[^0-9.\-]/g, ""));
          return isNaN(n) ? text : n;
        }
        return text;
      });
      aoa.push(cells);
    });
    return aoa;
  }

  function appendSheet(wb, card) {
    const table = card.querySelector("table");
    if (!table || visibleRowCount(card) === 0) return false;
    XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(tableToAOA(table)), sheetName(card.dataset.title));
    return true;
  }

  function downloadCard(card) {
    const wb = XLSX.utils.book_new();
    if (appendSheet(wb, card)) XLSX.writeFile(wb, fileName(slug(card.dataset.title)));
  }

  function downloadAll() {
    const wb = XLSX.utils.book_new();
    let added = 0;
    cards.forEach(function (card) {
      if (appendSheet(wb, card)) added++;
    });
    if (added) XLSX.writeFile(wb, fileName("asientos"));
  }

  [fromInput, toInput].forEach(function (el) {
    if (el) el.addEventListener("change", applyFilter);
  });
  cards.forEach(function (card) {
    const btn = card.querySelector(".download-one");
    if (btn) btn.addEventListener("click", function () { downloadCard(card); });
  });
  if (downloadAllBtn) downloadAllBtn.addEventListener("click", downloadAll);

  applyFilter();
})();