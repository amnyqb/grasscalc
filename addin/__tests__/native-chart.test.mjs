// Pure unit tests for native-chart.js — no Office.js, no PowerPoint host.
// Run with: node addin/__tests__/native-chart.test.mjs
//
// Verifies:
//   - mapChartType: every chartsmith type → expected PPT enum string
//   - shapeData: row/col layout, length checks, defaults, scatter/line union x

import { mapChartType, shapeData } from "../native-chart.js";
import { strict as assert } from "node:assert";

let passed = 0;
let failed = 0;
function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ✓ ${name}`);
  } catch (err) {
    failed++;
    console.log(`  ✗ ${name}\n    ${err.message}`);
  }
}

// ===================== mapChartType =====================
console.log("mapChartType:");

test("bar grouped vertical → columnClustered", () => {
  assert.equal(mapChartType({ type: "bar" }), "columnClustered");
});
test("bar stacked vertical → columnStacked", () => {
  assert.equal(mapChartType({ type: "bar", stacked: true }), "columnStacked");
});
test("bar grouped horizontal → barClustered", () => {
  assert.equal(mapChartType({ type: "bar", orientation: "horizontal" }), "barClustered");
});
test("bar stacked horizontal → barStacked", () => {
  assert.equal(
    mapChartType({ type: "bar", stacked: true, orientation: "horizontal" }),
    "barStacked",
  );
});
test("line → line", () => {
  assert.equal(mapChartType({ type: "line" }), "line");
});
test("scatter → xyscatter", () => {
  assert.equal(mapChartType({ type: "scatter" }), "xyscatter");
});
test("area stacked (default) → areaStacked", () => {
  assert.equal(mapChartType({ type: "area" }), "areaStacked");
});
test("area unstacked → area", () => {
  assert.equal(mapChartType({ type: "area", stacked: false }), "area");
});
test("pie → pie", () => {
  assert.equal(mapChartType({ type: "pie" }), "pie");
});
test("donut → doughnut", () => {
  assert.equal(mapChartType({ type: "pie", donut: true }), "doughnut");
});
test("waterfall → waterfall", () => {
  assert.equal(mapChartType({ type: "waterfall" }), "waterfall");
});
test("unknown type throws", () => {
  assert.throws(() => mapChartType({ type: "sankey" }));
});

// ===================== shapeData =====================
console.log("\nshapeData:");

test("bar: 2 series x 4 categories", () => {
  const out = shapeData({
    type: "bar",
    categories: ["Q1", "Q2", "Q3", "Q4"],
    series: [
      { name: "EMEA", values: [10, 20, 30, 40] },
      { name: "AMER", values: [15, 25, 35, 45] },
    ],
  });
  assert.deepEqual(out.categories, ["Q1", "Q2", "Q3", "Q4"]);
  assert.deepEqual(out.seriesNames, ["EMEA", "AMER"]);
  assert.deepEqual(out.values, [
    [10, 20, 30, 40],
    [15, 25, 35, 45],
  ]);
});

test("bar: mismatched series length throws with helpful message", () => {
  assert.throws(
    () =>
      shapeData({
        type: "bar",
        categories: ["A", "B", "C"],
        series: [{ name: "X", values: [1, 2] }],
      }),
    /series "X" has 2 values, expected 3/,
  );
});

test("area: shape preserved", () => {
  const out = shapeData({
    type: "area",
    categories: ["Jan", "Feb"],
    series: [{ name: "Free", values: [100, 120] }],
  });
  assert.deepEqual(out.values, [[100, 120]]);
});

test("line: union of x values across series", () => {
  const out = shapeData({
    type: "line",
    series: [
      { name: "A", points: [{ x: 1, y: 10 }, { x: 2, y: 20 }] },
      { name: "B", points: [{ x: 2, y: 25 }, { x: 3, y: 30 }] },
    ],
  });
  assert.deepEqual(out.categories, [1, 2, 3], "x union sorted numerically");
  assert.deepEqual(out.seriesNames, ["A", "B"]);
  // A is missing x=3 → padded to 0; B is missing x=1 → padded to 0
  assert.deepEqual(out.values, [
    [10, 20, 0],
    [0, 25, 30],
  ]);
});

test("scatter: same union behavior", () => {
  const out = shapeData({
    type: "scatter",
    series: [{ name: "S", points: [{ x: 5, y: 1 }, { x: 1, y: 2 }] }],
  });
  // numeric x sorted ascending
  assert.deepEqual(out.categories, [1, 5]);
  assert.deepEqual(out.values, [[2, 1]]);
});

test("pie: single series, slice labels are categories", () => {
  const out = shapeData({
    type: "pie",
    title: "Mix",
    slices: [
      { label: "Direct", value: 38 },
      { label: "Search", value: 32 },
    ],
  });
  assert.deepEqual(out.categories, ["Direct", "Search"]);
  assert.deepEqual(out.seriesNames, ["Mix"]);
  assert.deepEqual(out.values, [[38, 32]]);
});

test("waterfall: single series with categories", () => {
  const out = shapeData({
    type: "waterfall",
    categories: ["FY24", "Vol", "Px", "FY25"],
    values: [120, 18, 12, 150],
    title: "Bridge",
  });
  assert.deepEqual(out.categories, ["FY24", "Vol", "Px", "FY25"]);
  assert.deepEqual(out.values, [[120, 18, 12, 150]]);
  assert.deepEqual(out.seriesNames, ["Bridge"]);
});

test("unknown type throws", () => {
  assert.throws(() => shapeData({ type: "treemap" }));
});

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed === 0 ? 0 : 1);
