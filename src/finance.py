""" 
Módulo de Lógica Financiera y Reglas de Negocio (Deep Retention) 
""" 
from dataclasses import dataclass 
from operator import gt
from typing import Dict, Any, Optional 
import pandas as pd 

SALIDA_PERMITIDA = "Salida Permitida" 
SIN_ACCION = "Sin Acción Requerida" 
HIGH_RISK = 0.65 
LOW_RISK = 0.30 

DEFAULT_PARAMS: Dict[str, Any] = { 
    "spread": 0.02, 
    "comision_producto": 50.0, 
    "comision_tarjeta": 30.0, 
    "costo_servicio": 60.0, 
    "incentivos": [ 
        {"nombre": "Gestor VIP y tarifa plana", "costo": 500.0, "efectividad": 0.40}, 
        {"nombre": "Exoneración de comisiones", "costo": 150.0, "efectividad": 0.30}, 
        {"nombre": "Bonificación transaccional", "costo": 50.0, "efectividad": 0.20}, 
    ] 
} 

def customer_margin(balance: float, num_products: int, has_card: int, params: Optional[Dict[str, Any]] = None) -> float: 
    p = params if params is not None else DEFAULT_PARAMS 
    spread = p.get("spread", 0.02) 
    comision_prod = p.get("comision_producto", 50.0) 
    comision_tarj = p.get("comision_tarjeta", 30.0) 
    costo_serv = p.get("costo_servicio", 60.0) 

    margen = (balance * spread) + (num_products * comision_prod) + (has_card * comision_tarj) - costo_serv 
    return round(float(margen), 2) 

def expected_net_gains(p: float, margin: float, params: Optional[Dict[str, Any]] = None) -> Dict[str, float]: 
    par = params if params is not None else DEFAULT_PARAMS 
    incentivos = par.get("incentivos", DEFAULT_PARAMS["incentivos"]) 
    gains = {} 
    for inc in incentivos: 
        nombre = inc["nombre"] 
        costo = float(inc["costo"]) 
        efectividad = float(inc["efectividad"]) 
        gne = (p * efectividad * margin) - costo 
        gains[nombre] = round(float(gne), 2) 
    return gains 

def median_positive_margin(scored: pd.DataFrame) -> float: 
    if "margin" in scored.columns: 
        pos = scored[scored["margin"] > 0]["margin"] 
    elif "Balance" in scored.columns: 
        margins = scored.apply(lambda r: customer_margin(r["Balance"], r.get("NumOfProducts", 1), r.get("HasCrCard", 1)), axis=1) 
        pos = margins[margins > 0] 
    else: 
        return 1000.0 

    return float(pos.median()) if len(pos) > 0 else 1000.0 

def value_level_for(margin: float, median: float) -> str: 
    if margin <= 0: 
        return "Bajo/Deficitario" 
    elif margin <= median: 
        return "Medio" 
    else: 
        return "Superior" 

def segment(p: float, level: str) -> str: 
    if p < LOW_RISK:
        return "D"
    elif p < HIGH_RISK:
        return "E"
    else:
        if level == "Bajo/Deficitario":
            return "C"
        elif level == "Medio":
            return "B"
        else:
            return "A"

@dataclass
class Decision:
    label: str
    incentive: Optional[Dict[str, Any]]
    gains: Dict[str, float]

def decide(p: float, margin: float, seg_code: str, params: Optional[Dict[str, Any]] = None) -> Decision:
    gains = expected_net_gains(p, margin, params)
    par = params if params is not None else DEFAULT_PARAMS
    incentivos = par.get("incentivos", DEFAULT_PARAMS["incentivos"])

    best_inc = None
    max_gain = -float("inf")

    for inc in incentivos: 
        nombre = inc["nombre"] 
        g = gains.get(nombre, -float("inf")) 
        if g > max_gain: 
            max_gain = g 
            best_inc = inc 
            
    if max_gain > 0 and best_inc is not None: 
        label = best_inc["nombre"] 
        inc_obj = best_inc 
    else: 
        inc_obj = None 
        label = SIN_ACCION if seg_code == "D" else SALIDA_PERMITIDA 

    return Decision(label=label, incentive=inc_obj, gains=gains) 

@dataclass
class CustomerResult:
    p_churn: float
    margin: float
    segment: str
    decision: Decision

def evaluate_customer(
    p_churn: float,
    balance: float,
    num_products: int,
    has_card: int,
    median: float = 1000.0,
    params: Optional[Dict[str, Any]] = None
) -> CustomerResult:
    margin = customer_margin(balance, num_products, has_card, params)
    v_level = value_level_for(margin, median)
    seg_code = segment(p_churn, v_level)
    decision = decide(p_churn, margin, seg_code, params)
    return CustomerResult(p_churn=p_churn, margin=margin, segment=seg_code, decision=decision)