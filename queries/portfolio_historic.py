COLUMNS = """
    gval_cheque.gval_firmanteunocargarapida       AS Firmante,
    gval_cheque.gval_firmanteunocuitcargarapida   AS 'Cuit Librador',
    gval_cheque.gval_fechavaloroperacioncompra    AS 'Fecha Compra',
    gval_cheque.gval_fechapago                    AS 'Fecha Pago',
    gval_cheque.gval_importe                      AS Importe,
    gval_cheque.gval_empresaname                  AS Cliente,
    gval_cheque.statuscodename                    AS Estado,
    gval_cheque.gval_cuentapropiadestinoname      AS 'Cuenta Destino',
    gval_operacioncompracheques.gval_tasainteres  AS 'Tasa de Interes',
    gval_operacioncompracheques.gval_tasacomision AS 'Comision',
    gval_operacioncompracheques.gval_diaspromedio AS 'Dias'
"""

SOURCE = """
FROM gval_cheque
LEFT JOIN gval_operacioncompracheques ON gval_cheque.conf_nrooperacion = gval_operacioncompracheques.gval_numoperacion
"""

STATES = ("Pendiente de depósito", "En cartera", "Pendiente", "Vendido", "Depositado")

TEXT_FILTERS = {
    "cliente": "gval_cheque.gval_empresaname",
    "firmante": "gval_cheque.gval_firmanteunocargarapida",
    "cuit": "gval_cheque.gval_firmanteunocuitcargarapida",
}


def build_where(filters):
    clauses = ["gval_cheque.gval_fechavaloroperacioncompra >= ?",
               "gval_cheque.gval_fechavaloroperacioncompra <= ?"]
    params = [filters["desde"], filters["hasta"]]

    estados = filters.get("estados") or list(STATES)
    clauses.append("gval_cheque.statuscodename IN (" + ", ".join("?" for _ in estados) + ")")
    params.extend(estados)

    for nombre, columna in TEXT_FILTERS.items():
        valor = (filters.get(nombre) or "").strip()
        if valor:
            clauses.append(columna + " LIKE ?")
            params.append("%" + valor + "%")

    return " WHERE " + " AND ".join(clauses), params


def page_query(filters, offset, size):
    where, params = build_where(filters)
    query = ("SELECT" + COLUMNS + SOURCE + where +
             " ORDER BY gval_cheque.gval_fechavaloroperacioncompra DESC, gval_cheque.gval_importe DESC"
             " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY")
    return query, params + [offset, size]


def totals_query(filters):
    where, params = build_where(filters)
    query = ("SELECT COUNT(*) AS Cantidad, SUM(gval_cheque.gval_importe) AS Total" + SOURCE + where)
    return query, params
