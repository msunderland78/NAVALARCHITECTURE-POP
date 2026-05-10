const form = document.querySelector("#pop-form");
const statusNode = document.querySelector("#status");
const resultTable = document.querySelector("#result-table");
const jsonOutput = document.querySelector("#json-output");
const chart = document.querySelector("#result-chart");
const propellerDiagram = document.querySelector("#propeller-diagram");
const curveChart = document.querySelector("#curve-chart");
const runButton = document.querySelector("#run-button");
const resultMode = document.querySelector("#result-mode");
const verificationTable = document.querySelector("#verification-table");
let latestPayload = null;

document.querySelector("#load-sample").addEventListener("click", async () => {
  const response = await fetch("/api/sample");
  const data = await response.json();
  fillForm(data);
});

document.querySelector("#legacy-pop-file").addEventListener("change", async event => {
  const file = event.target.files[0];
  if (!file) return;
  statusNode.textContent = "Importing";
  try {
    const response = await fetch("/api/import-pop", {
      method: "POST",
      headers: {"Content-Type": "application/octet-stream"},
      body: await file.arrayBuffer()
    });
    const payload = await readJsonResponse(response);
    fillForm(payload.input);
    statusNode.textContent = "Imported";
  } catch (error) {
    statusNode.textContent = "Import Failed";
    jsonOutput.textContent = String(error);
  } finally {
    event.target.value = "";
  }
});

document.querySelector("#copy-json").addEventListener("click", async () => {
  if (!latestPayload) return;
  await navigator.clipboard.writeText(JSON.stringify(latestPayload, null, 2));
  statusNode.textContent = "Copied";
});

document.querySelector("#download-json").addEventListener("click", () => {
  if (!latestPayload) return;
  downloadText(exportBaseName(latestPayload) + ".json", "application/json", JSON.stringify(latestPayload, null, 2));
  statusNode.textContent = "JSON Exported";
});

document.querySelector("#download-csv").addEventListener("click", () => {
  if (!latestPayload) return;
  downloadText(exportBaseName(latestPayload) + ".csv", "text/csv", payloadToCsv(latestPayload));
  statusNode.textContent = "CSV Exported";
});

document.querySelector("#print-report").addEventListener("click", () => {
  if (!latestPayload) return;
  statusNode.textContent = "PDF Ready";
  window.print();
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  runButton.disabled = true;
  statusNode.textContent = "Running";
  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(readForm())
    });
    latestPayload = await readJsonResponse(response);
    renderResults(latestPayload);
    statusNode.textContent = `${labelForMode(latestPayload.mode)} Complete`;
  } catch (error) {
    statusNode.textContent = "Run Failed";
    jsonOutput.textContent = String(error);
  } finally {
    runButton.disabled = false;
  }
});

form.addEventListener("input", () => {
  updateModeFields();
  renderVerification(readForm());
  renderPropeller({
    diameterMeters: Number(form.elements.initialDiameterMeters.value),
    expandedAreaRatio: Number(form.elements.initialExpandedAreaRatio.value),
    pitchDiameterRatio: Number(form.elements.initialPitchDiameterRatio.value)
  }, Number(form.elements.bladeCount.value));
});

form.elements.mode.addEventListener("change", updateModeFields);

function readForm() {
  const data = new FormData(form);
  return {
    projectName: data.get("projectName"),
    runId: data.get("runId"),
    mode: data.get("mode"),
    series: "wageningen_b",
    pitchType: data.get("pitchType"),
    bladeCount: number(data, "bladeCount"),
    initialExpandedAreaRatio: number(data, "initialExpandedAreaRatio"),
    initialPitchDiameterRatio: number(data, "initialPitchDiameterRatio"),
    initialDiameterMeters: number(data, "initialDiameterMeters"),
    diameterMinMeters: number(data, "diameterMinMeters"),
    diameterMaxMeters: number(data, "diameterMaxMeters"),
    requiredThrustKn: number(data, "requiredThrustKn"),
    shipSpeedKnots: number(data, "shipSpeedKnots"),
    wakeFraction: number(data, "wakeFraction"),
    shaftDepthMeters: number(data, "shaftDepthMeters"),
    water: {
      kind: data.get("waterKind"),
      densityKgM3: number(data, "densityKgM3"),
      kinematicViscosityM2S: number(data, "kinematicViscosityM2S")
    },
    burrillBackCavitationPercent: number(data, "burrillBackCavitationPercent")
  };
}

