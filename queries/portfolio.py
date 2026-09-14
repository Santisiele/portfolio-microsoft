PORTFOLIO = """
SELECT
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
FROM gval_cheque
LEFT JOIN gval_operacioncompracheques ON gval_cheque.conf_nrooperacion = gval_operacioncompracheques.gval_numoperacion
WHERE gval_cheque.gval_fechapago >= DATEADD(day, -10, CAST(GETDATE() AS date))
  AND gval_cheque.statuscodename IN (
    'Pendiente de depósito', 'En cartera', 'Pendiente', 'Vendido', 'Depositado'
)
ORDER BY gval_cheque.gval_fechapago
"""