""" 
Módulo de Validación de Entradas 
""" 

from typing import Optional, Tuple 

ID_ERROR = "El identificador debe ser numérico." 
NOT_FOUND = "Cliente no encontrado" 

def parse_customer_id(text: str) -> Tuple[Optional[int], Optional[str]]: 
    """Convierte el texto ingresado a un entero de ID o devuelve un mensaje de error (VS-006).""" 
    if not text or not text.strip() or not text.strip().isdigit(): 
        return None, ID_ERROR 
    return int(text.strip()), None