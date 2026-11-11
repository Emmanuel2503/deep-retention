"""
Aplicación Principal - Deep Retention
"""

import os
import pandas as pd
import streamlit as st
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.finance import (
    DEFAULT_PARAMS, Params, evaluate_customer, portfolio_kpis, score_portfolio
)
from src.inference import load_portfolio


def render_buscador(scored_cartera: pd.DataFrame, params: Params, mediana_cartera: float):
    st.header("Buscador por Cliente")
    search_mode = st.radio(
        "Modalidad de consulta:",
        ["Cliente existente", "Cliente nuevo"],
        key="search_mode"
    )
    if search_mode == "Cliente existente":
        st.subheader("Consulta por Identificador")
        id_input = st.text_input("Identificador del cliente:", key="customer_id")
        if st.button("Consultar", key="search"):
            if id_input.strip().isdigit():
                cust_id = int(id_input.strip())
                cliente = scored_cartera[scored_cartera["CustomerId"] == cust_id]
                if not cliente.empty:
                    row = cliente.iloc[0]
                    p_churn = float(row["p_churn"])
                    balance = float(row["Balance"])
                    num_prod = int(row["NumOfProducts"])
                    has_card = int(row["HasCrCard"])
                    res = evaluate_customer(p_churn, balance, num_prod, has_card, mediana_cartera, params)
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Probabilidad de fuga", f"{res.p_churn:.2f}")
                    col2.metric("Margen del cliente", f"${res.margin:,.2f}" if res.margin >= 0 else f"-${abs(res.margin):,.2f}")
                    col3.metric("Segmento", res.segment)
                    col4.metric("Decisión de retención", res.decision.label)
                    st.markdown("---")
                    st.write("Ganancias Netas Esperadas por Incentivo")
                    # Valores numéricos (contrato de VS-005); el formato de dólares lo pone column_config.
                    df_gains = pd.DataFrame([{"Incentivo": nombre, "Ganancia neta esperada": g} for nombre, g in res.decision.gains.items()])
                    st.dataframe(
                        df_gains,
                        width="stretch",
                        column_config={"Ganancia neta esperada": st.column_config.NumberColumn(format="dollar")},
                    )


def money(x: float) -> str:
    """Monto en dólares con dos decimales (SRS/BR-09): "$1,234.56" o "-$10.00"."""
    return f"${x:,.2f}" if x >= 0 else f"-${abs(x):,.2f}"


def render_cartera(scored_cartera: pd.DataFrame, params: Params):
    st.header("Panel de Cartera")
    kpis = portfolio_kpis(scored_cartera)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes analizados", f"{kpis.n_customers:,}")
    c2.metric("Capital en riesgo", money(kpis.capital_at_risk))
    c3.metric("Capital en riesgo crítico", money(kpis.capital_at_risk_critical))
    c4.metric("Capital rescatable", money(kpis.rescuable_capital))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Inversión en retención", money(kpis.investment))
    c6.metric("Margen salvado", money(kpis.saved_margin))
    c7.metric("ROI", "N/A" if kpis.roi is None else f"{kpis.roi:.1%}")
    pct = "N/A" if kpis.avoided_churn_pct is None else f"{kpis.avoided_churn_pct:.1%}"
    c8.metric("Fugas evitadas esperadas", f"{kpis.expected_avoided_churn:,.2f} ({pct})")

    counts = pd.DataFrame(
        list(kpis.decision_counts.items()), columns=["Decisión de retención", "Clientes"]
    )
    # Styler: separador de miles fijo ("5,596"), sin depender del idioma del navegador.
    st.dataframe(counts.style.format({"Clientes": "{:,}"}), width="stretch", hide_index=True)

    # Nota metodológica de EP-003/BR-01.
    st.caption("El 85% de estos clientes se usó para entrenar o calibrar la red.")


def render_simulador(params: Params):
    st.header("Simulador de Parámetros")


def main():
    st.set_page_config(page_title="Deep Retention App", layout="wide")
    st.title("Sistema Deep Retention")

    # Inicializar params en session_state (ADR-0007)
    if "params" not in st.session_state:
        st.session_state["params"] = DEFAULT_PARAMS
    params: Params = st.session_state["params"]

    # 2. Cargar y puntuar cartera de forma defensiva
    try:
        df_cartera = load_portfolio()
        scored_cartera = score_portfolio(df_cartera, params)
    except Exception as e:
        st.error(f"❌ Error al cargar o puntuar la cartera: {e}")
        st.stop()

    pos_margins = scored_cartera[scored_cartera["margin"] > 0]["margin"]
    mediana_cartera = float(pos_margins.median()) if len(pos_margins) > 0 else 1000.0

    tab1, tab2, tab3 = st.tabs(["Buscador", "Cartera", "Simulador"])

    with tab1:
        render_buscador(scored_cartera, params, mediana_cartera)

    with tab2:
        render_cartera(scored_cartera, params)

    with tab3:
        render_simulador(params)


main()
