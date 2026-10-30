from datetime import date

import pytest

from modules.portfolio_historic import bolsa


def _record(**cambios):
    base = {
        "Empresa": "SC1",
        "FIRMANTE": "BARPRAN SRL",
        "CUIT Librador": "30-71211651-6",
        "Fecha Acr.": "15/8/2023",
        "Fecha Cpra.": "28/7/2023",
        "Importe": "5272727.27",
        "Cliente": "mesa",
        "Estado": "ACREDITADO",
        "TASA MERCADO": "0.5421",
    }
    base.update(cambios)
    return base


@pytest.fixture(autouse=True)
def cache_limpio():
    bolsa._cache.clear()
    yield
    bolsa._cache.clear()


def test_normalize_maps_the_sheet_columns():
    row = bolsa.normalize([_record()])[0]
    assert row["Empresa"] == "SC1"
    assert row["Firmante"] == "BARPRAN SRL"
    assert row["Cliente"] == "mesa"
    assert row["Estado"] == "ACREDITADO"


def test_normalize_tags_the_origin():
    assert bolsa.normalize([_record()])[0]["Origen"] == "BOLSA"


def test_normalize_reads_day_first_dates():
    row = bolsa.normalize([_record()])[0]
    assert row["Fecha Compra"] == date(2023, 7, 28)
    assert row["Fecha Acr."] == date(2023, 8, 15)


def test_normalize_turns_the_rate_into_a_percentage():
    assert bolsa.normalize([_record()])[0]["Tasa"] == pytest.approx(54.21)


def test_normalize_reads_the_amount_as_a_number():
    assert bolsa.normalize([_record()])[0]["Importe"] == pytest.approx(5272727.27)


def test_normalize_drops_the_checks_we_sold_to_the_market():
    records = [_record(Cliente="DHF S.A"), _record(Cliente="CONFINANCE S.A."), _record(Cliente="mesa")]
    assert [row["Cliente"] for row in bolsa.normalize(records)] == ["mesa"]


def test_normalize_skips_empty_rows():
    vacio = {clave: "" for clave in _record()}
    assert bolsa.normalize([vacio]) == []


def test_normalize_leaves_a_broken_date_empty_without_dropping_the_row():
    row = bolsa.normalize([_record(**{"Fecha Acr.": "sin fecha"})])[0]
    assert row["Fecha Acr."] is None and row["Fecha Compra"] == date(2023, 7, 28)


FILTROS = {"desde": "2023-01-01", "hasta": "2023-12-31"}


def _row(**cambios):
    return bolsa.normalize([_record(**cambios)])[0]


def test_matches_accepts_a_row_inside_the_range():
    assert bolsa.matches(_row(), FILTROS)


def test_matches_rejects_a_row_outside_the_range():
    assert not bolsa.matches(_row(**{"Fecha Cpra.": "28/7/2022"}), FILTROS)


def test_matches_rejects_a_row_without_purchase_date():
    assert not bolsa.matches(_row(**{"Fecha Cpra.": "sin fecha"}), FILTROS)


def test_matches_filters_by_state():
    assert bolsa.matches(_row(), {**FILTROS, "estados": ["ACREDITADO"]})
    assert not bolsa.matches(_row(), {**FILTROS, "estados": ["CARTERA"]})


def test_matches_filters_by_client_ignoring_case():
    assert bolsa.matches(_row(), {**FILTROS, "cliente": "MESA"})
    assert not bolsa.matches(_row(), {**FILTROS, "cliente": "otra"})


def test_matches_filters_by_signer():
    assert bolsa.matches(_row(), {**FILTROS, "firmante": "barpran"})


def test_matches_filters_by_cuit_ignoring_dashes():
    assert bolsa.matches(_row(), {**FILTROS, "cuit": "30712116516"})
    assert bolsa.matches(_row(), {**FILTROS, "cuit": "71211"})
    assert not bolsa.matches(_row(), {**FILTROS, "cuit": "99999"})


def test_totals_add_up_the_filtered_rows(monkeypatch):
    monkeypatch.setattr(bolsa, "HISTORIC_BOLSA_SHEET_ID", "una-planilla")
    monkeypatch.setattr(bolsa, "read_tab_records",
                        lambda sheet_id, gid: [_record(), _record(Importe="1000")])
    assert bolsa.totals(FILTROS) == {"cantidad": 2, "total": pytest.approx(5273727.27)}


def test_load_reads_the_sheet_only_once(monkeypatch):
    lecturas = []
    monkeypatch.setattr(bolsa, "HISTORIC_BOLSA_SHEET_ID", "una-planilla")
    monkeypatch.setattr(bolsa, "read_tab_records",
                        lambda sheet_id, gid: lecturas.append(1) or [_record()])
    bolsa.load(now=1000)
    bolsa.load(now=1100)
    assert len(lecturas) == 1


def test_load_reads_again_once_the_cache_expires(monkeypatch):
    lecturas = []
    monkeypatch.setattr(bolsa, "HISTORIC_BOLSA_SHEET_ID", "una-planilla")
    monkeypatch.setattr(bolsa, "read_tab_records",
                        lambda sheet_id, gid: lecturas.append(1) or [_record()])
    bolsa.load(now=1000)
    bolsa.load(now=1000 + bolsa.CACHE_SECONDS + 1)
    assert len(lecturas) == 2


def test_load_without_sheet_id_returns_nothing(monkeypatch):
    monkeypatch.setattr(bolsa, "HISTORIC_BOLSA_SHEET_ID", "")
    assert bolsa.load() == []


def test_normalize_uses_the_same_state_words_as_the_crm():
    estados = [bolsa.normalize([_record(Estado=e)])[0]["Estado"] for e in ("CARTERA", "VENDIDO")]
    assert estados == ["En cartera", "Vendido"]


def test_normalize_keeps_the_states_that_only_exist_in_the_sheet():
    estados = [bolsa.normalize([_record(Estado=e)])[0]["Estado"] for e in bolsa.BOLSA_STATES]
    assert estados == list(bolsa.BOLSA_STATES)


def test_matches_filters_by_the_translated_state():
    fila = bolsa.normalize([_record(Estado="CARTERA")])[0]
    assert bolsa.matches(fila, {**FILTROS, "estados": ["En cartera"]})
    assert not bolsa.matches(fila, {**FILTROS, "estados": ["CARTERA"]})
