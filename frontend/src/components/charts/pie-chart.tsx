import Plot from "react-plotly.js"

interface PieChartProps {
  labels: string[]
  values: number[]
  title?: string
}

const PALETTE = [
  "#4f46e5",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#06b6d4",
  "#8b5cf6",
]

export function PieChart({ labels, values, title }: PieChartProps) {
  return (
    <Plot
      data={[
        {
          type: "pie",
          labels,
          values,
          hole: 0.55,
          marker: {
            colors: PALETTE.slice(0, labels.length),
            line: { color: "rgba(0,0,0,0)", width: 2 },
          },
          textinfo: "label+percent",
          textposition: "outside",
          hovertemplate:
            "<b>%{label}</b>: %{value} (%{percent})<extra></extra>",
        },
      ]}
      layout={{
        title: { text: title, font: { size: 13 } },
        margin: { t: 40, r: 16, b: 20, l: 16 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        showlegend: false,
        font: { family: "Inter, sans-serif", size: 11 },
      }}
      config={{ responsive: true, displayModeBar: false }}
      className="h-[340px] w-full"
      useResizeHandler
    />
  )
}
