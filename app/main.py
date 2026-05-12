import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from app.auth import load_authenticator

st.set_page_config(
    page_title="Análisis de Inversiones",
    page_icon="📈",
    layout="wide",
)

authenticator, _auth_config = load_authenticator()

name = st.session_state.get("name")
authentication_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

if not authentication_status:
    tab_login, tab_register = st.tabs(["Iniciar sesión", "Crear cuenta"])

    with tab_login:
        authenticator.login(key="login")
        if authentication_status is False:
            st.error("Usuario o contraseña incorrectos.")

    with tab_register:
        st.subheader("Crear una cuenta")
        st.write("Accede al análisis profesional de inversiones por **19€/mes**.")
        st.divider()
        st.markdown("### Paso 1 — Suscríbete")
        st.link_button(
            "💳 Suscribirme por 19€/mes",
            "https://buy.stripe.com/7sYfZkeem3507itexZao800",
            type="primary",
        )
        st.divider()
        st.markdown("### Paso 2 — Recibe tus credenciales")
        st.info(
            "Tras completar el pago recibirás un email con tu usuario y contraseña "
            "en menos de 24 horas."
        )

    st.stop()

authenticator.logout("Cerrar sesión", "sidebar")
st.sidebar.write(f"Bienvenido, {name}")

from app.stripe_gate import has_active_subscription

user_email = (
    _auth_config.get("credentials", {})
    .get("usernames", {})
    .get(username or "", {})
    .get("email", "")
)
if not has_active_subscription(user_email):
    st.error("Tu suscripción no está activa.")
    st.info("Suscríbete por 19€/mes para acceder al análisis profesional.")
    st.link_button("💳 Suscribirme ahora", "https://buy.stripe.com/7sYfZkeem3507itexZao800", type="primary")
    st.stop()

TEMPLATE = Path("templates/Modelo 2025 vacio.xlsx")

st.title("📈 Análisis de Inversiones")
st.caption("Modelo profesional de valoración automatizado")

from engine.runner import run_analysis
from engine.excel_writer import generate_excel
from app.charts import revenue_chart, margins_chart, scenarios_chart, multiples_table
from app.search import search_local, search_yahoo

st.subheader("🔍 Buscar empresa")
search_query = st.text_input(
    "Nombre o ticker de la empresa",
    placeholder="Ej: Apple, Inditex, AAPL, ITX.MC...",
)

selected_ticker = None

if search_query and len(search_query) >= 2:
    local_results = search_local(search_query)

    if local_results:
        st.markdown("**Empresas populares:**")
        options_local = {f"{name} ({ticker}) — {market}": ticker
                        for ticker, name, market in local_results}
        choice_local = st.selectbox(
            "Selecciona de la lista:",
            ["— Selecciona una empresa —"] + list(options_local.keys()),
            key="local_select",
        )
        if choice_local != "— Selecciona una empresa —":
            selected_ticker = options_local[choice_local]

    with st.expander("🌐 Buscar en Yahoo Finance (tiempo real)", expanded=not local_results):
        if st.button("Buscar en Yahoo Finance", key="yahoo_search"):
            yahoo_results = search_yahoo(search_query)
            if yahoo_results:
                st.session_state["yahoo_results"] = yahoo_results
            else:
                st.warning("No se encontraron resultados. Prueba con otro término.")

        if "yahoo_results" in st.session_state and st.session_state["yahoo_results"]:
            options_yahoo = {f"{name} ({ticker}) — {exchange}": ticker
                            for ticker, name, exchange in st.session_state["yahoo_results"]}
            choice_yahoo = st.selectbox(
                "Selecciona de Yahoo Finance:",
                ["— Selecciona una empresa —"] + list(options_yahoo.keys()),
                key="yahoo_select",
            )
            if choice_yahoo != "— Selecciona una empresa —":
                selected_ticker = options_yahoo[choice_yahoo]

if selected_ticker:
    st.info(f"Empresa seleccionada: **{selected_ticker}**")

if st.button("Analizar", type="primary", disabled=not selected_ticker):
    if not selected_ticker:
        st.warning("Selecciona una empresa primero.")
    else:
        ticker = selected_ticker.strip().upper()
        with st.spinner(f"Analizando {ticker}..."):
            try:
                result = run_analysis(ticker)
            except ValueError as e:
                st.error(str(e))
                st.stop()
            except Exception as e:
                if "RateLimit" in type(e).__name__ or "RateLimit" in str(e):
                    st.error("Yahoo Finance ha limitado las peticiones temporalmente. Espera 30 segundos e inténtalo de nuevo.")
                else:
                    st.error(f"Error al obtener datos: {e}")
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
