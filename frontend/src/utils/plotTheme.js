const AXIS_COMMON = {
  gridcolor: "#eef1ef",
  zerolinecolor: "#e2e6e3",
  linecolor: "#cfd6d2",
  color: "#55605b",
};

export function chartLayout(layout = {}) {
  return {
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    font: { color: "#1c2321", family: "Segoe UI, system-ui, sans-serif" },
    ...layout,
    xaxis: { ...AXIS_COMMON, ...(layout.xaxis ?? {}) },
    yaxis: { ...AXIS_COMMON, ...(layout.yaxis ?? {}) },
    margin: { t: 20, ...(layout.margin ?? {}) },
  };
}

export const plotConfig = { displayModeBar: false, responsive: true };
