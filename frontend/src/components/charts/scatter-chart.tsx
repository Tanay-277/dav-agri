import Plot from "react-plotly.js"

interface ScatterChartProps {
  points: { x: number; y: number }[]
  title?: string
  xLabel?: string
  yLabel?: string
}

export function ScatterChart({
  points,
  title,
  xLabel = "Rainfall (mm)",
  yLabel = "Yield",
}: ScatterChartProps) {
  return (
    <Plot
      data={[
        {
          type: "scatter",
          mode: "markers",
          x: points.map((p) => p.x),
          y: points.map((p) => p.y),
          marker: {
            color: "#10b981",
            size: 9,
            opacity: 0.8,
          },
          hovertemplate: `${xLabel}: %{x:.1f}<br>${yLabel}: %{y:.1f}<extra></extra>`,
        },
      ]}
      layout={{
        title: { text: title, font: { size: 13 } },
        margin: { t: 40, r: 16, b: 44, l: 48 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: { title: { text: xLabel }, showgrid: false, zeroline: false },
        yaxis: {
          title: { text: yLabel },
          griddash: "dot",
          gridcolor: "rgba(128,128,128,0.2)",
          zeroline: false,
        },
        font: { family: "Inter, sans-serif", size: 12 },
      }}
      config={{ responsive: true, displayModeBar: false }}
      className="h-[340px] w-full"
      useResizeHandler
    />
  )
}
