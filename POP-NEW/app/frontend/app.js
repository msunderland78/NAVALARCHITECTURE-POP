const form = document.querySelector("#pop-form");
const statusNode = document.querySelector("#status");
const resultTable = document.querySelector("#result-table");
const jsonOutput = document.querySelector("#json-output");
const chart = document.querySelector("#result-chart");
let latestPayload = null;

document.querySelector("#load-sample").addEventListener("click", async () => {
  const response = await fetch("/api/sample");
  const data = await response.json();
  fillForm(data);
});

document.querySelector("#copy-json").addEventListener("click", async () => {
  if (!latestPayload) return;
  await navigator.clipboard.writeText(JSON.stringify(latestPayload, null, 2));
  statusNode.textContent = "Copied";
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  statusNode.textContent = "Running";
  const response = await fetch("/api/run", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(readForm())
  });
  latestPayload = await response.json();
  renderResults(latestPayload);
  statusNode.textContent = "Complete";
});

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
}

function renderResults(payload) {
  const rounded = payload.legacyRounded;
  const rows = [
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
  renderChart(rounded);
}

function renderChart(result) {
  const values = [
    ["J", result.advanceCoefficient],
    ["KT", result.thrustCoefficient],
    ["10KQ", result.torqueCoefficient * 10],
    ["Eta", result.openWaterEfficiency]
  ];
  const maxValue = Math.max(...values.map(item => item[1]), 0.1);
  const bars = values.map(([label, value], index) => {
    const x = 80 + index * 130;
    const height = Math.max(2, value / maxValue * 200);
    const y = 240 - height;
    return `<rect x="${x}" y="${y}" width="58" height="${height}" fill="#2f7d8c"></rect><text x="${x + 29}" y="265" text-anchor="middle">${label}</text><text x="${x + 29}" y="${y - 8}" text-anchor="middle">${value.toFixed(3)}</text>`;
  }).join("");
  chart.innerHTML = `<line x1="48" y1="240" x2="600" y2="240" stroke="#94a3ad"></line>${bars}`;
}

function number(data, key) {
  return Number(data.get(key));
}

form.dispatchEvent(new Event("submit"));
