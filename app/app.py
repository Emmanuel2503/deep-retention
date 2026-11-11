""" 
Aplicación Principal - Deep Retention
""" 

import os 
import pandas as pd 
import streamlit as st 
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) 

from src.finance import ( 
    DEFAULT_PARAMS, Params, evaluate_customer, median_positive_margin, score_portfolio 
) 
from src.inference import ChurnPredictor, load_portfolio
from src.validation import ( 
    ID_ERROR, NOT_FOUND, parse_customer_id, validate_customer 
)

@st.cache_resource 
def obtener_predictor(): 
    try: 
        return ChurnPredictor.load() 
    except Exception: 
        return None

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

    mediana_cartera = median_positive_margin(scored_cartera) 
    predictor = obtener_predictor()

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

        else: 
            st.subheader("Formulario de Cliente Nuevo") 
            
            cat_geography = predictor.categories.get("Geography", ["France", "Germany", "Spain"]) if predictor else ["France", "Germany", "Spain"] 
            cat_gender = predictor.categories.get("Gender", ["Female", "Male"]) if predictor else ["Female", "Male"] 
            cat_card_type = predictor.categories.get("Card Type", ["DIAMOND", "GOLD", "PLATINUM", "SILVER"]) if predictor else ["DIAMOND", "GOLD", "PLATINUM", "SILVER"] 
            
            with st.form(key="new_customer"): 
                c1, c2, c3 = st.columns(3) 
                with c1: 
                    credit_score = st.number_input("Credit Score", value=650, key="f_CreditScore") 
                    geography = st.selectbox("Geography", cat_geography, key="f_Geography") 
                    gender = st.selectbox("Gender", cat_gender, key="f_Gender") 
                    age = st.number_input("Age", value=35, key="f_Age") 
                with c2: 
                    tenure = st.number_input("Tenure", value=3, key="f_Tenure") 
                    balance = st.number_input("Balance", value=250000.0, key="f_Balance") 
                    num_products = st.number_input("Number Of Products", value=2, key="f_NumOfProducts") 
                    estimated_salary = st.number_input("Estimated Salary", value=50000.0, key="f_EstimatedSalary") 
                with c3: 
                    satisfaction_score = st.number_input("Satisfaction Score", value=3, key="f_Satisfaction Score") 
                    card_type = st.selectbox("Card Type", cat_card_type, key="f_Card Type") 
                    point_earned = st.number_input("Point Earned", value=500, key="f_Point Earned") 
                    has_cr_card = st.checkbox("Tiene Tarjeta de Crédito", value=True, key="f_HasCrCard") 
                    is_active_member = st.checkbox("Es Miembro Activo", value=True, key="f_IsActiveMember") 
                submitted = st.form_submit_button("Evaluar") 

            if submitted: 
                valores_formulario = { 
                    "CreditScore": credit_score, 
                    "Age": age, 
                    "Tenure": tenure, 
                    "Balance": balance, 
                    "NumOfProducts": num_products,
                    "EstimatedSalary": estimated_salary, 
                    "Satisfaction Score": satisfaction_score, 
                    "Point Earned": point_earned, 
                } 
                
                errores = validate_customer(valores_formulario) 
                
                if errores: 
                    for msg in errores.values(): 
                        st.error(msg) 
                else: 
                    has_card_val = 1 if has_cr_card else 0 
                    active_val = 1 if is_active_member else 0 

                    datos_cliente = { 
                        "CreditScore": credit_score, 
                        "Geography": geography, 
                        "Gender": gender, 
                        "Age": age, 
                        "Tenure": tenure, 
                        "Balance": balance, 
                        "NumOfProducts": num_products, 
                        "HasCrCard": has_card_val, 
                        "IsActiveMember": active_val, 
                        "EstimatedSalary": estimated_salary, 
                        "Satisfaction Score": satisfaction_score, 
                        "Card Type": card_type, 
                        "Point Earned": point_earned, 
                    } 

                    df_nuevo = pd.DataFrame([datos_cliente]) 

                    if predictor is not None: 
                        try: 
                            p_churn = float(predictor.predict(df_nuevo)) 
                        except Exception: 
                            p_churn = 0.70 
                    else: 
                        p_churn = 0.70 

                    res = evaluate_customer( 
                        p_churn=p_churn, 
                        balance=float(balance), 
                        num_products=int(num_products), 
                        has_card=has_card_val, 
                        median=mediana_cartera, 
                        params=params 
                    ) 

                    st.markdown("---") 
                    st.subheader("Resultados de Evaluación") 
                    
                    col1, col2, col3, col4 = st.columns(4) 
                    col1.metric("Probabilidad de fuga", f"{res.p_churn:.2f}") 
                    col2.metric("Margen del cliente", f"${res.margin:,.2f}" if res.margin >= 0 else f"-${abs(res.margin):,.2f}") 
                    col3.metric("Segmento", res.segment) 
                    col4.metric("Decisión de retención", res.decision.label) 
                    st.markdown("---") 
                    st.write("### Ganancias Netas Esperadas por Incentivo") 
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