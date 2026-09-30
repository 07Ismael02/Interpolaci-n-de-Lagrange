"use strict";

const OFFICIAL = {
  puntos: [
    { x: 2, y: 150 },
    { x: 4, y: 85 },
    { x: 8, y: 50 },
    { x: 12, y: 70 },
  ],
  x_eval: 6,
};

let currentResult = null;
let resizeFrame = null;
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function formatNumber(value, digits = 11) {
  if (value === null || value === undefined) return "—";
  const number = Number(value);
  if (!Number.isFinite(number)) return String(value);
  if (Math.abs(number) < 5e-14) return "0";
  const absolute = Math.abs(number);
  if (absolute >= 1e8 || absolute < 1e-7) return number.toExponential(digits - 1).replace(/\.0+e/, "e");
  return Number(number.toPrecision(digits)).toString();
}

function showMessage(text, type = "error") {
  const element = $("#message");
  element.textContent = text;
  element.className = `message${type === "success" ? " success" : ""}`;
  element.hidden = false;
  element.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function hideMessage() {
  $("#message").hidden = true;
}

function setBusy(button, busy) {
  if (!button.dataset.label) button.dataset.label = button.textContent;
  button.disabled = busy;
  button.textContent = busy ? "Calculando…" : button.dataset.label;
}

function hideResults() {
  currentResult = null;
  $$(".result-section").forEach((section) => { section.hidden = true; });
  $("#copy-status").textContent = "";
}

function buildPointInputs(values = null) {
  const body = $("#points-input");
  body.innerHTML = "";
  for (let i = 0; i < 4; i += 1) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td class="node-label">x<sub>${i}</sub></td>
      <td><input class="x-input" type="number" step="any" aria-label="Valor x del punto ${i}" data-index="${i}"></td>
      <td><input class="y-input" type="number" step="any" aria-label="Valor y del punto ${i}" data-index="${i}"></td>`;
    body.append(row);
  }
  if (values) {
    $$(".x-input").forEach((input, i) => { input.value = values.puntos[i].x; });
    $$(".y-input").forEach((input, i) => { input.value = values.puntos[i].y; });
    $("#x-eval").value = values.x_eval;
  } else {
    $("#x-eval").value = "";
  }
  hideResults();
}

function readFinite(input, label) {
  if (input.value.trim() === "") throw new Error(`${label} no puede estar vacío.`);
  const value = Number(input.value);
  if (!Number.isFinite(value)) throw new Error(`${label} debe ser un número real finito.`);
  return value;
}

function readPayload() {
  const xs = $$(".x-input");
  const ys = $$(".y-input");
  const puntos = xs.map((input, i) => ({
    x: readFinite(input, `x${i}`),
    y: readFinite(ys[i], `y${i}`),
  }));
  return { puntos, x_eval: readFinite($("#x-eval"), "x_eval") };
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  let data;
  try { data = await response.json(); }
  catch { throw new Error("El servidor devolvió una respuesta no válida."); }
  if (!response.ok || !data.ok) throw new Error(data.error || `Error HTTP ${response.status}.`);
  return data;
}

function renderBase(base) {
  const denominatorSteps = base.factores.map((factor) => factor.factor_denominador).join("");
  const evaluationProducts = base.factores.map((factor) =>
    `(${formatNumber(factor.numerador_en_x_eval)} / ${formatNumber(factor.denominador_numerico)})`
  ).join(" · ");
  $("#base-" + base.indice).innerHTML = `
    <div class="base-grid">
      <div class="math-panel">
        <h3>Reemplazo de nodos</h3>
        <div class="math-line">${base.formula_producto}</div>
        <div class="math-line">Denominador = ${denominatorSteps} = ${formatNumber(base.denominador)}</div>
        <div class="math-line math-line--result">${base.polinomio_texto}</div>
      </div>
      <div class="base-facts">
        <div class="fact"><span>Nodo propio</span><strong>x${base.indice} = ${formatNumber(base.x_k)}</strong></div>
        <div class="fact"><span>Denominador</span><strong>${formatNumber(base.denominador)}</strong></div>
        <div class="fact"><span>Evaluación en x_eval</span><strong>L${base.indice}(${formatNumber(currentResult.x_eval)}) = ${evaluationProducts} = ${formatNumber(base.valor_en_x_eval)}</strong></div>
        <div class="fact"><span>Aporte y${base.indice}L${base.indice}</span><strong>${formatNumber(base.y_k)} · ${formatNumber(base.valor_en_x_eval)} = ${formatNumber(base.aporte_en_x_eval)}</strong></div>
      </div>
    </div>`;
}

function renderPolynomial(result) {
  const coefficients = result.polinomio.coeficientes;
  const coefficientCards = [];
  for (let power = result.grado; power >= 0; power -= 1) {
    coefficientCards.push(`<div class="coefficient"><span>a${power}</span><strong>${formatNumber(coefficients[power])}</strong></div>`);
  }
  $("#polynomial-content").innerHTML = `
    <div class="construction">
      <div class="construction-stage"><span>Fórmula</span><code>${result.polinomio.formula_general}</code></div>
      <div class="construction-stage"><span>Reemplazo de y_k</span><code>${result.polinomio.formula_con_valores}</code></div>
      <div class="construction-stage"><span>Sustitución de las bases</span><code>${result.polinomio.sustitucion_bases}</code></div>
      <div class="construction-stage"><span>Forma estándar simplificada</span><code>${result.polinomio.texto}</code></div>
    </div>
    <div class="coefficient-grid">${coefficientCards.join("")}</div>`;
}

function evaluationExpression(result) {
  return result.evaluacion.terminos.map((term, index) => {
    const coefficient = term.coeficiente_texto;
    const magnitude = coefficient.startsWith("-") ? coefficient.slice(1) : coefficient;
    const factor = term.potencia === 0 ? `(${magnitude})` : `(${magnitude})(${formatNumber(result.x_eval)}^${term.potencia})`;
    if (index === 0) return coefficient.startsWith("-") ? `-${factor}` : factor;
    return `${coefficient.startsWith("-") ? "−" : "+"} ${factor}`;
  }).join(" ");
}

function renderEvaluation(result) {
  const rows = result.evaluacion.terminos.map((term) => `
    <div class="term-row"><span>(${term.coeficiente_texto}) · ${formatNumber(result.x_eval)}<sup>${term.potencia}</sup></span><strong>${formatNumber(term.aporte)}</strong></div>`).join("");
  $("#evaluation-content").innerHTML = `
    <div class="evaluation-grid">
      <div class="math-panel">
        <h3>Sustitución numérica</h3>
        <div class="math-line">P${result.grado}(${formatNumber(result.x_eval)}) = ${evaluationExpression(result)}</div>
        <div class="term-list">${rows}</div>
        <div class="math-line math-line--result">P${result.grado}(${formatNumber(result.x_eval)}) = ${formatNumber(result.resultado)}</div>
      </div>
      <div class="result-panel"><span>Latencia estimada</span><strong>${formatNumber(result.resultado)}</strong><small>milisegundos</small></div>
    </div>`;
}

function renderVerification(result) {
  const body = $("#verification-table tbody");
  body.innerHTML = "";
  result.comprobaciones.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${formatNumber(item.x)}</td><td>${formatNumber(item.y_original)}</td><td>${formatNumber(item.p_x)}</td><td>${formatNumber(item.diferencia)}</td>`;
    body.append(row);
  });
  $("#max-difference").innerHTML = `Máximo |y<sub>i</sub> − P<sub>3</sub>(x<sub>i</sub>)| = <strong>${formatNumber(result.max_diferencia_nodos)}</strong>`;
}

