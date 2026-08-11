(function () {
  const els = {
    cuit: document.getElementById("f-cuit"),
    firmante: document.getElementById("f-firmante"),
    cliente: document.getElementById("f-cliente"),
    guaranteed: document.getElementById("guaranteed"),
    count: document.getElementById("count"),
    totalFixed: document.getElementById("total-fixed"),
    totalFiltered: document.getElementById("total-filtered"),
    totalFilteredPill: document.getElementById("total-filtered-pill"),
    origenLabel: document.getElementById("origen-label"),
    estadoLabel: document.getElementById("estado-label"),
  };
  const tbody = document.getElementById("rows");
  const rows = Array.from(tbody.querySelectorAll("tr"));
  const headers = Array.from(document.querySelectorAll("th.sortable"));
  const origenBoxes = Array.from(document.querySelectorAll(".origen-check"));
  const estadoBoxes = Array.from(document.querySelectorAll(".estado-check"));

  const origenClassByValue = {};
  origenBoxes.forEach(function (b) {
    const tag = b.closest(".form-check").querySelector(".tag");
    const cls = tag ? Array.from(tag.classList).find((c) => c.indexOf("origen-") === 0) : null;
    if (cls) origenClassByValue[b.value] = cls;
  });

  const onlyDigits = (s) => (s || "").replace(/\D/g, "");

  function formatAmount(n) {
    return "$" + n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  rows.forEach(function (tr) {
    tr.dataset.cuitNorm = onlyDigits(tr.dataset.cuit);
  });

  document.querySelectorAll(".js-amount").forEach(function (td) {
    const raw = parseFloat(td.closest("tr").dataset.amount) || 0;
    td.textContent = formatAmount(raw);
  });

  function isGuaranteed(tr) {
    return tr.dataset.account === "5005" && tr.dataset.state === "Vendido";
  }

  function selectedOrigins() {
    return origenBoxes.filter((b) => b.checked).map((b) => b.value);
  }

  function selectedStates() {
    return estadoBoxes.filter((b) => b.checked).map((b) => b.value);
  }

  function sumCents(list) {
    let cents = 0;
    list.forEach(function (tr) {
      cents += Math.round((parseFloat(tr.dataset.amount) || 0) * 100);
    });
    return cents;
  }

  function apply() {
    const onlyGuaranteed = els.guaranteed && els.guaranteed.checked;
    const cuitQ = onlyDigits(els.cuit.value);
    const firmanteQ = els.firmante.value.trim().toLowerCase();
    const clienteQ = els.cliente.value.trim().toLowerCase();
    const origins = selectedOrigins();
    const states = selectedStates();

    const base = rows.filter((tr) => !onlyGuaranteed || isGuaranteed(tr));
    els.totalFixed.textContent = formatAmount(sumCents(base) / 100);

    const visible = [];
    rows.forEach(function (tr) {
      const inBase = !onlyGuaranteed || isGuaranteed(tr);
      const okCuit = !cuitQ || tr.dataset.cuitNorm.indexOf(cuitQ) !== -1;
      const okFirmante = !firmanteQ || tr.dataset.firmante.indexOf(firmanteQ) !== -1;
      const okCliente = !clienteQ || tr.dataset.cliente.indexOf(clienteQ) !== -1;
      const okOrigen = origins.length === 0 || origins.indexOf(tr.dataset.origen) !== -1;
      const okEstado = states.length === 0 || states.indexOf(tr.dataset.state) !== -1;
      const show = inBase && okCuit && okFirmante && okCliente && okOrigen && okEstado;
      tr.style.display = show ? "" : "none";
      if (show) visible.push(tr);
    });

    els.totalFiltered.textContent = formatAmount(sumCents(visible) / 100);
    els.count.textContent = visible.length;
    els.origenLabel.textContent = origins.length ? "Origen (" + origins.length + ")" : "Origen";
    els.estadoLabel.textContent = states.length ? "Estado (" + states.length + ")" : "Estado";

    const pill = els.totalFilteredPill;
    Object.values(origenClassByValue).forEach((c) => pill.classList.remove(c));
    if (origins.length === 1 && origenClassByValue[origins[0]]) {
      pill.classList.add(origenClassByValue[origins[0]]);
    }
  }

  function sortValue(tr, index, type) {
    const cell = tr.children[index];
    const text = cell.textContent.trim();
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
    sortDir = sortIndex === index ? -sortDir : 1;
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
        i === index ? (sortDir === 1 ? "▲" : "▼") : "";
    });
  }

  headers.forEach(function (th, index) {
    th.addEventListener("click", function () {
      sortBy(index, th.dataset.type || "text");
    });
  });

  [els.cuit, els.firmante, els.cliente].forEach(function (el) {
    if (el) el.addEventListener("input", apply);
  });
  if (els.guaranteed) els.guaranteed.addEventListener("change", apply);
  origenBoxes.forEach(function (b) { b.addEventListener("change", apply); });
  estadoBoxes.forEach(function (b) { b.addEventListener("change", apply); });

  apply();
})();