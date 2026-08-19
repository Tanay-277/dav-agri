import Plot from "react-plotly.js"

interface HeatmapChartProps {
  columns: string[]
  matrix: number[][]
  title?: string
}

export function HeatmapChart({ columns, matrix, title }: HeatmapChartProps) {
  return (
    <Plot
      data={[
        {
          type: "heatmap",
          z: matrix,
          x: columns,
          y: columns,
          colorscale: "RdBu_r",
          zmin: -1,
          zmax: 1,
          showscale: true,
          colorbar: { outlinewidth: 0, thickness: 8 },
          hovertemplate: "%{x} ↔ %{y}: %{z:.2f}<extra></extra>",
        },
      ]}
      layout={{
        title: { text: title, font: { size: 13 } },
        margin: { t: 40, r: 60, b: 44, l: 60 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: { showgrid: false, tickangle: -35 },
        yaxis: { showgrid: false, autorange: "reversed" },
        font: { family: "Inter, sans-serif", size: 11 },
      }}
      config={{ responsive: true, displayModeBar: false }}
      className="h-[340px] w-full"
      useResizeHandler
    />
  )
}
