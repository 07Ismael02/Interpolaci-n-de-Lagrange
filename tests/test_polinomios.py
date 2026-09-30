import unittest

from metodos.polinomios import (
    escalar,
    evaluar,
    multiplicar_por_factor,
    polinomio_a_texto,
    sumar,
)


class PolinomiosTests(unittest.TestCase):
    def test_multiplicar_por_factor(self):
        # (x + 1)(x - 2) = x² - x - 2
        resultado = multiplicar_por_factor([1, 1], 2)
        self.assertEqual(resultado, [-2, -1, 1])

    def test_escalar_y_sumar(self):
        self.assertEqual(escalar([1, -2, 3], 2), [2, -4, 6])
        self.assertEqual(sumar([1, 2], [3, 4, 5]), [4, 6, 5])

    def test_evaluar_horner(self):
        self.assertEqual(evaluar([3, 2, 1], 4), 27)

    def test_texto_polinomio_con_fracciones_y_signos(self):
        texto = polinomio_a_texto([1, -5 / 6, 3 / 16, -1 / 96], "L2(x)")
        self.assertEqual(texto, "L2(x) = - 1/96x^3 + 3/16x^2 - 5/6x + 1")


if __name__ == "__main__":
    unittest.main()

