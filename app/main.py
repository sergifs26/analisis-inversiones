import tempfile
from pathlib import Path
import streamlit as st
from engine.runner import run_analysis
from engine.excel_writer import generate_excel
from app.charts import revenue_chart, margins_chart, scenarios_chart, multiples_table
from app.auth import load_authenticator

authenticator, _auth_config = load_authenticator()
name, authentication_status, username = authenticator.login("Acceder", "main")

if authentication_status is False:
    st.error("Usuario o contraseña incorrectos.")
    st.stop()
elif authentication_status is None:
    st.warning("Introduce tus credenciales.")
    st.stop()

authenticator.logout("Cerrar sesión", "sidebar")
st.sidebar.write(f"Bienvenido, {name}")

from app.stripe_gate import has_active_subscription

# Verificar suscripcion activa
user_email = (
    _auth_config.get("credentials", {})
    .get("usernames", {})
    .get(username or "", {})
    .get("email", "")
)
if not has_active_subscription(user_email):
    st.error("Tu suscripción no está activa.")
    st.info("Suscríbete por 19€/mes para acceder al análisis profesional.")
    st.stop()

TEMPLATE = Path("templates/Modelo 2025 vacio.xlsx")

st.set_page_config(
    page_title="Análisis de Inversiones",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Análisis de Inversiones")
st.caption("Modelo profesional de valoración automatizado")

ticker_input = st.text_input(
    "Introduce el ticker de la empresa",
    placeholder="AAPL, MSFT, ITX.MC, SAN.MC...",
    max_chars=20,
)

if st.button("Analizar", type="primary", use_container_width=False):
    if not ticker_input.strip():
        st.warning("Introduce un ticker válido.")
    else:
        ticker = ticker_input.strip().upper()
        with st.spinner(f"Analizando {ticker}..."):
            try:
                result = run_analysis(ticker)
            except ValueError as e:
                st.error(str(e))
                st.stop()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Empresa",  result.company_name)
        col2.metric("Sector",   result.sector)
        col3.metric("Precio",   f"{result.assumptions.price:.2f} {result.currency}")
        col4.metric("Div Yield", f"{result.assumptions.div_yield:.2%}")

        st.divider()

        st.subheader("Supuestos de proyección")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Crecimiento ventas", f"{result.assumptions.growth:.1%}")
        c2.metric("Margen EBIT",        f"{result.assumptions.ebit_margin:.1%}")
        c3.metric("Tasa impositiva",     f"{result.assumptions.tax_rate:.1%}")
        c4.metric("% Recompras FCF",    f"{result.assumptions.buyback_pct:.0%}")

        st.divider()

        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(revenue_chart(result), use_container_width=True)
        with col_b:
            st.plotly_chart(margins_chart(result), use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            st.plotly_chart(scenarios_chart(result), use_container_width=True)
        with col_d:
            st.subheader("Múltiplos históricos")
            st.plotly_chart(multiples_table(result), use_container_width=True)

        st.divider()

        st.subheader("Escenarios Bull / Mid / Bear")
        s = result.scenarios
        data = {
            "Escenario": ["🐂 Bull", "➡️ Mid", "🐻 Bear"],
            "Precio 3Y": [f"{s.bull_3y:.2f}", f"{s.mid_3y:.2f}", f"{s.bear_3y:.2f}"],
            "Precio 5Y": [f"{s.bull_5y:.2f}", f"{s.mid_5y:.2f}", f"{s.bear_5y:.2f}"],
            "CAGR 3Y estimado": [
                f"{((s.bull_3y/result.assumptions.price)**(1/3)-1):.1%}" if result.assumptions.price else "N/D",
                f"{((s.mid_3y/result.assumptions.price)**(1/3)-1):.1%}"  if result.assumptions.price else "N/D",
                f"{((s.bear_3y/result.assumptions.price)**(1/3)-1):.1%}" if result.assumptions.price else "N/D",
            ],
        }
        st.table(data)

        st.divider()

        st.subheader("Descarga el modelo completo")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / f"{ticker}_Modelo_2025.xlsx"
            generate_excel(result, TEMPLATE, output)
            with open(output, "rb") as f:
                excel_bytes = f.read()

        st.download_button(
            label="⬇️ Descargar Excel completo",
            data=excel_bytes,
            file_name=f"{ticker}_Modelo_2025.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )

        st.caption("⚠️ Esta herramienta es únicamente para análisis personal. "
                   "No constituye asesoramiento financiero ni recomendación de inversión.")