function fillForm(data) {
  form.elements.projectName.value = data.projectName;
  form.elements.runId.value = data.runId;
  form.elements.mode.value = data.mode;
  form.elements.pitchType.value = data.pitchType;
  form.elements.bladeCount.value = data.bladeCount;
  form.elements.initialExpandedAreaRatio.value = data.initialExpandedAreaRatio;
  form.elements.initialPitchDiameterRatio.value = data.initialPitchDiameterRatio;
  form.elements.initialDiameterMeters.value = data.initialDiameterMeters;
  form.elements.diameterMinMeters.value = data.diameterMinMeters;
  form.elements.diameterMaxMeters.value = data.diameterMaxMeters;
  form.elements.requiredThrustKn.value = data.requiredThrustKn;
  form.elements.shipSpeedKnots.value = data.shipSpeedKnots;
  form.elements.wakeFraction.value = data.wakeFraction;
  form.elements.shaftDepthMeters.value = data.shaftDepthMeters;
  form.elements.waterKind.value = data.water.kind;
  form.elements.densityKgM3.value = data.water.densityKgM3;
  form.elements.kinematicViscosityM2S.value = data.water.kinematicViscosityM2S;
  form.elements.burrillBackCavitationPercent.value = data.burrillBackCavitationPercent;
  statusNode.textContent = "Sample Loaded";
  updateModeFields();
  renderVerification(readForm());
  renderPropeller({
    diameterMeters: data.initialDiameterMeters,
    expandedAreaRatio: data.initialExpandedAreaRatio,
    pitchDiameterRatio: data.initialPitchDiameterRatio
  }, data.bladeCount);
}

function renderResults(payload) {
  const rounded = payload.legacyRounded;
  resultMode.textContent = labelForMode(payload.mode);
  const rows = [
    ["Run Mode", labelForMode(payload.mode)],
    ["Diameter Dp (m)", rounded.diameterMeters],
    ["Pitch P (m)", rounded.pitchMeters],
    ["P/Dp", rounded.pitchDiameterRatio],
    ["Ae/Ao", rounded.expandedAreaRatio],
    ["RPM", rounded.rpm],
    ["J", rounded.advanceCoefficient],
    ["KT", rounded.thrustCoefficient],
    ["KQ", rounded.torqueCoefficient],
    ["Eta 0", rounded.openWaterEfficiency],
    ["Thrust (kN)", rounded.thrustKn],
    ["RN", rounded.reynoldsNumber],
    ["Sigma", rounded.cavitationNumber],
    ["Evaluations", rounded.optimizationSearchEvaluationCount ?? "-"]
  ];
  resultTable.innerHTML = rows.map(([name, value]) => `<tr><td>${name}</td><td>${value}</td></tr>`).join("");
  jsonOutput.textContent = JSON.stringify(payload, null, 2);
  renderPropeller(rounded, Number(form.elements.bladeCount.value));
  renderCurveChart(payload.curves, payload.mode);
  renderChart(rounded);
}

function renderVerification(input) {
  const effectiveSpeed = input.shipSpeedKnots * (1 - input.wakeFraction);
  const diameter = input.mode === "optimization"
    ? `${format(input.diameterMinMeters)} to ${format(input.diameterMaxMeters)} m`
    : `${format(input.initialDiameterMeters)} m`;
  const rows = [
    ["Mode", labelForMode(input.mode)],
    ["Project", input.projectName],
    ["Required Thrust", `${format(input.requiredThrustKn)} kN`],
    ["Ship Speed", `${format(input.shipSpeedKnots)} kn`],
    ["Advance Speed", `${format(effectiveSpeed)} kn`],
    ["Diameter", diameter],
    ["Blades", input.bladeCount],
    ["Pitch Type", titleCase(input.pitchType)],
    ["Water Density", `${format(input.water.densityKgM3)} kg/m3`],
    ["Viscosity", `${input.water.kinematicViscosityM2S.toExponential(4)} m2/s`],
    ["Cavitation Limit", `${format(input.burrillBackCavitationPercent)}%`]
  ];
  verificationTable.innerHTML = rows.map(([name, value]) => `<tr><td>${escapeHtml(name)}</td><td>${escapeHtml(value)}</td></tr>`).join("");
}

