"""
Aplicación Principal - Deep Retention
"""

import os
import pandas as pd
import streamlit as st
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.finance import (
    DEFAULT_PARAMS, Params, evaluate_customer, portfolio_kpis, realized_roi, score_portfolio,
    segment_matrix, widget_defaults, with_incentive,
)
from src.inference import load_portfolio
from src.validation import NOT_FOUND, parse_customer_id, validate_incentive


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
            cust_id, err_msg = parse_customer_id(id_input)
            if err_msg is not None:
                st.error(err_msg)
            else:
                cliente = scored_cartera[scored_cartera["CustomerId"] == cust_id]
                if cliente.empty:
                    st.warning(NOT_FOUND)
                else:
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
    only_test = st.toggle("Solo clientes de prueba", key="only_test", value=False)
    # La Cartera ya viene puntuada completa (VS-012/Q-01): filtrar después conserva
    # el Segmento de cada cliente, calculado con la mediana de los 10,000.
    shown = scored_cartera[scored_cartera["split"] == "test"] if only_test else scored_cartera
    kpis = portfolio_kpis(shown)

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

    if only_test:
        # SRS/OBJ-03: usa el abandono real (Exited), así que puede ser negativo.
        roi_real = realized_roi(shown)
        st.metric("ROI realizado", "N/A" if roi_real is None else f"{roi_real:.1%}")

    counts = pd.DataFrame(
        list(kpis.decision_counts.items()), columns=["Decisión de retención", "Clientes"]
    )
    # Styler: separador de miles fijo ("5,596"), sin depender del idioma del navegador.
    st.dataframe(counts.style.format({"Clientes": "{:,}"}), width="stretch", hide_index=True)

    st.subheader("Matriz por segmento")
    matrix = segment_matrix(shown, params)
    money_cols = ["Inversión en retención", "Ganancia neta esperada"]
    count_cols = [c for c in matrix.columns[3:] if c not in money_cols]
    st.dataframe(
        matrix.style.format({**{c: "{:,}" for c in count_cols}, **{c: money for c in money_cols}}),
        width="stretch",
    )

    # Nota metodológica de EP-003/BR-01, solo con la Cartera completa.
    if not only_test:
        st.caption("El 85% de estos clientes se usó para entrenar o calibrar la red.")


def on_incentive_change(i: int):
    """Callback del Incentivo i (ADR-0007): corre antes del script, así que las tres
    pestañas usan los parámetros nuevos en la misma ejecución."""
    cost = st.session_state[f"cost_{i}"]
    eff_pct = st.session_state[f"eff_{i}"]
    error = validate_incentive(cost, eff_pct)
    if error is None:
        st.session_state["params"] = with_incentive(st.session_state["params"], i, cost, eff_pct / 100)
        st.session_state["sim_errors"].pop(f"incentive_{i}", None)
    else:
        # Valor inválido: se conservan los parámetros anteriores (US-011/BR-03).
        st.session_state["sim_errors"][f"incentive_{i}"] = error


def render_simulador(params: Params):
    st.header("Simulador de Parámetros")

    st.subheader("Incentivos")
    for i, inc in enumerate(params.incentives):
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.markdown(f"**{inc.name}**")
        c2.number_input("Costo ($)", key=f"cost_{i}", step=10.0, on_change=on_incentive_change, args=(i,))
        c3.number_input("Efectividad (%)", key=f"eff_{i}", step=1.0, on_change=on_incentive_change, args=(i,))

    for error in st.session_state["sim_errors"].values():
        st.error(error)


def main():
    st.set_page_config(page_title="Deep Retention App", layout="wide")
    st.title("Sistema Deep Retention")

    # Inicializar params en session_state (ADR-0007)
    if "params" not in st.session_state:
        st.session_state["params"] = DEFAULT_PARAMS
    params: Params = st.session_state["params"]
    # Claves de las entradas del Simulador (VS-013): sin `value` en el widget, su valor vive aquí.
    for k, v in widget_defaults(params).items():
        st.session_state.setdefault(k, v)
    st.session_state.setdefault("sim_errors", {})

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
