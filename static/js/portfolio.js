(function () {
  const search = document.getElementById("search");
  const countEl = document.getElementById("count");
  const totalEl = document.getElementById("total");
  const tbody = document.getElementById("rows");
  const rows = Array.from(tbody.querySelectorAll("tr"));
  const headers = Array.from(document.querySelectorAll("th.sortable"));

  function formatAmount(n) {
    return "$" + n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  document.querySelectorAll(".js-amount").forEach(function (td) {
    const raw = parseFloat(td.closest("tr").dataset.amount) || 0;
    td.textContent = formatAmount(raw);
  });

  function recalc() {
    let cents = 0;
    let visible = 0;
    rows.forEach(function (tr) {
      if (tr.style.display !== "none") {
        cents += Math.round((parseFloat(tr.dataset.amount) || 0) * 100);
        visible += 1;
      }
    });
    totalEl.textContent = formatAmount(cents / 100);
    countEl.textContent = visible;
  }

  function applyFilter() {
    const q = search.value.trim().toLowerCase();
    rows.forEach(function (tr) {
      tr.style.display = tr.dataset.text.indexOf(q) !== -1 ? "" : "none";
    });
    recalc();
  }

  function sortValue(tr, index, type) {
    const text = tr.children[index].textContent.trim();
    if (type === "number") {
      return parseFloat(text.replace(/[^0-9.\-]/g, "")) || 0;
    }
    if (type === "date") {
      const p = text.split("/");
      return p.length === 3 ? p[2] + p[1] + p[0] : "";
    }
    return text.toLowerCase();
  }

  let sortIndex = null;
  let sortDir = 1;

  function sortBy(index, type) {
    sortDir = (sortIndex === index) ? -sortDir : 1;
    sortIndex = index;
    rows.sort(function (a, b) {
      const va = sortValue(a, index, type);
      const vb = sortValue(b, index, type);
      if (va < vb) return -sortDir;
      if (va > vb) return sortDir;
      return 0;
    });
    rows.forEach(function (tr) { tbody.appendChild(tr); });
    headers.forEach(function (th, i) {
      th.querySelector(".sort-ind").textContent =
        (i === index) ? (sortDir === 1 ? "▲" : "▼") : "";
    });
  }

  headers.forEach(function (th, index) {
    th.addEventListener("click", function () {
      sortBy(index, th.dataset.type || "text");
    });
  });

  if (search) search.addEventListener("input", applyFilter);
  recalc();
})();