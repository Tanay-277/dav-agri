import Plot from "react-plotly.js"

interface BarChartProps {
  labels: string[]
  values: number[]
  title?: string
}

export function BarChart({ labels, values, title }: BarChartProps) {
  return (
    <Plot
      data={[
        {
          type: "bar",
          x: labels,
          y: values,
          marker: { color: "#4f46e5" },
          hovertemplate: "<b>%{x}</b>: %{y:.2f}<extra></extra>",
        },
      ]}
      layout={{
        title: { text: title, font: { size: 13 } },
        margin: { t: 40, r: 16, b: 60, l: 48 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: {
          showgrid: false,
          tickangle: -20,
          linecolor: "#888",
          zeroline: false,
        },
        yaxis: {
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
