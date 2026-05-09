# Análisis de Inversiones

Plataforma SaaS de análisis de inversiones. Introduce un ticker y obtén análisis financiero completo con descarga Excel.

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app/main.py
```

## Deploy en Streamlit Cloud

1. Sube el repositorio a GitHub
2. Ve a https://share.streamlit.io
3. Conecta el repo y configura `app/main.py` como entry point
4. En "Advanced settings > Secrets", añade:
   ```
   STRIPE_SECRET_KEY = "sk_live_..."
   ```
5. Deploy

## Credenciales demo (local)

- Usuario: `demo`
- Contraseña: `test1234`

⚠️ Cambiar credenciales antes de producción.
