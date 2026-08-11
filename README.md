# Cartera CRM

API + front en Flask que consulta datos de Dynamics 365 / Dataverse por SQL,
consolidando dos entornos (DHF y CONFINANCE) y mostrándolos en un tablero web.

## Cómo funciona

El usuario entra a la web e **inicia sesión con su cuenta de Microsoft** (con MFA).
Flask usa ese login (flujo Authorization Code de Entra) para obtener un **token del
usuario**, y con ese token consulta el **endpoint TDS** de Dataverse por SQL, igual
que SSMS pero desde código.

Cada consulta se corre en **los dos entornos** y se consolida en una sola respuesta,
agregando una columna `Origen` (`DHF` / `CONFINANCE`) para saber de dónde vino cada fila.

```
Navegador  --(login + MFA)-->  Entra ID  -->  token del usuario
   |                                              |
   v                                              v
Flask (front + API)  --(token + SQL)-->  Dataverse TDS (DHF y CONFINANCE)
```

## Estructura

```
app.py            Punto de entrada: crea la app y registra los blueprints
config.py         Variables de entorno y entornos de Dataverse

core/             Plomería (no se toca casi nunca)
  auth.py           Login con Microsoft (MSAL)
  db.py             Consultas SQL + consolidación de entornos + reintentos

domain/           Transformaciones estilo Power BI (pandas)
  date_table.py     Tabla calendario + días hábiles bancarios
  measures.py       Cálculos reutilizables (measures)

queries/          Las consultas SQL, por tema
  portfolio.py

routes/           Endpoints (un blueprint por tema)
  main.py           Home
  auth.py           Login / logout / callback
  portfolio.py      /portfolio (JSON) y /portfolio/table (HTML)

templates/        HTML (base.html + páginas que lo extienden)
static/           CSS / JS
tests/            Unit + tests de rutas
```

**Flujo de un endpoint:** `queries/` (el SQL) → `core.db` (lo corre) →
`domain/` (lo transforma) → `routes/` (responde JSON o HTML).

## Requisitos

- Python 3.11+
- ODBC Driver 18 for SQL Server (para `pyodbc`)
- Una App Registration en Entra con:
  - plataforma **Web** con redirect URI `http://localhost:5000/getAToken`
  - permiso delegado **Dynamics CRM → user_impersonation**

## Configuración

Copiá `.env.example` a `.env` y completá:

```
TENANT_ID=...
CLIENT_ID=...
CLIENT_SECRET=...
DHF_URL=https://dhf.crm2.dynamics.com
CONFINANCE_URL=https://confinance.crm2.dynamics.com
FLASK_SECRET_KEY=una-cadena-larga-y-secreta
```

## Correr local

```
pip install -r requirements.txt
python app.py
```

Abrí http://localhost:5000, iniciá sesión, y entrá a la cartera.

## Tests

```
python -m pytest
```

Los unit tests no tocan el CRM (mockean la capa de datos). Los de integración
(contra un entorno real, ej. CONFINANCE TEST) se marcan con `@pytest.mark.integration`
y se corren aparte: `pytest -m integration`.

## Deploy (Render)

El `Dockerfile` instala el ODBC Driver 18 (que en Render no viene). Al desplegar:

1. Subí el repo y creá un Web Service en Render (usa el Dockerfile).
2. Cargá las mismas variables de entorno del `.env`.
3. Agregá en Azure la redirect URI de Render: `https://<tu-app>.onrender.com/getAToken`.

## Atajos (Makefile)

`make install` · `make run` · `make test` · `make docker-build` · `make docker-run`