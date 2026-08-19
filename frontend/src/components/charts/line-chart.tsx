import Plot from "react-plotly.js"
import type { Series } from "@/types/api"

interface LineChartProps {
  labels: string[]
  series: Series[]
  title?: string
}

export function LineChart({ labels, series, title }: LineChartProps) {
  const x = labels.length > 0 ? labels : (series[0]?.labels ?? [])

  const traces = series.map((s) => ({
    name: s.name,
    type: "scatter" as const,
    mode: "lines+markers" as const,
    connectgaps: false,
    x: x.length > 0 ? x : s.labels,
    y: s.values,
    line: { shape: "spline" as const, width: 2.5 },
  }))

  return (
    <Plot
      data={traces as never}
      layout={{
        title: { text: title, font: { size: 13 } },
        margin: { t: 40, r: 16, b: 40, l: 48 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: { showgrid: false, linecolor: "#888", zeroline: false },
        yaxis: {
          griddash: "dot",
          gridcolor: "rgba(128,128,128,0.2)",
          zeroline: false,
        },
        showlegend: true,
        legend: { orientation: "h", y: -0.15 },
        font: { family: "Inter, sans-serif", size: 12 },
        hovermode: "x unified",
      }}
      config={{ responsive: true, displayModeBar: false }}
      className="h-[340px] w-full"
      useResizeHandler
    />
  )
}
