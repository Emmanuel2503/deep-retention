"""
Módulo de Validación de Entradas
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

ID_ERROR = "El identificador debe ser numérico."
NOT_FOUND = "Cliente no encontrado"
COST_ERROR = "El costo debe ser ≥ 0"
EFFECTIVENESS_ERROR = "La efectividad debe estar entre 0% y 100%"

def parse_customer_id(text: str) -> tuple[int | None, str | None]:
    if text is None:
        return None, ID_ERROR
    text_clean = text.strip()
    if not text_clean or not text_clean.isdigit():
        return None, ID_ERROR
    return int(text_clean), None

@dataclass(frozen=True) 
class Limit: 
    min: Optional[float] = None 
    max: Optional[float] = None 
    integer: bool = False 

BUSINESS_LIMITS: Dict[str, Limit] = { 
    "CreditScore": Limit(300, 850, True), 
    "Age": Limit(18, 100, True), 
    "Tenure": Limit(0, 50, True), 
    "Balance": Limit(0, None, False), 
    "NumOfProducts": Limit(1, None, True), 
    "EstimatedSalary": Limit(0, None, False), 
    "Satisfaction Score": Limit(1, 5, True), 
    "Point Earned": Limit(0, None, True), 
} 

def validate_customer(values: Dict[str, Any]) -> Dict[str, str]:
    errors: Dict[str, str] = {} 
    for field, limit in BUSINESS_LIMITS.items(): 
        val = values.get(field) 
        if val is None or val == "": 
            errors[field] = f"{field}: es obligatorio" 
            continue 

        try: 
            val_num = float(val) 
        except (ValueError, TypeError): 
            errors[field] = f"{field}: debe ser un entero" if limit.integer else f"{field}: debe ser un número" 
            continue 

        if limit.integer: 
            if not val_num.is_integer(): 
                errors[field] = f"{field}: debe ser un entero" 
                continue 

        val_num = int(val_num) 
        if limit.min is not None and limit.max is not None: 
            if val_num < limit.min or val_num > limit.max: 
                min_str = int(limit.min) if limit.min == int(limit.min) else limit.min 
                max_str = int(limit.max) if limit.max == int(limit.max) else limit.max 
                errors[field] = f"{field}: debe estar entre {min_str} y {max_str}" 
        elif limit.min is not None: 
            if val_num < limit.min: 
                min_str = int(limit.min) if limit.min == int(limit.min) else limit.min 
                errors[field] = f"{field}: debe ser ≥ {min_str}" 
        elif limit.max is not None: 
            if val_num > limit.max: 
                max_str = int(limit.max) if limit.max == int(limit.max) else limit.max 
                errors[field] = f"{field}: debe ser ≤ {max_str}" 

    return errors


def validate_incentive(cost: float, effectiveness_pct: float) -> str | None:
    """Mensaje del primer valor inválido de un Incentivo (US-011/BR-03), o None si es válido.

    La Efectividad llega en porcentaje (0..100), como en el Simulador.
    """
    if cost is None or cost < 0:
        return COST_ERROR
    if effectiveness_pct is None or not 0 <= effectiveness_pct <= 100:
        return EFFECTIVENESS_ERROR
    return None

def validate_margin_params(spread_pct: float, fee_per_product: float, fee_card: float,
                           service_cost: float) -> dict[str, str]:
    """Campo → mensaje con el rango permitido (US-012/AC-02); {} si todo es válido.

    El Spread llega en porcentaje (0..100), como en el Simulador.
    """
    errors = {}
    if spread_pct is None or not 0 <= spread_pct <= 100:
        errors["spread"] = "El spread debe estar entre 0% y 100%"
    for field, value, label in [
        ("fee_per_product", fee_per_product, "La comisión por producto"),
        ("fee_card", fee_card, "La comisión por tarjeta"),
        ("service_cost", service_cost, "El costo de servicio"),
    ]:
        if value is None or value < 0:
            errors[field] = f"{label} debe ser ≥ 0"
    return errors
