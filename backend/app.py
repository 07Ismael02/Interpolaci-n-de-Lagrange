"""Servidor Flask para la actividad de interpolación de Lagrange."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import BadRequest

from metodos.lagrange import interpolar_lagrange
from metodos.validaciones import ErrorValidacion, validar_solicitud


app = Flask(__name__)


def _leer_json() -> dict:
    if not request.is_json:
        raise ErrorValidacion(
            "La solicitud debe usar JSON con Content-Type application/json."
        )
    try:
        datos = request.get_json(silent=False)
    except BadRequest as exc:
        raise ErrorValidacion("El cuerpo contiene JSON inválido.") from exc
    if not isinstance(datos, dict):
        raise ErrorValidacion("El cuerpo JSON debe ser un objeto.")
    return datos


@app.get("/")
def inicio():
    return render_template("index.html")


@app.post("/api/interpolar")
def interpolar():
    try:
        datos = _leer_json()
        xs, ys, x_eval = validar_solicitud(
            datos.get("puntos"), datos.get("x_eval")
        )
        resultado = interpolar_lagrange(xs, ys, x_eval)
        return jsonify({"ok": True, **resultado})
    except ErrorValidacion as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


if __name__ == "__main__":
    app.run()

