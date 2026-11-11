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
