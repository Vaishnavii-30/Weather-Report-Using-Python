import { Line } from "react-chartjs-2";

export default function TempChart({ items }) {
  const labels = items.map(i => i.time);
  const data = { labels, datasets: [{ label: "Temp (°C)", data: items.map(i=>i.temp), fill:false }] };
  return <Line data={data} options={{responsive:true}} />;
}
