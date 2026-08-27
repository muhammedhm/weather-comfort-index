import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function TempTrendChart({ cityName, points }) {
  if (!points || points.length === 0) {
    return <p>Loading forecast…</p>;
  }

  const data = points.map((p) => ({
    time: p.dt.slice(5, 16), // "MM-DD HH:MM"
    temp: p.temp_c,
  }));

  return (
    <div className="chart-wrapper">
      <h4>{cityName} — temperature trend (next ~48h)</h4>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis dataKey="time" tick={{ fontSize: 11 }} />
          <YAxis unit="°C" tick={{ fontSize: 11 }} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="temp"
            stroke="var(--accent)"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
