(function () {
  const els = {
    cuit: document.getElementById("f-cuit"),
    firmante: document.getElementById("f-firmante"),
    cliente: document.getElementById("f-cliente"),
    acrFrom: document.getElementById("f-acr-from"),
    acrTo: document.getElementById("f-acr-to"),
    guaranteed: document.getElementById("guaranteed"),
    count: document.getElementById("count"),
    totalFixed: document.getElementById("total-fixed"),
    totalFiltered: document.getElementById("total-filtered"),
    totalFilteredPill: document.getElementById("total-filtered-pill"),
    originLabel: document.getElementById("origin-label"),
    companyLabel: document.getElementById("company-label"),
    stateLabel: document.getElementById("state-label"),
    reset: document.getElementById("reset-filters"),
    verManana: document.getElementById("ver-manana"),
  };
  const tbody = document.getElementById("rows");
  const rows = Array.from(tbody.querySelectorAll("tr"));
  const headers = Array.from(document.querySelectorAll("th.sortable"));
  const originBoxes = Array.from(document.querySelectorAll(".origin-check"));
  const companyBoxes = Array.from(document.querySelectorAll(".company-check"));
  const stateBoxes = Array.from(document.querySelectorAll(".state-check"));

  const originClassByValue = {};
  originBoxes.forEach(function (b) {
    const tag = b.closest(".form-check").querySelector(".tag");
    const cls = tag ? Array.from(tag.classList).find((c) => c.indexOf("origin-") === 0) : null;
    if (cls) originClassByValue[b.value] = cls;
  });

  const companiesByOrigin = {};
  rows.forEach(function (tr) {
    const o = tr.dataset.origin;
    const c = tr.dataset.company;
    if (!o || !c) return;
    (companiesByOrigin[o] = companiesByOrigin[o] || new Set()).add(c);
  });

  function syncCompanyOptions() {
    const origins = selectedOrigins();
    let allowed = null;
    if (origins.length) {
      allowed = new Set();
      origins.forEach(function (o) {
        (companiesByOrigin[o] || new Set()).forEach((c) => allowed.add(c));
      });
    }
    companyBoxes.forEach(function (b) {
      const show = !allowed || allowed.has(b.value);
      b.closest(".form-check").style.display = show ? "" : "none";
      if (!show && b.checked) b.checked = false;
    });
  }

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

  const acrDates = rows.map((tr) => tr.dataset.acr).filter(Boolean).sort();
  const acrMin = acrDates.length ? acrDates[0] : "";
  const acrMax = acrDates.length ? acrDates[acrDates.length - 1] : "";
  if (acrDates.length && els.acrFrom && els.acrTo) {
    els.acrFrom.value = acrMin;
    els.acrFrom.min = acrMin;
    els.acrFrom.max = acrMax;
    els.acrTo.min = acrMin;
    els.acrTo.max = acrMax;
  }

  function isGuaranteed(tr) {
    return tr.dataset.account === "5005" && tr.dataset.state === "Vendido";
  }

  function selectedOrigins() {
    return originBoxes.filter((b) => b.checked).map((b) => b.value);
  }

  function selectedCompanies() {
    return companyBoxes.filter((b) => b.checked && b.closest(".form-check").style.display !== "none").map((b) => b.value);
  }

  function selectedStates() {
    return stateBoxes.filter((b) => b.checked).map((b) => b.value);
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
    const acrFrom = els.acrFrom ? els.acrFrom.value : "";
    const acrTo = els.acrTo ? els.acrTo.value : "";
    const origins = selectedOrigins();
    const companies = selectedCompanies();
    const states = selectedStates();

    const base = rows.filter((tr) => !onlyGuaranteed || isGuaranteed(tr));
    els.totalFixed.textContent = formatAmount(sumCents(base) / 100);

    const visible = [];
    rows.forEach(function (tr) {
      const inBase = !onlyGuaranteed || isGuaranteed(tr);
      const okCuit = !cuitQ || tr.dataset.cuitNorm.indexOf(cuitQ) !== -1;
      const okFirmante = !firmanteQ || tr.dataset.firmante.indexOf(firmanteQ) !== -1;
      const okCliente = !clienteQ || tr.dataset.cliente.indexOf(clienteQ) !== -1;
      const okOrigin = origins.length === 0 || origins.indexOf(tr.dataset.origin) !== -1;
      const okCompany = companies.length === 0 || companies.indexOf(tr.dataset.company) !== -1;
      const okState = states.length === 0 || states.indexOf(tr.dataset.state) !== -1;
      const acr = tr.dataset.acr;
      const okAcr = !acr || ((!acrFrom || acr >= acrFrom) && (!acrTo || acr <= acrTo));
      const show = inBase && okCuit && okFirmante && okCliente && okOrigin && okCompany && okState && okAcr;
      tr.style.display = show ? "" : "none";
      if (show) visible.push(tr);
    });

    els.totalFiltered.textContent = formatAmount(sumCents(visible) / 100);
    els.count.textContent = visible.length;
    els.originLabel.textContent = origins.length ? "Origen (" + origins.length + ")" : "Origen";
    els.companyLabel.textContent = companies.length ? "Empresa (" + companies.length + ")" : "Empresa";
    els.stateLabel.textContent = states.length ? "Estado (" + states.length + ")" : "Estado";

    const pill = els.totalFilteredPill;
    Object.values(originClassByValue).forEach((c) => pill.classList.remove(c));
    if (origins.length === 1 && originClassByValue[origins[0]]) {
      pill.classList.add(originClassByValue[origins[0]]);
    }
  }

  function resetFilters() {
    els.cuit.value = "";
    els.firmante.value = "";
    els.cliente.value = "";
    originBoxes.forEach((b) => (b.checked = false));
    companyBoxes.forEach((b) => (b.checked = false));
    stateBoxes.forEach((b) => (b.checked = false));
    if (els.guaranteed) els.guaranteed.checked = false;
    if (els.acrFrom && els.acrTo && acrDates.length) {
      els.acrFrom.value = acrMin;
      els.acrTo.value = "";
    }
    syncCompanyOptions();
    apply();
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
  [els.acrFrom, els.acrTo].forEach(function (el) {
    if (el) el.addEventListener("change", apply);
  });
  if (els.guaranteed) els.guaranteed.addEventListener("change", apply);
  originBoxes.forEach(function (b) {
    b.addEventListener("change", function () {
      syncCompanyOptions();
      apply();
    });
  });
  companyBoxes.forEach(function (b) { b.addEventListener("change", apply); });
  stateBoxes.forEach(function (b) { b.addEventListener("change", apply); });
  if (els.reset) els.reset.addEventListener("click", resetFilters);
  if (els.verManana) els.verManana.addEventListener("click", function () {
    const d = els.verManana.dataset.next || acrMin;
    if (!d) return;
    if (els.acrFrom) els.acrFrom.value = d;
    if (els.acrTo) els.acrTo.value = d;
    apply();
  });

  syncCompanyOptions();
  apply();
})();