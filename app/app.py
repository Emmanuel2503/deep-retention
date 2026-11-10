""" 
Aplicación Principal - Deep Retention
""" 

import os 
import pandas as pd 
import streamlit as st 
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) 

from src.finance import evaluate_customer, median_positive_margin 

def cargar_cartera_ejemplo() -> pd.DataFrame: 
    rutas = [ 
        os.getenv("DEEP_RETENTION_PORTFOLIO", ""), 
        "models/portfolio_scored.csv", 
        "data/fixtures/portfolio_cases.csv" 
    ] 
    for ruta in rutas: 
        if ruta and os.path.exists(ruta): 
            df = pd.read_csv(ruta) 
            if "p_churn" not in df.columns and "Probabilidad" in df.columns: 
                df["p_churn"] = df["Probabilidad"] 
            elif "p_churn" not in df.columns and "Exited" in df.columns: 
                df["p_churn"] = df["Exited"].astype(float) 
            return df 
    
    return pd.DataFrame([ 
        {"CustomerId": 1001, "Balance": 100000.0, "NumOfProducts": 2, "HasCrCard": 1, "p_churn": 0.80}, 
        {"CustomerId": 1002, "Balance": 0.0, "NumOfProducts": 1, "HasCrCard": 0, "p_churn": 0.50}, 
        {"CustomerId": 1003, "Balance": 100000.0, "NumOfProducts": 2, "HasCrCard": 1, "p_churn": 0.10}, 
    ]) 

def render_buscador(): 
    st.header("Buscador por Cliente") 
    st.subheader("Consulta por Identificador") 
    
    df_cartera = cargar_cartera_ejemplo() 
    mediana_cartera = median_positive_margin(df_cartera) 
    
    id_input = st.text_input("Identificador del cliente:", key="customer_id") 
    
    if st.button("Consultar", key="search"): 
        cust_id = int(id_input.strip()) 
        cliente = df_cartera[df_cartera["CustomerId"] == cust_id] 
        
        if not cliente.empty: 
            row = cliente.iloc[0] 
            p_churn = float(row.get("p_churn", 0.50)) 
            balance = float(row.get("Balance", 0.0)) 
            num_prod = int(row.get("NumOfProducts", 1)) 
            has_card = int(row.get("HasCrCard", 1)) 

            res = evaluate_customer(p_churn, balance, num_prod, has_card, mediana_cartera) 

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

def render_cartera(): 
    st.header("Panel de Cartera")

def render_simulador(): 
    st.header("Simulador de Parámetros")

def main(): 
    st.set_page_config(page_title="Deep Retention App", layout="wide") 
    st.title("Sistema Deep Retention") 

    tab1, tab2, tab3 = st.tabs(["Buscador", "Cartera", "Simulador"])
    with tab1: 
        render_buscador() 
    with tab2: 
        render_cartera() 
    with tab3: 
        render_simulador() 

if __name__ == "__main__": 
    main()