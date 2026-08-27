import { useEffect, useState, useMemo } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import CityCard from "./CityCard.jsx";
import TempTrendChart from "./TempTrendChart.jsx";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

export default function Dashboard() {
  const { getAccessTokenSilently } = useAuth0();
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortKey, setSortKey] = useState("rank"); // rank | temperature_c | humidity_pct
  const [query, setQuery] = useState("");
  const [selectedCity, setSelectedCity] = useState(null);
  const [forecastPoints, setForecastPoints] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const token = await getAccessTokenSilently();
        const res = await fetch(`${API_BASE}/api/cities`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        const data = await res.json();
        if (!cancelled) setCities(data.cities);
      } catch (e) {
        if (!cancelled) setError(e.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [getAccessTokenSilently]);

  async function handleSelectCity(city) {
    setSelectedCity(city);
    setForecastPoints(null);
    try {
      const token = await getAccessTokenSilently();
      const res = await fetch(
        `${API_BASE}/api/cities/${city.city_id}/forecast`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const data = await res.json();
      setForecastPoints(data.points);
    } catch {
      setForecastPoints([]);
    }
  }

  const visibleCities = useMemo(() => {
    let list = cities.filter((c) =>
      c.city_name.toLowerCase().includes(query.toLowerCase())
    );
    if (sortKey === "rank") {
      list = [...list].sort((a, b) => a.rank - b.rank);
    } else {
      // ascending for humidity, descending for temperature (warmest first)
      list = [...list].sort((a, b) =>
        sortKey === "temperature_c"
          ? b[sortKey] - a[sortKey]
          : a[sortKey] - b[sortKey]
      );
    }
    return list;
  }, [cities, sortKey, query]);

  if (loading) return <p className="status-msg">Loading weather data…</p>;
  if (error) return <p className="status-msg status-msg--error">{error}</p>;

  return (
    <div>
      <div className="controls">
        <input
          type="text"
          placeholder="Filter by city name…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select value={sortKey} onChange={(e) => setSortKey(e.target.value)}>
          <option value="rank">Sort: Comfort rank</option>
          <option value="temperature_c">Sort: Warmest first</option>
          <option value="humidity_pct">Sort: Least humid first</option>
        </select>
      </div>

      <div className="city-grid">
        {visibleCities.map((city) => (
          <CityCard
            key={city.city_id}
            city={city}
            onSelect={handleSelectCity}
            selected={selectedCity?.city_id === city.city_id}
          />
        ))}
      </div>

      {selectedCity && (
        <TempTrendChart
          cityName={selectedCity.city_name}
          points={forecastPoints}
        />
      )}
    </div>
  );
}