function renderPropeller(result, bladeCount) {
  const diameter = result.diameterMeters || Number(form.elements.initialDiameterMeters.value);
  const areaRatio = result.expandedAreaRatio || Number(form.elements.initialExpandedAreaRatio.value);
  const pitchRatio = result.pitchDiameterRatio || Number(form.elements.initialPitchDiameterRatio.value);
  const bladeLength = 118;
  const bladeWidth = Math.max(28, Math.min(70, 36 + areaRatio * 42));
  const pitchSkew = Math.max(-22, Math.min(36, (pitchRatio - 0.75) * 65));
  const cx = 320;
  const cy = 170;
  const blades = Array.from({length: bladeCount}, (_, index) => {
    const angle = 360 / bladeCount * index;
    return `
      <g transform="rotate(${angle} ${cx} ${cy})">
        <path d="M ${cx + 26} ${cy - 9}
                 C ${cx + 80} ${cy - bladeWidth} ${cx + bladeLength + pitchSkew} ${cy - bladeWidth / 2} ${cx + 148} ${cy - 6}
                 C ${cx + bladeLength + pitchSkew} ${cy + bladeWidth / 2} ${cx + 82} ${cy + bladeWidth} ${cx + 26} ${cy + 9}
                 Z"
              fill="#2f7d8c" stroke="#174c56" stroke-width="2"></path>
        <path d="M ${cx + 44} ${cy} C ${cx + 92} ${cy - 10} ${cx + 122} ${cy - 8} ${cx + 146} ${cy - 2}"
              fill="none" stroke="#d9f0f3" stroke-width="2"></path>
      </g>`;
  }).join("");
  propellerDiagram.innerHTML = `
    <circle cx="${cx}" cy="${cy}" r="154" fill="none" stroke="#cbd6de" stroke-width="2"></circle>
    ${blades}
    <circle cx="${cx}" cy="${cy}" r="34" fill="#10212f"></circle>
    <circle cx="${cx}" cy="${cy}" r="14" fill="#e9f2f5"></circle>
    <text x="42" y="320">D ${diameter.toFixed(2)} m</text>
    <text x="214" y="320">Ae/Ao ${areaRatio.toFixed(4)}</text>
    <text x="414" y="320">P/D ${pitchRatio.toFixed(4)}</text>`;
}

function renderChart(result) {
  const values = [
    ["J", result.advanceCoefficient],
    ["KT", result.thrustCoefficient],
    ["10KQ", result.torqueCoefficient * 10],
    ["Eta", result.openWaterEfficiency]
  ];
  const maxValue = Math.max(...values.map(item => item[1]), 0.1);
  const baseline = 170;
  const bars = values.map(([label, value], index) => {
    const x = 80 + index * 130;
    const height = Math.max(2, value / maxValue * 130);
    const y = baseline - height;
    return `<rect x="${x}" y="${y}" width="58" height="${height}" fill="#2f7d8c"></rect><text x="${x + 29}" y="198" text-anchor="middle">${label}</text><text x="${x + 29}" y="${y - 8}" text-anchor="middle">${value.toFixed(3)}</text>`;
  }).join("");
  chart.innerHTML = `<line x1="48" y1="${baseline}" x2="600" y2="${baseline}" stroke="#94a3ad"></line>${bars}`;
}

function renderCurveChart(curves, mode = null) {
  if (!curves || !curves.openWater || !curves.openWater.length) {
    curveChart.innerHTML = emptyCurveChart();
    return;
  }
  const width = 760;
  const height = 420;
  const margin = {left: 66, right: 28, top: 28, bottom: 54};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const xMin = 0;
  const xMax = 1.45;
  const yMax = Math.max(
    0.7,
    ...curves.openWater.flatMap(point => [point.kt, point.kq * 10, point.eta]).filter(value => Number.isFinite(value))
  );
  const x = value => margin.left + (value - xMin) / (xMax - xMin) * plotWidth;
  const y = value => margin.top + plotHeight - value / yMax * plotHeight;
  const ktPath = pathFor(curves.openWater, point => point.kt, x, y);
  const kqPath = pathFor(curves.openWater, point => point.kq * 10, x, y);
  const etaPath = pathFor(curves.openWater, point => point.eta, x, y);
  const point = curves.point;
  const markerX = x(point.j);
  const markerY = y(point.kt);
  curveChart.innerHTML = `
    ${gridLines(x, y, yMax)}
    <path d="${ktPath}" fill="none" stroke="#1f6f8b" stroke-width="3"></path>
    <path d="${kqPath}" fill="none" stroke="#a35f22" stroke-width="3"></path>
    <path d="${etaPath}" fill="none" stroke="#28784f" stroke-width="3"></path>
    <line x1="${markerX}" y1="${margin.top}" x2="${markerX}" y2="${margin.top + plotHeight}" stroke="#333f48" stroke-dasharray="5 5"></line>
    <circle cx="${markerX}" cy="${markerY}" r="7" fill="#d7263d" stroke="#ffffff" stroke-width="2"></circle>
    <text x="${markerX + 10}" y="${markerY - 10}" class="chart-label">Current J ${point.j.toFixed(4)}</text>
    <text x="${margin.left}" y="20" class="chart-title">${labelForMode(mode)} open-water characteristics</text>
    <text x="660" y="56" fill="#1f6f8b">KT</text>
    <text x="660" y="80" fill="#a35f22">10KQ</text>
    <text x="660" y="104" fill="#28784f">Eta 0</text>
    <text x="360" y="406" class="axis-label">Advance coefficient J</text>
    <text x="15" y="230" transform="rotate(-90 15 230)" class="axis-label">Coefficient value</text>`;
}

