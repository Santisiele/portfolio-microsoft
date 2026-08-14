DEPOSITS = """
SELECT gval_numerodedeposito,
    gval_fechaconfirmacion,
    gval_cuentapropiadestinoname,
    gval_fechadedeposito,
    gval_observaciones,
    gval_numtransaccionboletarealdedeposito,
    gval_cantidadchequesincluidos,
    gval_importetotalcheques
    FROM gval_operaciondedeposito
WHERE gval_fechaconfirmacion >= DATEADD(DAY, -14, GETDATE())
ORDER BY gval_fechaconfirmacion DESC
"""

SALES = """
SELECT gval_numerodeventa,
    gval_fechaconfirmacion,
    gval_cuentapropiadestinoname,
    gval_tiponame,
    gval_fechavalor,
    gval_tasainteres,
    gval_tasacomision,
    gval_observaciones,
    gval_fechadeoperacion,
    gval_fechadeacreditacion,
    gval_cantidadchequesincluidos,
    gval_importetotalcheques
FROM gval_ventadecheques 
WHERE gval_fechaconfirmacion >= DATEADD(DAY, -14, GETDATE())
ORDER BY gval_fechaconfirmacion DESC
"""

REJECTED = """
SELECT gval_chequerechazado.gval_numerodeoperacion,
    gval_chequerechazado.gval_importe,
    gval_chequerechazado.gval_gastos,
    gval_chequerechazado.gval_iva,
    gval_chequerechazado.gval_cuentacorrientename,
    gval_chequerechazado.gval_fechadeconfirmacion,
    gval_chequerechazado.gval_numcheque,
    gval_cheque.gval_cuentapropiadestinoname AS Cuenta}
FROM gval_chequerechazado
INNER JOIN gval_cheque
ON gval_chequerechazado.gval_cheque = gval_cheque.gval_chequeid
WHERE gval_chequerechazado.gval_fechadeconfirmacion >= DATEADD(DAY, -14, GETDATE())
ORDER BY gval_chequerechazado.gval_fechadeconfirmacion DESC
""""

PENDING = """
SELECT gval_numerodeoperacion,
    gval_fechadeconfirmacion,
    gval_importe,
    gval_cuentacorrientename,
    gval_numcheque
FROM gval_chequependiente
WHERE gval_fechadeconfirmacion >= DATEADD(DAY, -14, GETDATE())
ORDER BY gval_fechadeconfirmacion DESC
"""

PAYMENTS = """
"SELECT  gval_numoperacion,
    gval_empresaname, 
    gval_importe,
    gval_fechaconfirmacion
FROM gval_operacionpagoalcliente
WHERE statuscodename = 'Pagada' 
AND gval_tiponame = 'Adelanto'
AND gval_fechaconfirmacion >= DATEADD(DAY, -14, GETDATE())
ORDER BY gval_fechaconfirmacion DESC
"""

TAX_DOCUMENTS = """
SELECT
    gval_tipodocumentoname AS 'Tipo documento',
    gval_importetotal AS 'Importe',
    gval_ivatotal AS 'Iva',
    gval_empresaname AS 'Empresa',
    gval_fechaconfirmacion AS 'Fecha',
    gval_operaciondocumentofiscalid AS 'Id'
FROM gval_operaciondocumentofiscal
WHERE gval_fechaconfirmacion >= DATEADD(DAY, -14, GETDATE())
ORDER BY gval_fechaconfirmacion DESC;
"""

COLLECTIONS = """
SELECT 
	gval_importe AS 'Importe',
	gval_fechadeconfirmacion AS 'Fecha',
	gval_cuentacorrientename AS 'Empresa'
FROM gval_cobranza
WHERE gval_fechadeconfirmacion >= DATEADD(DAY, -14, GETDATE())
ORDER BY gval_fechadeconfirmacion DESC
"""

OPERATIONS = """
SELECT
    gval_bruto AS 'Bruto',
    gval_comision AS 'Comision',
    gval_interes AS 'Intereses',
	gval_interior AS 'Interior',
    gval_numeral AS 'Numeral',
	gval_iva AS 'Iva',
	gval_netooperativo AS 'Neto operativo',
	gval_saldoadescontar AS 'Saldo a descontar',
	gval_netofinal AS 'Neto final',
    gval_fechavalor AS 'Fecha',
    statuscodename AS 'Estado',
    gval_empresaname AS 'Nombre cliente',
	gval_cuentasdestino AS 'Cuenta destino',
    gval_operacioncomprachequesid AS 'Id'
FROM gval_operacioncompracheques
WHERE
    gval_fechavalor >= DATEFROMPARTS(YEAR(GETDATE()), 1, 1)
    AND statuscodename = 'Pagada'
ORDER BY gval_fechavalor;
"""