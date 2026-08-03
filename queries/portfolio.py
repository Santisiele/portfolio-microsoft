PORTFOLIO = """
SELECT
    gval_firmanteunocargarapida     AS firmante,
    gval_firmanteunocuitcargarapida AS cuit_librador,
    gval_fechavaloroperacioncompra  AS fecha_compra,
    gval_fechapago                  AS fecha_pago,
    gval_importe                    AS importe,
    gval_empresaname                AS cliente,
    gval_chequeid                   AS id,
    statuscodename                  AS estado,
    gval_cuentapropiadestinoname    AS cuenta_destino
FROM gval_cheque
WHERE statuscodename IN (
    'Pendiente de pago', 'En cartera', 'Pendiente', 'Vendido', 'Depositado'
)
"""