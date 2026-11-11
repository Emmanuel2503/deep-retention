""" 
Aplicación Principal - Deep Retention
""" 

import os 
import pandas as pd 
import streamlit as st 
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) 

from src.finance import evaluate_customer, median_positive_margin 
from src.validation import parse_customer_id, NOT_FOUND
from src.inference import ChurnPredictor, load_portfolio

@st.cache_resource 
def obtener_predictor():
    try: 
        return ChurnPredictor.load()
    except Exception as e: 
        st.error(f"⚠️ Aviso al cargar el modelo: {e}") 
        return None

def cargar_cartera_ejemplo() -> pd.DataFrame: 
    try: 
        return load_portfolio() 
    except Exception as e: 
        st.error(f"⚠️ Aviso al cargar la cartera: {e}") 
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
  
    search_mode = st.radio( 
      "Modalidad de consulta:", 
      ["Cliente existente", "Cliente nuevo"], 
      key="search_mode" 
    ) 
  
    df_cartera = cargar_cartera_ejemplo() 
    mediana_cartera = median_positive_margin(df_cartera) 
    predictor = obtener_predictor()
  
    if search_mode == "Cliente existente": 
        st.subheader("Consulta por Identificador") 
        id_input = st.text_input("Identificador del cliente:", key="customer_id") 
        
        if st.button("Consultar", key="search"): 
            cust_id, err = parse_customer_id(id_input) 
            
            if err: 
                st.error(err) 
                return 
            
            cliente = df_cartera[df_cartera["CustomerId"] == cust_id] 
            
            if cliente.empty: 
                st.warning(NOT_FOUND) 
                return 
            
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
                for nombre, g in res.decision.gains.items() ]) 
            st.dataframe(df_gains, use_container_width=True) 
        
    else: 
        st.subheader("Evaluación de Cliente Nuevo") 

        predictor = obtener_predictor()

        geo_opts = predictor.categories.get("Geography", ["France", "Germany", "Spain"]) if predictor else ["France", "Germany", "Spain"] 
        gender_opts = predictor.categories.get("Gender", ["Female", "Male"]) if predictor else ["Female", "Male"]

        with st.form(key="new_customer"): 
            col_a, col_b = st.columns(2) 
            
            with col_a: 
                credit_score = st.number_input("Credit Score", value=650, key="f_CreditScore") 
                age = st.number_input("Age", value=35, key="f_Age") 
                tenure = st.number_input("Tenure", value=3, key="f_Tenure") 
                balance = st.number_input("Balance", value=50000.0, step=1000.0, key="f_Balance") 
                num_products = st.number_input("Number Of Products", value=2, key="f_NumOfProducts") 
                
            with col_b: 
                salary = st.number_input("Estimated Salary", value=60000.0, step=1000.0, key="f_EstimatedSalary") 
                satisfaction = st.number_input("Satisfaction Score", value=3, key="f_Satisfaction Score") 
                points = st.number_input("Point Earned", value=500, key="f_Point Earned") 
                geography = st.selectbox("Geography", geo_opts, key="f_Geography") 
                gender = st.selectbox("Gender", gender_opts, key="f_Gender")

            has_cr_card = st.checkbox("Tiene Tarjeta de Crédito", value=True, key="f_HasCrCard") 
            is_active = st.checkbox("Es Miembro Activo", value=True, key="f_IsActiveMember")
            
            submitted = st.form_submit_button("Evaluar") 
            
            if submitted: 
                form_data = { 
                    "CreditScore": credit_score, 
                    "Geography": geography, 
                    "Gender": gender, 
                    "Age": age, 
                    "Tenure": tenure, 
                    "Balance": balance, 
                    "NumOfProducts": num_products, 
                    "HasCrCard": 1 if has_cr_card else 0, 
                    "IsActiveMember": 1 if is_active else 0, 
                    "EstimatedSalary": salary, 
                    "Satisfaction Score": satisfaction, 
                    "Point Earned": points 
                } 
                
                if predictor is not None: 
                    df_nuevo = pd.DataFrame([form_data]) 
                    p_churn = float(predictor.predict(df_nuevo)) 
                else: 
                    p_churn = 0.70 
                
                res = evaluate_customer( 
                    p_churn, balance, int(num_products), 1 if has_cr_card else 0, mediana_cartera 
                ) 
                
                st.success("Evaluación realizada") 
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