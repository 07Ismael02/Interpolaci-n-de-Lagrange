"""Interpolación de Lagrange O(n²) con procedimiento académico completo."""

from __future__ import annotations

from .polinomios import (
    escalar,
    evaluar,
    formatear_fraccion,
    formatear_numero,
    limpiar_ceros,
    multiplicar_por_factor,
    polinomio_a_texto,
    sumar,
)
from .validaciones import validar_vectores


def _factor_texto(x_i: float) -> str:
    if x_i < 0:
        return f"(x + {formatear_numero(abs(x_i))})"
    return f"(x - {formatear_numero(x_i)})"


def _denominador_texto(x_k: float, x_i: float) -> str:
    signo = "-" if x_i >= 0 else "+"
    return f"({formatear_numero(x_k)} {signo} {formatear_numero(abs(x_i))})"


def _formula_suma(nombre: str, valores: list[float], simbolo: str) -> str:
    terminos = [f"{formatear_numero(valor)}{simbolo}{i}(x)" for i, valor in enumerate(valores)]
    return f"{nombre} = " + " + ".join(terminos)


def _muestras_grafica(
    coeficientes: list[float], xs: list[float], x_eval: float, cantidad: int = 241
) -> dict:
    minimo = min(min(xs), x_eval)
    maximo = max(max(xs), x_eval)
    if minimo == maximo:
        minimo -= 1.0
        maximo += 1.0
    paso = (maximo - minimo) / (cantidad - 1)
    puntos = []
    for indice in range(cantidad):
        x = minimo + indice * paso
        puntos.append({"x": x, "y": evaluar(coeficientes, x)})
    return {"intervalo": [minimo, maximo], "curva": puntos}


