""" 
Aplicación Principal - Deep Retention
""" 

import os 
import pandas as pd 
import streamlit as st 
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) 

from src.finance import ( 
    DEFAULT_PARAMS, Params, evaluate_customer, score_portfolio 
) 
from src.inference import load_portfolio
from src.validation import ID_ERROR, NOT_FOUND, parse_customer_id

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
                        df_gains = pd.DataFrame([ 
                            {"Incentivo": nombre, "Ganancia neta esperada": f"${g:,.2f}" if g >= 0 else f"-${abs(g):,.2f}"} 
                            for nombre, g in res.decision.gains.items() 
                        ]) 
                        st.dataframe(df_gains, use_container_width=True) 

    with tab2: 
        st.header("Panel de Cartera")

    with tab3: 
        st.header("Simulador de Parámetros")


main()