function drawChart(result) {
  const canvas = $("#lagrange-chart");
  const frame = canvas.parentElement;
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  const width = Math.max(320, frame.clientWidth);
  const height = Math.max(300, frame.clientHeight);
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, width, height);

  const margin = { left: width < 520 ? 58 : 72, right: 24, top: 22, bottom: 57 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const allY = [
    ...result.grafica.curva.map((point) => point.y),
    ...result.grafica.nodos.map((point) => point.y),
    result.grafica.punto_interpolado.y,
  ];
  let yMin = Math.min(...allY);
  let yMax = Math.max(...allY);
  const yPadding = Math.max((yMax - yMin) * 0.12, 1);
  yMin -= yPadding;
  yMax += yPadding;
  const [xMin, xMax] = result.grafica.intervalo;
  const mapX = (x) => margin.left + ((x - xMin) / (xMax - xMin)) * plotWidth;
  const mapY = (y) => margin.top + (1 - (y - yMin) / (yMax - yMin)) * plotHeight;

  ctx.font = "12px system-ui";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  for (let i = 0; i <= 5; i += 1) {
    const x = margin.left + (plotWidth * i) / 5;
    const value = xMin + ((xMax - xMin) * i) / 5;
    ctx.strokeStyle = "#e2e8f0";
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(x, margin.top); ctx.lineTo(x, margin.top + plotHeight); ctx.stroke();
    ctx.fillStyle = "#64748b";
    ctx.fillText(formatNumber(value, 5), x, margin.top + plotHeight + 9);
  }
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for (let i = 0; i <= 5; i += 1) {
    const y = margin.top + (plotHeight * i) / 5;
    const value = yMax - ((yMax - yMin) * i) / 5;
    ctx.strokeStyle = "#e2e8f0";
    ctx.beginPath(); ctx.moveTo(margin.left, y); ctx.lineTo(margin.left + plotWidth, y); ctx.stroke();
    ctx.fillStyle = "#64748b";
    ctx.fillText(formatNumber(value, 5), margin.left - 8, y);
  }

  ctx.strokeStyle = "#17324f";
  ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.moveTo(margin.left, margin.top); ctx.lineTo(margin.left, margin.top + plotHeight); ctx.lineTo(margin.left + plotWidth, margin.top + plotHeight); ctx.stroke();

  ctx.strokeStyle = "#087d96";
  ctx.lineWidth = 3;
  ctx.beginPath();
  result.grafica.curva.forEach((point, index) => {
    const px = mapX(point.x); const py = mapY(point.y);
    if (index === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
  });
  ctx.stroke();

  result.grafica.nodos.forEach((point) => {
    ctx.fillStyle = "#1769e0";
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(mapX(point.x), mapY(point.y), 6, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  });

  const estimated = result.grafica.punto_interpolado;
  const ex = mapX(estimated.x); const ey = mapY(estimated.y);
  ctx.fillStyle = "#e08a13";
  ctx.strokeStyle = "#fff";
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(ex, ey - 9); ctx.lineTo(ex + 9, ey); ctx.lineTo(ex, ey + 9); ctx.lineTo(ex - 9, ey); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.fillStyle = "#7a4600";
  ctx.font = "700 12px system-ui";
  ctx.textAlign = ex > width * .7 ? "right" : "left";
  ctx.textBaseline = "bottom";
  ctx.fillText(`(${formatNumber(estimated.x)}, ${formatNumber(estimated.y)})`, ex + (ex > width * .7 ? -12 : 12), ey - 8);

  ctx.fillStyle = "#334155";
  ctx.font = "700 12px system-ui";
  ctx.textAlign = "center";
  ctx.textBaseline = "bottom";
  ctx.fillText(result.grafica.eje_x, margin.left + plotWidth / 2, height - 4);
  ctx.save();
  ctx.translate(15, margin.top + plotHeight / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText(result.grafica.eje_y, 0, 0);
  ctx.restore();
}

function renderResult(result) {
  currentResult = result;
  result.bases.forEach(renderBase);
  renderPolynomial(result);
  renderEvaluation(result);
  renderVerification(result);
  $("#interpretation").textContent = result.interpretacion;
  $("#chart-interval").textContent = `Intervalo [${formatNumber(result.grafica.intervalo[0])}, ${formatNumber(result.grafica.intervalo[1])}]`;
  $$(".result-section").forEach((section) => { section.hidden = false; });
  drawChart(result);
}

function buildProcedure(result) {
  const lines = [
    "INTERPOLACIÓN POLINÓMICA DE LAGRANGE",
    "", "1. DATOS DEL PROBLEMA",
    ...result.nodos.map((node) => `x${node.indice} = ${formatNumber(node.x)}, y${node.indice} = ${formatNumber(node.y)}`),
    `x_eval = ${formatNumber(result.x_eval)}`,
    "", "2. FÓRMULA GENERAL",
    "L_k(x) = producto[(x - x_i)/(x_k - x_i)], i != k",
    `P${result.grado}(x) = sumatoria[y_k L_k(x)]`,
  ];
  result.bases.forEach((base) => {
    lines.push(
      "", `${base.indice + 3}. CONSTRUCCIÓN DE L${base.indice}(x)`,
      base.formula_producto,
      `Denominador = ${base.denominador_factores_texto} = ${formatNumber(base.denominador)}`,
      base.polinomio_texto,
      `L${base.indice}(${formatNumber(result.x_eval)}) = ${formatNumber(base.valor_en_x_eval)}`,
      `y${base.indice}L${base.indice} = ${formatNumber(base.aporte_en_x_eval)}`,
    );
  });
  lines.push(
    "", "7. CONSTRUCCIÓN DEL POLINOMIO",
    result.polinomio.formula_con_valores,
    result.polinomio.sustitucion_bases,
    result.polinomio.texto,
    "", "8. EVALUACIÓN",
    `P${result.grado}(${formatNumber(result.x_eval)}) = ${evaluationExpression(result)}`,
    ...result.evaluacion.terminos.map((term) => `  Aporte de grado ${term.potencia}: ${formatNumber(term.aporte)}`),
    `P${result.grado}(${formatNumber(result.x_eval)}) = ${formatNumber(result.resultado)}`,
    "", "9. COMPROBACIÓN",
    ...result.comprobaciones.map((item) => `P${result.grado}(${formatNumber(item.x)}) = ${formatNumber(item.p_x)}; original = ${formatNumber(item.y_original)}; diferencia = ${formatNumber(item.diferencia)}`),
    `Máximo |y_i - P${result.grado}(x_i)| = ${formatNumber(result.max_diferencia_nodos)}`,
    "", "10. INTERPRETACIÓN",
    result.interpretacion,
  );
  return lines.join("\n");
}

async function interpolate() {
  hideMessage();
  const button = $("#interpolate");
  try {
    const payload = readPayload();
    setBusy(button, true);
    const result = await postJson("/api/interpolar", payload);
    renderResult(result);
    $("#paso-2").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    hideResults();
    showMessage(error.message);
  } finally {
    setBusy(button, false);
  }
}

async function copyProcedure() {
  if (!currentResult) return;
  const text = buildProcedure(currentResult);
  const status = $("#copy-status");
  try {
    await navigator.clipboard.writeText(text);
    status.textContent = "Procedimiento copiado.";
  } catch {
    const area = document.createElement("textarea");
    area.value = text;
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.append(area);
    area.select();
    const copied = document.execCommand("copy");
    area.remove();
    status.textContent = copied ? "Procedimiento copiado." : "No fue posible copiar automáticamente.";
  }
}

$("#load-official").addEventListener("click", () => { buildPointInputs(OFFICIAL); hideMessage(); });
$("#clear-inputs").addEventListener("click", () => { buildPointInputs(); hideMessage(); });
$("#interpolate").addEventListener("click", interpolate);
$("#copy-procedure").addEventListener("click", copyProcedure);
$("#points-input").addEventListener("input", hideResults);
$("#x-eval").addEventListener("input", hideResults);
window.addEventListener("resize", () => {
  if (!currentResult) return;
  if (resizeFrame) cancelAnimationFrame(resizeFrame);
  resizeFrame = requestAnimationFrame(() => drawChart(currentResult));
});

buildPointInputs(OFFICIAL);

