# Interpolación Polinómica de Lagrange

Aplicación web educativa de **Análisis Numérico - Sesión 8**. Automatiza la interpolación de Lagrange para cuatro nodos sin ocultar el procedimiento matemático: construye cada base, expande el polinomio, evalúa el punto solicitado, comprueba los nodos y genera una gráfica.

## Contexto del problema

La actividad estudia la latencia de un microservicio desplegado en un clúster de nube. La variable `x` representa la memoria RAM asignada en GB y `y` la latencia media en milisegundos.

| Nodo | Memoria `x` (GB) | Latencia `y` (ms) |
|---|---:|---:|
| x0 | 2 | 150 |
| x1 | 4 | 85 |
| x2 | 8 | 50 |
| x3 | 12 | 70 |

Se desea estimar la latencia para `x_eval = 6 GB`. El resultado esperado es `P3(6) = 55.25 ms`.

## Método de Lagrange

Para cuatro nodos, el interpolador tiene grado máximo tres:

```text
L_k(x) = producto[(x - x_i) / (x_k - x_i)], i != k
P_3(x) = sumatoria[y_k L_k(x)], k = 0, 1, 2, 3
```

La evaluación principal usa dos ciclos anidados: por cada índice `k`, recorre todos los índices `i` distintos de `k`. Por tanto, su complejidad es `O(n²)`. No se utiliza ninguna función externa de interpolación.

La forma estándar se obtiene con operaciones manuales sobre listas de coeficientes:

- multiplicación por factores `(x - x_i)`;
- escalado por el denominador de cada base;
- multiplicación por `y_k`;
- suma de polinomios.

## Procedimiento mostrado

1. Datos del problema.
2. Fórmula general.
3. Construcción dinámica de `L0(x)`.
4. Construcción dinámica de `L1(x)`.
5. Construcción dinámica de `L2(x)`.
6. Construcción dinámica de `L3(x)`.
7. Construcción y simplificación de `P3(x)`.
8. Sustitución y evaluación en `x_eval`.
9. Comprobación en los cuatro nodos.
10. Interpretación del resultado y gráfica.

## Gráfica

La gráfica se dibuja en un elemento `canvas` responsive y muestra:

- los cuatro datos experimentales;
- la curva continua calculada a partir de los coeficientes de `P3(x)`;
- el punto interpolado resaltado;
- ejes y leyenda.

La biblioteca gráfica es código JavaScript propio de visualización; no participa en la interpolación.

## Estructura

```text
backend/
  app.py                    Servidor y API Flask
  templates/index.html     Interfaz educativa
  static/css/styles.css    Diseño responsive
  static/js/app.js         Interacción y gráfica
metodos/
  validaciones.py          Validaciones numéricas y estructurales
  polinomios.py            Operaciones elementales con coeficientes
  lagrange.py              Algoritmo O(n²) y trazabilidad
tests/
  test_lagrange.py
  test_polinomios.py
  test_app.py
```

## Instalación local

Desde PowerShell, dentro de la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

El entorno `.venv` ya está excluido mediante `.gitignore`.

## Ejecución

```powershell
.\.venv\Scripts\python.exe -m backend.app
```

Abra `http://127.0.0.1:5000`.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas incluyen el caso oficial, reproducción de nodos, bases fundamentales, coeficientes, entradas inválidas, nodos repetidos, API y un polinomio alternativo contra hardcoding.

## API

### `GET /`

Entrega la interfaz educativa.

### `POST /api/interpolar`

```json
{
  "puntos": [
    {"x": 2, "y": 150},
    {"x": 4, "y": 85},
    {"x": 8, "y": 50},
    {"x": 12, "y": 70}
  ],
  "x_eval": 6
}
```

La respuesta incluye nodos, bases, factores, denominadores, coeficientes, evaluación, comprobaciones y muestras de la gráfica.

## Render (uso futuro)

`render.yaml` queda preparado para instalar `requirements.txt` y ejecutar:

```text
gunicorn backend.app:app
```

No se realiza despliegue ni conexión con GitHub desde este proyecto.

## Limitaciones

- La interfaz corresponde a la actividad oficial de cuatro nodos.
- El motor matemático acepta dos o más nodos, pero la API exige exactamente cuatro.
- Se utiliza punto flotante de doble precisión; el formato visual limpia artefactos sin reducir la precisión interna.
- La interpolación fuera del intervalo de los nodos es extrapolación y puede ser menos confiable.
- No se usan NumPy, SciPy, SymPy, Pandas ni solvers externos.

