# Quant Desk

Estación de trabajo de derivados: curva de swaps (bootstrap con Treasury + SOFR), forwards/futuros de commodities (oro, petróleo) y opciones (árbol CRR de 10 capas vs Black-Scholes, sensibilidades y estrategias por régimen de mercado). Interfaz bilingüe EN/ES.

Datos en vivo: FRED (curva) y Yahoo Finance (futuros, opciones). Si una fuente falla, la app muestra la última lectura en vivo o, si no hay, datos DEMO marcados en la insignia del encabezado.

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run qd_app.py
```

## Desplegar en Streamlit Community Cloud

1. Sube esta carpeta a un repositorio de GitHub (público o privado).
2. Entra a https://share.streamlit.io con tu cuenta de GitHub.
3. **Create app** → elige el repositorio, la rama `main` y el archivo `qd_app.py`.
4. En **Advanced settings** elige Python 3.13 (o 3.12).
5. **Deploy**. En 2 a 4 minutos tendrás un enlace `https://<nombre>.streamlit.app`.

## Archivos

| Archivo | Contenido |
|---|---|
| `qd_app.py` | Punto de entrada |
| `qd_rates.py`, `qd_fwd.py`, `qd_opt.py`, `qd_desk.py` | Motores: curva, forwards, opciones, herramientas de mesa (DV01, cobertura, FRA) |
| `qd_data.py` | Descarga de datos (FRED, Yahoo) con caché, reintentos y respaldo DEMO |
| `qd_ui.py`, `qd_motion.py` | Sistema de diseño y núcleo de movimiento |
| `tab_curve.py`, `tab_curve_desk.py`, `tab_fwd.py`, `tab_fwd_build.py`, `tab_opt.py` | Las tres pestañas y sus módulos de mesa / constructor de forwards |
| `qd_i18n.py`, `qd_i18n_x.py` | Textos en inglés y español |

## Datos cuando Yahoo bloquea al servidor

Yahoo Finance suele rechazar las IP de servidores compartidos (error 401 "Invalid Crumb"). Para eso hay una capa de respaldo:

1. `.github/workflows/snapshot.yml` ejecuta `snapshot.py` en GitHub Actions cada 30 minutos en horario de mercado.
2. El resultado se publica en la rama `data` (`snapshot.json`). La rama `main` no cambia, así que la app no se reinicia.
3. `qd_data.py` lee ese archivo cuando la descarga directa falla. La dirección se deduce sola del repositorio; también puede fijarse con la variable `QD_SNAPSHOT_URL` (en Streamlit Cloud: Settings → Secrets, `QD_SNAPSHOT_URL = "https://raw.githubusercontent.com/<usuario>/<repo>/data/snapshot.json"`).
