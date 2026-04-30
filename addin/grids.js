/**
 * Lightweight editable data grids per chart-type-grid-shape.
 * Vanilla DOM, no framework. Each grid:
 *   - mounts into a host element
 *   - emits a `change` CustomEvent on the host whenever the user edits
 *   - exposes getState() returning the current grid state
 *
 * Grid shapes (matched to TYPES[t].grid in chart-types.js):
 *   - rowsByCategory:   first column is category label; remaining columns
 *                       are series; cells are numeric.
 *   - pointsBySeries:   columns = "x" | "<series>" | repeat...; each row
 *                       is one x value with a y for each series.
 *   - slices:           two columns: "label" | "value".
 *   - waterfall:        columns = "category" | "value" | "subtotal".
 */

function emit(host) {
  host.dispatchEvent(new CustomEvent("change"));
}

function n(v, fallback = 0) {
  const x = Number(String(v).replace(/[, %]/g, ""));
  return Number.isFinite(x) ? x : fallback;
}

function mountTable(host, headers, rows, onCellInput) {
  host.innerHTML = "";
  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const trh = document.createElement("tr");
  for (const h of headers) {
    const th = document.createElement("th");
    th.textContent = h;
    trh.appendChild(th);
  }
  thead.appendChild(trh);
  table.appendChild(thead);
  const tbody = document.createElement("tbody");
  rows.forEach((cells, ri) => {
    const tr = document.createElement("tr");
    cells.forEach((val, ci) => {
      const td = document.createElement("td");
      td.contentEditable = "true";
      td.textContent = String(val ?? "");
      td.addEventListener("input", () => onCellInput(ri, ci, td.textContent));
      td.addEventListener("paste", (e) => handlePaste(e, host, ri, ci));
      td.addEventListener("blur", () => emit(host));
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  host.appendChild(table);
}

/** Excel-style paste: TSV/CSV with newlines. */
function handlePaste(e, host, ri, ci) {
  const text = e.clipboardData?.getData("text") ?? "";
  if (!text.includes("\t") && !text.includes("\n")) return; // single-cell paste, default behavior
  e.preventDefault();
  const grid = host.__grid;
  if (!grid) return;
  const rows = text.replace(/\r/g, "").split("\n").filter((l) => l.length > 0);
  for (let r = 0; r < rows.length; r++) {
    const cols = rows[r].split("\t");
    for (let c = 0; c < cols.length; c++) {
      grid.setCell(ri + r, ci + c, cols[c]);
    }
  }
  grid.render();
  emit(host);
}

// ------------------------------------------------------------
// rowsByCategory: first col = category, rest = series

export function makeRowsByCategoryGrid(host, defaults) {
  const state = {
    categories: [...defaults.categories],
    series: defaults.series.map((s) => ({ name: s.name, values: [...s.values] })),
    stacked: defaults.stacked ?? false,
  };

  function render() {
    const headers = ["Category", ...state.series.map((s) => s.name)];
    const rows = state.categories.map((cat, i) => [
      cat,
      ...state.series.map((s) => s.values[i] ?? 0),
    ]);
    mountTable(host, headers, rows, (ri, ci, value) => {
      if (ci === 0) {
        state.categories[ri] = String(value).trim();
      } else {
        state.series[ci - 1].values[ri] = n(value);
      }
    });
  }

  host.__grid = {
    setCell(r, c, v) {
      while (state.categories.length <= r) state.categories.push("");
      while (state.series[c - 1] && state.series[c - 1].values.length <= r) {
        state.series[c - 1].values.push(0);
      }
      if (c === 0) state.categories[r] = String(v).trim();
      else if (state.series[c - 1]) state.series[c - 1].values[r] = n(v);
    },
    render,
    addRow() {
      state.categories.push(`Cat ${state.categories.length + 1}`);
      state.series.forEach((s) => s.values.push(0));
      render();
      emit(host);
    },
    delRow() {
      if (state.categories.length <= 1) return;
      state.categories.pop();
      state.series.forEach((s) => s.values.pop());
      render();
      emit(host);
    },
    addCol() {
      state.series.push({
        name: `Series ${state.series.length + 1}`,
        values: state.categories.map(() => 0),
      });
      render();
      emit(host);
    },
    delCol() {
      if (state.series.length <= 1) return;
      state.series.pop();
      render();
      emit(host);
    },
    getState: () => state,
    onHeaderEdit: () => {},
  };
  render();

  // Allow editing series names by double-clicking on header cells.
  host.addEventListener("dblclick", (e) => {
    const th = e.target.closest("th");
    if (!th || !th.parentElement) return;
    const idx = Array.from(th.parentElement.children).indexOf(th);
    if (idx < 1) return;
    const newName = prompt("Series name", state.series[idx - 1].name);
    if (newName) {
      state.series[idx - 1].name = newName;
      render();
      emit(host);
    }
  });
}

// ------------------------------------------------------------
// pointsBySeries: rows are x values; columns are x | series1 | series2 ...

export function makePointsBySeriesGrid(host, defaults) {
  const state = {
    series: defaults.series.map((s) => ({
      name: s.name,
      points: s.points.map((p) => ({ x: p.x, y: p.y })),
    })),
  };
  // x values shared by all series — take from series[0]
  function xs() { return state.series[0].points.map((p) => p.x); }

  function render() {
    const headers = ["x", ...state.series.map((s) => s.name)];
    const xVals = xs();
    const rows = xVals.map((x, i) => [
      x,
      ...state.series.map((s) => s.points[i]?.y ?? 0),
    ]);
    mountTable(host, headers, rows, (ri, ci, value) => {
      if (ci === 0) {
        const v = n(value, value);
        state.series.forEach((s) => {
          if (s.points[ri]) s.points[ri].x = v;
        });
      } else {
        const s = state.series[ci - 1];
        if (s && s.points[ri]) s.points[ri].y = n(value);
      }
    });
  }

  host.__grid = {
    setCell(r, c, v) {
      // Ensure rows exist for all series.
      state.series.forEach((s) => {
        while (s.points.length <= r) s.points.push({ x: r + 1, y: 0 });
      });
      if (c === 0) {
        const x = n(v, v);
        state.series.forEach((s) => (s.points[r].x = x));
      } else if (state.series[c - 1]) {
        state.series[c - 1].points[r].y = n(v);
      }
    },
    render,
    addRow() {
      const lastX = xs().slice(-1)[0] ?? 0;
      const nextX = typeof lastX === "number" ? lastX + 1 : `${lastX}+1`;
      state.series.forEach((s) =>
        s.points.push({ x: nextX, y: 0 }),
      );
      render();
      emit(host);
    },
    delRow() {
      if (xs().length <= 1) return;
      state.series.forEach((s) => s.points.pop());
      render();
      emit(host);
    },
    addCol() {
      const x = xs();
      state.series.push({
        name: `Series ${state.series.length + 1}`,
        points: x.map((xv) => ({ x: xv, y: 0 })),
      });
      render();
      emit(host);
    },
    delCol() {
      if (state.series.length <= 1) return;
      state.series.pop();
      render();
      emit(host);
    },
    getState: () => state,
  };
  render();

  host.addEventListener("dblclick", (e) => {
    const th = e.target.closest("th");
    if (!th || !th.parentElement) return;
    const idx = Array.from(th.parentElement.children).indexOf(th);
    if (idx < 1) return;
    const newName = prompt("Series name", state.series[idx - 1].name);
    if (newName) {
      state.series[idx - 1].name = newName;
      render();
      emit(host);
    }
  });
}

// ------------------------------------------------------------
// slices: rows are slices, two columns: label | value

export function makeSlicesGrid(host, defaults) {
  const state = {
    slices: defaults.slices.map((s) => ({ label: s.label, value: s.value })),
    donut: defaults.donut ?? false,
  };

  function render() {
    mountTable(
      host,
      ["Label", "Value"],
      state.slices.map((s) => [s.label, s.value]),
      (ri, ci, value) => {
        if (ci === 0) state.slices[ri].label = String(value).trim();
        else state.slices[ri].value = n(value);
      },
    );
  }

  host.__grid = {
    setCell(r, c, v) {
      while (state.slices.length <= r) state.slices.push({ label: "", value: 0 });
      if (c === 0) state.slices[r].label = String(v).trim();
      else state.slices[r].value = n(v);
    },
    render,
    addRow() {
      state.slices.push({ label: `Slice ${state.slices.length + 1}`, value: 0 });
      render();
      emit(host);
    },
    delRow() {
      if (state.slices.length <= 1) return;
      state.slices.pop();
      render();
      emit(host);
    },
    addCol() {},
    delCol() {},
    getState: () => state,
  };
  render();
}

// ------------------------------------------------------------
// waterfall: rows are categories; columns: category | value | subtotal

export function makeWaterfallGrid(host, defaults) {
  const state = {
    categories: [...defaults.categories],
    values: [...defaults.values],
    subtotalIndices: new Set(defaults.subtotalIndices ?? []),
  };

  function render() {
    host.innerHTML = "";
    const table = document.createElement("table");
    const thead = document.createElement("thead");
    thead.innerHTML = "<tr><th>Category</th><th>Value</th><th>Subtotal?</th></tr>";
    table.appendChild(thead);
    const tbody = document.createElement("tbody");
    state.categories.forEach((cat, i) => {
      const tr = document.createElement("tr");
      const tdCat = document.createElement("td");
      tdCat.contentEditable = "true";
      tdCat.textContent = cat;
      tdCat.addEventListener("input", () => {
        state.categories[i] = tdCat.textContent.trim();
      });
      tdCat.addEventListener("blur", () => emit(host));
      const tdVal = document.createElement("td");
      tdVal.contentEditable = "true";
      tdVal.textContent = state.values[i];
      tdVal.classList.add("cs-numeric");
      tdVal.addEventListener("input", () => {
        state.values[i] = n(tdVal.textContent);
      });
      tdVal.addEventListener("blur", () => emit(host));
      const tdTot = document.createElement("td");
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = state.subtotalIndices.has(i);
      cb.addEventListener("change", () => {
        if (cb.checked) state.subtotalIndices.add(i);
        else state.subtotalIndices.delete(i);
        emit(host);
      });
      tdTot.appendChild(cb);
      tr.append(tdCat, tdVal, tdTot);
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    host.appendChild(table);
  }

  host.__grid = {
    setCell(r, c, v) {
      while (state.categories.length <= r) {
        state.categories.push("");
        state.values.push(0);
      }
      if (c === 0) state.categories[r] = String(v).trim();
      else if (c === 1) state.values[r] = n(v);
    },
    render,
    addRow() {
      state.categories.push(`Step ${state.categories.length + 1}`);
      state.values.push(0);
      render();
      emit(host);
    },
    delRow() {
      if (state.categories.length <= 2) return;
      state.subtotalIndices.delete(state.categories.length - 1);
      state.categories.pop();
      state.values.pop();
      render();
      emit(host);
    },
    addCol() {},
    delCol() {},
    getState: () => ({
      categories: state.categories,
      values: state.values,
      subtotalIndices: [...state.subtotalIndices].sort((a, b) => a - b),
    }),
  };
  render();
}

export function mountGridForType(host, type, defaults) {
  if (type === "bar" || type === "area") {
    return makeRowsByCategoryGrid(host, defaults);
  }
  if (type === "line" || type === "scatter") {
    return makePointsBySeriesGrid(host, defaults);
  }
  if (type === "pie") return makeSlicesGrid(host, defaults);
  if (type === "waterfall") return makeWaterfallGrid(host, defaults);
  throw new Error(`No grid for chart type: ${type}`);
}
