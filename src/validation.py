"""
Módulo de Validación de Entradas
"""

ID_ERROR = "El identificador debe ser numérico."
NOT_FOUND = "Cliente no encontrado"

def parse_customer_id(text: str) -> tuple[int | None, str | None]:
    if text is None:
        return None, ID_ERROR
    text_clean = text.strip()
    if not text_clean or not text_clean.isdigit():
        return None, ID_ERROR
    return int(text_clean), None
