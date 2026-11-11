""" 
Módulo de Validación de Entradas 
""" 

from dataclasses import dataclass 
from typing import Any, Dict, Optional, Tuple

ID_ERROR = "El identificador debe ser numérico." 
NOT_FOUND = "Cliente no encontrado" 

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