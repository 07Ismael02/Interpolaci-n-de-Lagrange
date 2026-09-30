"""Validaciones de entrada para la API de interpolación."""

from __future__ import annotations

import math
from typing import Any


class ErrorValidacion(ValueError):
    """Error de datos esperado y comprensible para el usuario."""


def es_numero_finito(valor: Any) -> bool:
    return (
        isinstance(valor, (int, float))
        and not isinstance(valor, bool)
        and math.isfinite(valor)
    )


def validar_vectores(
    x_valores: Any, y_valores: Any, x_eval: Any
) -> tuple[list[float], list[float], float]:
    """Valida vectores numéricos para el motor, sin imponer cuatro nodos."""
    if not isinstance(x_valores, list) or not isinstance(y_valores, list):
        raise ErrorValidacion("Los valores x e y deben enviarse como listas.")
    if len(x_valores) < 2:
        raise ErrorValidacion("Se requieren al menos dos nodos para interpolar.")
    if len(x_valores) != len(y_valores):
        raise ErrorValidacion("Las listas de valores x e y deben tener la misma longitud.")

    xs: list[float] = []
    ys: list[float] = []
    for indice, (x, y) in enumerate(zip(x_valores, y_valores)):
        if not es_numero_finito(x):
            raise ErrorValidacion(
                f"x{indice} debe ser un número real finito; no se aceptan booleanos, NaN ni Infinity."
            )
        if not es_numero_finito(y):
            raise ErrorValidacion(
                f"y{indice} debe ser un número real finito; no se aceptan booleanos, NaN ni Infinity."
            )
        xs.append(float(x))
        ys.append(float(y))

    if not es_numero_finito(x_eval):
        raise ErrorValidacion(
            "x_eval debe ser un número real finito; no se aceptan booleanos, NaN ni Infinity."
        )

    for k in range(len(xs)):
        for i in range(k + 1, len(xs)):
            escala = max(1.0, abs(xs[k]), abs(xs[i]))
            if abs(xs[k] - xs[i]) <= 1e-14 * escala:
                raise ErrorValidacion(
                    "No es posible aplicar la interpolación de Lagrange porque existen valores x_i repetidos."
                )

    return xs, ys, float(x_eval)


def validar_solicitud(
    puntos: Any, x_eval: Any
) -> tuple[list[float], list[float], float]:
    """Valida el contrato de la actividad: exactamente cuatro nodos editables."""
    if puntos is None:
        raise ErrorValidacion("Falta el campo puntos.")
    if not isinstance(puntos, list):
        raise ErrorValidacion("puntos debe ser una lista de cuatro nodos.")
    if len(puntos) != 4:
        raise ErrorValidacion("La actividad requiere exactamente cuatro nodos.")

    xs: list[Any] = []
    ys: list[Any] = []
    for indice, punto in enumerate(puntos):
        if not isinstance(punto, dict):
            raise ErrorValidacion(f"El punto {indice} debe ser un objeto con campos x e y.")
        if "x" not in punto or "y" not in punto:
            raise ErrorValidacion(f"El punto {indice} está incompleto: debe incluir x e y.")
        xs.append(punto["x"])
        ys.append(punto["y"])

    return validar_vectores(xs, ys, x_eval)