def interpolar_lagrange(
    x_valores: list[float], y_valores: list[float], x_eval: float
) -> dict:
    """
    Construye y evalúa el interpolador.

    La evaluación principal conserva explícitamente los dos bucles anidados
    requeridos por la actividad: para cada k recorre todos los i != k.
    """
    xs, ys, x_eval = validar_vectores(x_valores, y_valores, x_eval)
    cantidad = len(xs)
    grado = cantidad - 1
    coeficientes_p = [0.0] * cantidad
    bases: list[dict] = []
    resultado_directo = 0.0

    # Algoritmo de Lagrange O(n²): bucles k/i visibles y sin solver externo.
    for k in range(cantidad):
        denominador = 1.0
        valor_base_en_eval = 1.0
        numerador_coeficientes = [1.0]
        factores: list[dict] = []

        for i in range(cantidad):
            if i == k:
                continue
            diferencia_denominador = xs[k] - xs[i]
            diferencia_evaluacion = x_eval - xs[i]
            denominador *= diferencia_denominador
            valor_base_en_eval *= diferencia_evaluacion / diferencia_denominador
            numerador_coeficientes = multiplicar_por_factor(
                numerador_coeficientes, xs[i]
            )
            factores.append(
                {
                    "indice": i,
                    "x_i": xs[i],
                    "factor_numerador": _factor_texto(xs[i]),
                    "factor_denominador": _denominador_texto(xs[k], xs[i]),
                    "numerador_en_x_eval": diferencia_evaluacion,
                    "denominador_numerico": diferencia_denominador,
                    "cociente_en_x_eval": diferencia_evaluacion
                    / diferencia_denominador,
                }
            )

        coeficientes_base = limpiar_ceros(
            escalar(numerador_coeficientes, 1.0 / denominador)
        )
        coeficientes_aporte = escalar(coeficientes_base, ys[k])
        coeficientes_p = sumar(coeficientes_p, coeficientes_aporte)
        aporte_evaluado = ys[k] * valor_base_en_eval
        resultado_directo += aporte_evaluado

        numerador_texto = "".join(f["factor_numerador"] for f in factores)
        denominador_factores = "".join(f["factor_denominador"] for f in factores)
        bases.append(
            {
                "indice": k,
                "x_k": xs[k],
                "y_k": ys[k],
                "factores": factores,
                "numerador_texto": numerador_texto,
                "denominador_factores_texto": denominador_factores,
                "denominador": denominador,
                "denominador_texto": formatear_numero(denominador),
                "coeficientes": coeficientes_base,
                "coeficientes_descendentes": list(reversed(coeficientes_base)),
                "polinomio_texto": polinomio_a_texto(
                    coeficientes_base, f"L{k}(x)"
                ),
                "valor_en_x_eval": valor_base_en_eval,
                "aporte_en_x_eval": aporte_evaluado,
                "formula_producto": (
                    f"L{k}(x) = {numerador_texto} / {denominador_factores}"
                ),
            }
        )

    coeficientes_p = limpiar_ceros(coeficientes_p)
    resultado_estandar = evaluar(coeficientes_p, x_eval)
    terminos_evaluacion: list[dict] = []
    for potencia in range(grado, -1, -1):
        coeficiente = coeficientes_p[potencia]
        potencia_evaluada = x_eval**potencia
        terminos_evaluacion.append(
            {
                "potencia": potencia,
                "coeficiente": coeficiente,
                "coeficiente_texto": formatear_fraccion(coeficiente),
                "x_potencia": potencia_evaluada,
                "aporte": coeficiente * potencia_evaluada,
            }
        )

    comprobaciones: list[dict] = []
    max_diferencia = 0.0
    for indice in range(cantidad):
        calculado = evaluar(coeficientes_p, xs[indice])
        diferencia = ys[indice] - calculado
        max_diferencia = max(max_diferencia, abs(diferencia))
        comprobaciones.append(
            {
                "indice": indice,
                "x": xs[indice],
                "y_original": ys[indice],
                "p_x": calculado,
                "diferencia": diferencia,
            }
        )

    nombre_p = f"P{grado}(x)"
    sustitucion_bases = " + ".join(
        f"{formatear_numero(ys[k])}({bases[k]['polinomio_texto'].split(' = ', 1)[1]})"
        for k in range(cantidad)
    )
    grafica = _muestras_grafica(coeficientes_p, xs, x_eval)
    grafica.update(
        {
            "nodos": [{"x": xs[i], "y": ys[i]} for i in range(cantidad)],
            "punto_interpolado": {"x": x_eval, "y": resultado_directo},
            "eje_x": "Memoria asignada (GB)",
            "eje_y": "Latencia media (ms)",
        }
    )

    return {
        "nodos": [
            {"indice": i, "x": xs[i], "y": ys[i]} for i in range(cantidad)
        ],
        "x_eval": x_eval,
        "grado": grado,
        "complejidad": "O(n²)",
        "bases": bases,
        "polinomio": {
            "nombre": nombre_p,
            "formula_general": f"{nombre_p} = Σ y_k L_k(x), k = 0…{grado}",
            "formula_con_valores": _formula_suma(nombre_p, ys, "L"),
            "sustitucion_bases": f"{nombre_p} = {sustitucion_bases}",
            "coeficientes": coeficientes_p,
            "coeficientes_descendentes": list(reversed(coeficientes_p)),
            "texto": polinomio_a_texto(coeficientes_p, nombre_p),
        },
        "evaluacion": {
            "x_eval": x_eval,
            "terminos": terminos_evaluacion,
            "aportes_lagrange": [
                {
                    "indice": base["indice"],
                    "l_k": base["valor_en_x_eval"],
                    "y_k": base["y_k"],
                    "aporte": base["aporte_en_x_eval"],
                }
                for base in bases
            ],
            "resultado_directo": resultado_directo,
            "resultado_estandar": resultado_estandar,
            "diferencia_metodos": resultado_directo - resultado_estandar,
        },
        "resultado": resultado_directo,
        "comprobaciones": comprobaciones,
        "max_diferencia_nodos": max_diferencia,
        "grafica": grafica,
        "interpretacion": (
            f"Para una asignación de {formatear_numero(x_eval)} GB de memoria RAM, "
            f"el modelo interpolador estima una latencia media de aproximadamente "
            f"{formatear_numero(resultado_directo)} ms."
        ),
    }


__all__ = ["interpolar_lagrange"]

