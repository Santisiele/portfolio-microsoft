GUARANTEED_AMOUNT = """
SELECT SUM(gval_importe) as Garantizado, gval_fechapago as Fecha
FROM gval_cheque
WHERE gval_fechapago >= DATEADD(day, -10, CAST(GETDATE() AS date))
  AND (statuscodename = 'Vendido' and (gval_cuentapropiadestinoname = '5005'))
GROUP BY gval_fechapago
"""

CHECKING_ACCOUNT = """
SELECT sum(gval_saldo) as 'Cuenta corriente' FROM gval_cuentacorriente WHERE conf_nombreempresa <> 'PREMIUM BEDS SA'
"""