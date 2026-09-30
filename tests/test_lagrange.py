import math
import unittest

from metodos.lagrange import interpolar_lagrange
from metodos.polinomios import evaluar
from metodos.validaciones import ErrorValidacion


X_OFICIAL = [2, 4, 8, 12]
Y_OFICIAL = [150, 85, 50, 70]


class LagrangeTests(unittest.TestCase):
    def setUp(self):
        self.resultado = interpolar_lagrange(X_OFICIAL, Y_OFICIAL, 6)

    def test_caso_oficial(self):
        self.assertAlmostEqual(self.resultado["resultado"], 55.25, places=11)
        self.assertEqual(self.resultado["grado"], 3)
        self.assertEqual(self.resultado["complejidad"], "O(n²)")

    def test_reproduce_nodos(self):
        for esperado, comprobacion in zip(Y_OFICIAL, self.resultado["comprobaciones"]):
            self.assertAlmostEqual(comprobacion["p_x"], esperado, places=10)
            self.assertAlmostEqual(comprobacion["diferencia"], 0.0, places=10)
        self.assertLess(self.resultado["max_diferencia_nodos"], 1e-10)

    def test_coeficientes_oficiales(self):
        esperados_ascendentes = [261, -1651 / 24, 227 / 32, -43 / 192]
        for obtenido, esperado in zip(
            self.resultado["polinomio"]["coeficientes"], esperados_ascendentes
        ):
            self.assertAlmostEqual(obtenido, esperado, places=11)

    def test_coeficientes_de_bases_oficiales(self):
        esperados = [
            [16 / 5, -22 / 15, 1 / 5, -1 / 120],
            [-3, 17 / 8, -11 / 32, 1 / 64],
            [1, -5 / 6, 3 / 16, -1 / 96],
            [-1 / 5, 7 / 40, -7 / 160, 1 / 320],
        ]
        for base, coeficientes in zip(self.resultado["bases"], esperados):
            for obtenido, esperado in zip(base["coeficientes"], coeficientes):
                self.assertAlmostEqual(obtenido, esperado, places=12)

    def test_propiedad_delta_de_todas_las_bases(self):
        for k, base in enumerate(self.resultado["bases"]):
            for i, x in enumerate(X_OFICIAL):
                esperado = 1.0 if i == k else 0.0
                self.assertAlmostEqual(evaluar(base["coeficientes"], x), esperado, places=12)

    def test_denominadores_oficiales(self):
        self.assertEqual(
            [base["denominador"] for base in self.resultado["bases"]],
            [-120, 64, -96, 320],
        )

    def test_x_eval_distinto_y_fuera_del_intervalo(self):
        dentro = interpolar_lagrange(X_OFICIAL, Y_OFICIAL, 5)
        fuera = interpolar_lagrange(X_OFICIAL, Y_OFICIAL, 14)
        self.assertNotAlmostEqual(dentro["resultado"], self.resultado["resultado"])
        self.assertTrue(math.isfinite(fuera["resultado"]))
        self.assertEqual(fuera["grafica"]["intervalo"], [2.0, 14.0])

    def test_polinomio_alternativo_anti_hardcoding(self):
        xs = [-2, 0, 1, 3]
        ys = [x * x + 2 * x + 3 for x in xs]
        resultado = interpolar_lagrange(xs, ys, 2)
        self.assertAlmostEqual(resultado["resultado"], 11.0, places=12)
        self.assertNotEqual(resultado["resultado"], 55.25)
        segundo = interpolar_lagrange(xs, ys, 4)
        self.assertAlmostEqual(segundo["resultado"], 27.0, places=12)

    def test_nodos_repetidos(self):
        with self.assertRaisesRegex(ErrorValidacion, "valores x_i repetidos"):
            interpolar_lagrange([1, 2, 2, 4], [3, 4, 5, 6], 3)

    def test_datos_invalidos(self):
        casos = [
            ([1], [2], 1),
            ([1, 2], [3], 1),
            ([1, math.nan], [2, 3], 1),
            ([1, 2], [3, math.inf], 1),
            ([1, 2], [3, 4], math.nan),
            ([1, True], [3, 4], 1),
        ]
        for xs, ys, x_eval in casos:
            with self.subTest(xs=xs, ys=ys, x_eval=x_eval):
                with self.assertRaises(ErrorValidacion):
                    interpolar_lagrange(xs, ys, x_eval)

    def test_evaluacion_directa_coincide_con_forma_estandar(self):
        self.assertAlmostEqual(
            self.resultado["evaluacion"]["resultado_directo"],
            self.resultado["evaluacion"]["resultado_estandar"],
            places=10,
        )

    def test_grafica_contiene_curva_nodos_y_punto(self):
        grafica = self.resultado["grafica"]
        self.assertEqual(grafica["intervalo"], [2.0, 12.0])
        self.assertEqual(len(grafica["curva"]), 241)
        self.assertEqual(len(grafica["nodos"]), 4)
        self.assertAlmostEqual(grafica["punto_interpolado"]["y"], 55.25)

    def test_auditoria_matematica_imprime_resultados(self):
        print("\n--- AUDITORÍA MATEMÁTICA OFICIAL ---")
        for base in self.resultado["bases"]:
            print(base["polinomio_texto"])
        print(self.resultado["polinomio"]["texto"])
        print(f"P3(6) = {self.resultado['resultado']:.12g}")
        for comprobacion in self.resultado["comprobaciones"]:
            print(f"P3({comprobacion['x']:.12g}) = {comprobacion['p_x']:.12g}")
        print(f"max |y_i - P3(x_i)| = {self.resultado['max_diferencia_nodos']:.12g}")
        self.assertAlmostEqual(self.resultado["resultado"], 55.25)


if __name__ == "__main__":
    unittest.main()