function pathFor(points, valueFor, x, y) {
  return points.map((point, index) => {
    const command = index === 0 ? "M" : "L";
    return `${command} ${x(point.j).toFixed(2)} ${y(Math.max(0, valueFor(point))).toFixed(2)}`;
  }).join(" ");
}

function gridLines(x, y, yMax) {
  const xTicks = [0, 0.25, 0.5, 0.75, 1, 1.25];
  const yTicks = [0, 0.25, 0.5, 0.75, 1].filter(value => value <= yMax);
  const vertical = xTicks.map(value => `<line x1="${x(value)}" y1="28" x2="${x(value)}" y2="366" stroke="#e0e7ed"></line><text x="${x(value)}" y="388" text-anchor="middle">${value.toFixed(2)}</text>`).join("");
  const horizontal = yTicks.map(value => `<line x1="66" y1="${y(value)}" x2="732" y2="${y(value)}" stroke="#e0e7ed"></line><text x="56" y="${y(value) + 4}" text-anchor="end">${value.toFixed(2)}</text>`).join("");
  return `${vertical}${horizontal}<rect x="66" y="28" width="666" height="338" fill="none" stroke="#aebac4"></rect>`;
}

function emptyCurveChart() {
  return `<rect x="66" y="28" width="666" height="338" fill="none" stroke="#aebac4"></rect><text x="380" y="210" text-anchor="middle">Run a case to plot open-water curves</text>`;
}

function number(data, key) {
  return Number(data.get(key));
}

async function readJsonResponse(response) {
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.message || payload.error || "Request failed");
  }
  return payload;
}

function payloadToCsv(payload) {
  const rows = [
    ["section", "name", "value"],
    ...Object.entries(payload.legacyRounded).map(([name, value]) => ["result", name, value]),
    [],
    ["curve", "j", "kt", "kq", "eta"],
    ...payload.curves.openWater.map(point => ["openWater", point.j, point.kt, point.kq, point.eta])
  ];
  return rows.map(row => row.map(csvCell).join(",")).join("\n") + "\n";
}

function csvCell(value) {
  if (value === null || value === undefined) return "";
  const text = String(value);
  if (/[",\n]/.test(text)) return `"${text.replaceAll('"', '""')}"`;
  return text;
}

function downloadText(filename, type, text) {
  const blob = new Blob([text], {type});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function exportBaseName(payload) {
  return `${slug(payload.projectName)}-${slug(payload.runId)}-${payload.mode}`;
}

function slug(value) {
  return String(value || "pop").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "pop";
}

function format(value) {
  if (!Number.isFinite(value)) return "-";
  return Number(value.toFixed(4)).toString();
}

function titleCase(value) {
  return String(value || "").replaceAll("_", " ").replace(/\b[a-z]/g, letter => letter.toUpperCase());
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[character]));
}

function updateModeFields() {
  const mode = form.elements.mode.value;
  document.querySelectorAll("[data-mode-field]").forEach(node => {
    node.classList.toggle("mode-hidden", node.dataset.modeField !== mode);
  });
  runButton.textContent = `Run ${labelForMode(mode)}`;
  if (mode === "optimization") {
    statusNode.textContent = "Optimization Ready";
  } else {
    statusNode.textContent = "Evaluation Ready";
  }
}

function labelForMode(mode) {
  return mode === "optimization" ? "Optimization" : "Evaluation";
}

updateModeFields();
renderVerification(readForm());
renderPropeller({
  diameterMeters: Number(form.elements.initialDiameterMeters.value),
  expandedAreaRatio: Number(form.elements.initialExpandedAreaRatio.value),
  pitchDiameterRatio: Number(form.elements.initialPitchDiameterRatio.value)
}, Number(form.elements.bladeCount.value));
renderChart({
  advanceCoefficient: 0,
  thrustCoefficient: 0,
  torqueCoefficient: 0,
  openWaterEfficiency: 0
});
renderCurveChart(null);
