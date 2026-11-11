"""
Módulo de Lógica Financiera y Reglas de Negocio (Deep Retention)
"""
from dataclasses import dataclass
from typing import Dict, Optional, Union
import pandas as pd
import numpy as np

SALIDA_PERMITIDA = "Salida Permitida"
SIN_ACCION = "Sin Acción Requerida"
HIGH_RISK = 0.65
LOW_RISK = 0.30

@dataclass(frozen=True)
class Incentive:
    name: str
    cost: float
    effectiveness: float          # 0..1

@dataclass(frozen=True)
class Params:
    spread: float = 0.02
    fee_per_product: float = 50.0
    fee_card: float = 30.0
    service_cost: float = 60.0
    incentives: tuple[Incentive, ...] = (
        Incentive("Gestor VIP y tarifa plana", 500.0, 0.40),
        Incentive("Exoneración de comisiones", 150.0, 0.30),
        Incentive("Bonificación transaccional", 50.0, 0.20),
    )

DEFAULT_PARAMS = Params()

def customer_margin(
    balance: Union[float, pd.Series],
    num_products: Union[int, pd.Series],
    has_card: Union[int, pd.Series],
    params: Params
    ) -> Union[float, pd.Series]:
    margen = (
        (balance * params.spread)
        + (num_products * params.fee_per_product)
        + (has_card * params.fee_card)
        - params.service_cost
    )
    if isinstance(margen, pd.Series):
        return margen.round(2)
    return round(float(margen), 2)

def expected_net_gains(p: float, margin: float, params: Params) -> Dict[str, float]:
    gains = {}
    for inc in params.incentives:
        gne = (p * inc.effectiveness * margin) - inc.cost
        gains[inc.name] = round(float(gne), 2)
    return gains

def value_level_for(margin: float, median: float) -> str:
    if margin <= 0:
        return "Bajo/Deficitario"
    elif margin <= median:
        return "Medio"
    else:
        return "Superior"

def value_level(margins: pd.Series) -> pd.Series:
    pos_margins = margins[margins > 0]
    mediana = float(pos_margins.median()) if len(pos_margins) > 0 else 1000.0

    conditions = [
        margins <= 0,
        (margins > 0) & (margins <= mediana),
        margins > mediana
    ]
    choices = ["Bajo/Deficitario", "Medio", "Superior"]

    return pd.Series(np.select(conditions, choices, default="Bajo/Deficitario"), index=margins.index)

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
        else: return "A"

@dataclass
class Decision:
    label: str
    incentive: Optional[Incentive]
    gains: Dict[str, float]

def decide(p: float, margin: float, seg_code: str, params: Params) -> Decision:
    gains = expected_net_gains(p, margin, params)

    best_inc: Optional[Incentive] = None
    max_gain = -float("inf")

    for inc in params.incentives:
        g = gains.get(inc.name, -float("inf"))
        if g > max_gain:
            max_gain = g
            best_inc = inc

    if max_gain > 0 and best_inc is not None:
        label = best_inc.name
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
    median: float,
    params: Params
) -> CustomerResult:
    margin = float(customer_margin(balance, num_products, has_card, params))
    v_level = value_level_for(margin, median)
    seg_code = segment(p_churn, v_level)
    decision = decide(p_churn, margin, seg_code, params)
    return CustomerResult(p_churn=p_churn, margin=margin, segment=seg_code, decision=decision)

def score_portfolio(portfolio: pd.DataFrame, params: Params) -> pd.DataFrame:
    df = portfolio.copy()
    df["margin"] = customer_margin(df["Balance"], df["NumOfProducts"], df["HasCrCard"], params)
    df["value_level"] = value_level(df["margin"])
    pos_margins = df[df["margin"] > 0]["margin"]
    mediana = float(pos_margins.median()) if len(pos_margins) > 0 else 1000.0
    decisions = []
    incentive_costs = []
    incentive_effs = []
    expected_gains = []
    gain_cols = {f"gain__{inc.name}": [] for inc in params.incentives}

    for _, row in df.iterrows():
        p_ch = float(row["p_churn"])
        m = float(row["margin"])
        v_lev = value_level_for(m, mediana)
        seg = segment(p_ch, v_lev)
        dec = decide(p_ch, m, seg, params)

        decisions.append(dec.label)

        if dec.incentive is not None:
            incentive_costs.append(float(dec.incentive.cost))
            incentive_effs.append(float(dec.incentive.effectiveness))
            expected_gains.append(float(dec.gains[dec.incentive.name]))
        else:
            incentive_costs.append(0.0)
            incentive_effs.append(0.0)
            expected_gains.append(0.0)

        for inc in params.incentives:
            gain_cols[f"gain__{inc.name}"].append(dec.gains[inc.name])

    df["segment"] = [segment(float(r["p_churn"]), value_level_for(float(r["margin"]), mediana)) for _, r in df.iterrows()]
    df["decision"] = decisions
    df["incentive_cost"] = incentive_costs
    df["incentive_effectiveness"] = incentive_effs
    df["expected_gain"] = expected_gains
    for col_name, values in gain_cols.items():
        df[col_name] = values

    return df
