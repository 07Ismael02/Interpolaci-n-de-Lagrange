import math
import unittest

from backend.app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        self.oficial = {
            "puntos": [
                {"x": 2, "y": 150},
                {"x": 4, "y": 85},
                {"x": 8, "y": 50},
                {"x": 12, "y": 70},
            ],
            "x_eval": 6,
        }

    def test_get_inicio(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Interpolaci\xc3\xb3n Polin\xc3\xb3mica", response.data)
        self.assertIn(b"Cargar caso oficial", response.data)

    def test_post_oficial(self):
        response = self.client.post("/api/interpolar", json=self.oficial)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["ok"])
        self.assertAlmostEqual(data["resultado"], 55.25)
        self.assertEqual(len(data["bases"]), 4)
        self.assertEqual(len(data["grafica"]["curva"]), 241)

    def test_api_alternativa_anti_hardcoding(self):
        puntos = [{"x": x, "y": x * x + 2 * x + 3} for x in [-2, 0, 1, 3]]
        response = self.client.post(
            "/api/interpolar", json={"puntos": puntos, "x_eval": 2}
        )
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.get_json()["resultado"], 11.0)

    def test_json_invalido(self):
        response = self.client.post(
            "/api/interpolar", data="{invalido", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("JSON inválido", response.get_json()["error"])

    def test_content_type_incorrecto(self):
        response = self.client.post("/api/interpolar", data="texto")
        self.assertEqual(response.status_code, 400)
        self.assertIn("application/json", response.get_json()["error"])

    def test_datos_incompletos(self):
        casos = [
            ({}, "puntos"),
            ({"puntos": self.oficial["puntos"]}, "x_eval"),
            ({"puntos": self.oficial["puntos"][:3], "x_eval": 6}, "cuatro"),
            ({"puntos": [{"x": 1}] * 4, "x_eval": 6}, "incompleto"),
        ]
        for payload, fragmento in casos:
            with self.subTest(payload=payload):
                response = self.client.post("/api/interpolar", json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn(fragmento, response.get_json()["error"].lower())

    def test_nodos_repetidos_http_400(self):
        payload = {
            "puntos": [
                {"x": 1, "y": 2}, {"x": 2, "y": 3},
                {"x": 2, "y": 4}, {"x": 4, "y": 5},
            ],
            "x_eval": 3,
        }
        response = self.client.post("/api/interpolar", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("valores x_i repetidos", response.get_json()["error"])

    def test_no_numericos_nan_infinity_booleanos(self):
        valores = ["texto", math.nan, math.inf, True]
        for valor in valores:
            payload = {**self.oficial, "puntos": [dict(p) for p in self.oficial["puntos"]]}
            payload["puntos"][0]["y"] = valor
            with self.subTest(valor=valor):
                response = self.client.post("/api/interpolar", json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertFalse(response.get_json()["ok"])


if __name__ == "__main__":
    unittest.main()

