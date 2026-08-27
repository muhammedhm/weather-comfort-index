export default function CityCard({ city, onSelect, selected }) {
  return (
    <button
      className={`city-card ${selected ? "city-card--selected" : ""}`}
      onClick={() => onSelect(city)}
    >
      <div className="city-card__rank">#{city.rank}</div>
      <h3>
        {city.city_name}
        {city.country ? `, ${city.country}` : ""}
      </h3>
      <p className="city-card__desc">{city.weather_description}</p>
      <div className="city-card__stats">
        <span>{city.temperature_c}°C</span>
        <span>{city.humidity_pct}% humidity</span>
        <span>{city.wind_speed_ms} m/s wind</span>
      </div>
      <div className="city-card__score">
        <span className="score-value">{city.comfort_score}</span>
        <span className="score-label">Comfort Score</span>
      </div>
    </button>
  );
}
