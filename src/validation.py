"""
Módulo de Validación de Entradas
"""

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

def validate_incentive(cost: float, effectiveness_pct: float) -> str | None:
    """Mensaje del primer valor inválido de un Incentivo (US-011/BR-03), o None si es válido.

    La Efectividad llega en porcentaje (0..100), como en el Simulador.
    """
    if cost is None or cost < 0:
        return COST_ERROR
    if effectiveness_pct is None or not 0 <= effectiveness_pct <= 100:
        return EFFECTIVENESS_ERROR
    return None
