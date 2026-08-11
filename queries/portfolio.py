PORTFOLIO = """
SELECT
    gval_firmanteunocargarapida     AS Firmante,
    gval_firmanteunocuitcargarapida AS 'Cuit Librador',
    gval_fechavaloroperacioncompra  AS 'Fecha Compra',
    gval_fechapago                  AS 'Fecha Pago',
    gval_importe                    AS Importe,
    gval_empresaname                AS Cliente,
    statuscodename                  AS Estado,
    gval_cuentapropiadestinoname    AS 'Cuenta Destino'
FROM gval_cheque
WHERE gval_fechapago >= DATEADD(day, -10, CAST(GETDATE() AS date))
  AND statuscodename IN (
    'Pendiente de pago', 'En cartera', 'Pendiente', 'Vendido', 'Depositado'
)
ORDER BY gval_fechapago
"""