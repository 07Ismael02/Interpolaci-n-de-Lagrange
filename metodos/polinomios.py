"""Operaciones elementales con polinomios representados en orden ascendente."""

from __future__ import annotations

from fractions import Fraction


def multiplicar_por_factor(coeficientes: list[float], raiz: float) -> list[float]:
    """Multiplica un polinomio por (x - raiz) usando ciclos explícitos."""
    resultado = [0.0] * (len(coeficientes) + 1)
    for grado, coeficiente in enumerate(coeficientes):
        resultado[grado] += -raiz * coeficiente
        resultado[grado + 1] += coeficiente
    return resultado


def escalar(coeficientes: list[float], factor: float) -> list[float]:
    return [coeficiente * factor for coeficiente in coeficientes]


def sumar(a: list[float], b: list[float]) -> list[float]:
    longitud = max(len(a), len(b))
    resultado = [0.0] * longitud
    for i in range(longitud):
        if i < len(a):
            resultado[i] += a[i]
        if i < len(b):
            resultado[i] += b[i]
    return resultado


def evaluar(coeficientes: list[float], x: float) -> float:
    """Evalúa mediante Horner; los coeficientes están en orden ascendente."""
    resultado = 0.0
    for coeficiente in reversed(coeficientes):
        resultado = resultado * x + coeficiente
    return resultado


def limpiar_ceros(coeficientes: list[float], tolerancia: float = 1e-14) -> list[float]:
    escala = max((abs(valor) for valor in coeficientes), default=1.0)
    umbral = tolerancia * max(1.0, escala)
    return [0.0 if abs(valor) <= umbral else valor for valor in coeficientes]


def formatear_numero(valor: float, cifras: int = 12) -> str:
    if abs(valor) < 5e-15:
        valor = 0.0
    if valor == 0:
        return "0"
    return f"{valor:.{cifras}g}"


def formatear_fraccion(valor: float) -> str:
    """Usa una fracción limpia solo cuando representa fielmente al flotante."""
    if abs(valor) < 5e-15:
        return "0"
    fraccion = Fraction(valor).limit_denominator(1_000_000)
    tolerancia = 1e-11 * max(1.0, abs(valor))
    if abs(float(fraccion) - valor) <= tolerancia:
        if fraccion.denominator == 1:
            return str(fraccion.numerator)
        return f"{fraccion.numerator}/{fraccion.denominator}"
    return formatear_numero(valor)


def polinomio_a_texto(
    coeficientes: list[float], nombre: str | None = None, usar_fracciones: bool = True
) -> str:
    """Convierte coeficientes ascendentes en una expresión estándar legible."""
    formatear = formatear_fraccion if usar_fracciones else formatear_numero
    terminos: list[str] = []
    grado_maximo = len(coeficientes) - 1
    for potencia in range(grado_maximo, -1, -1):
        coeficiente = coeficientes[potencia]
        if abs(coeficiente) < 5e-14:
            continue
        magnitud = abs(coeficiente)
        coef_texto = formatear(magnitud)
        if potencia == 0:
            termino = coef_texto
        else:
            factor = "" if abs(magnitud - 1.0) < 1e-14 else coef_texto
            variable = "x" if potencia == 1 else f"x^{potencia}"
            termino = f"{factor}{variable}"
        if not terminos:
            terminos.append(f"- {termino}" if coeficiente < 0 else termino)
        else:
            terminos.append(f"{'-' if coeficiente < 0 else '+'} {termino}")
    expresion = " ".join(terminos) if terminos else "0"
    return f"{nombre} = {expresion}" if nombre else expresion


__all__ = [
    "multiplicar_por_factor",
    "escalar",
    "sumar",
    "evaluar",
    "limpiar_ceros",
    "formatear_numero",
    "formatear_fraccion",
    "polinomio_a_texto",
]

