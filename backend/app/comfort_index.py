"""
Custom Comfort Index Score (0-100).

This is the part you MUST be able to defend and modify live, so read this
file carefully rather than just running it - you'll be re-deriving a piece
of this logic on camera.

Parameters used (4, satisfies the "at least three" requirement):
  - Temperature (deg C)   weight 0.40
  - Humidity (%)          weight 0.25
  - Wind speed (m/s)      weight 0.20
  - Cloudiness (%)        weight 0.15

Design reasoning (goes in your README too):
  Each raw parameter is first converted into its own 0-100 "sub-score" using
  a shape that matches how humans actually experience that variable, THEN
  the sub-scores are combined with weights. This two-step approach (score
  each dimension independently, then weight) is easier to reason about and
  tune than one big formula, and it's easy to extend: adding a 5th
  parameter (e.g. pressure) just means writing one more `_score_x()`
  function and adjusting the weights to sum to 1.0 - exactly what Part 3 of
  the assignment asks you to do live.

  - Temperature: comfort peaks around 22 deg C and falls off the further you
    get from it in either direction (too cold or too hot both feel bad).
    Modeled as an inverted parabola clipped to [0, 100].
  - Humidity: comfort peaks around 45% relative humidity; very dry and very
    humid air both feel unpleasant. Same inverted-parabola shape, wider.
  - Wind: mild breeze is pleasant, strong wind is not. Comfort is high at
    low wind speed and decays linearly past a threshold.
  - Cloudiness: mostly a preference call - we treat partial cloud cover as
    neutral-to-pleasant (softens harsh sun) and full overcast as a mild
    negative. Linear penalty above 50% cover.

  Weights were chosen because temperature dominates how "comfortable"
  outdoor conditions feel, humidity is the second biggest driver of
  perceived comfort (it changes how temperature *feels*), and wind/cloud
  are secondary modifiers. These are opinions, not physics - be ready to
  say why you'd change them.
"""
from dataclasses import dataclass


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _score_temperature(temp_c: float) -> float:
    ideal = 22.0
    spread = 12.0  # degrees away from ideal before score hits ~0
    score = 100 - ((temp_c - ideal) ** 2) * (100 / (spread ** 2))
    return _clamp(score)


def _score_humidity(humidity_pct: float) -> float:
    ideal = 45.0
    spread = 45.0
    score = 100 - ((humidity_pct - ideal) ** 2) * (100 / (spread ** 2))
    return _clamp(score)


def _score_wind(wind_speed_ms: float) -> float:
    comfortable_up_to = 3.0   # m/s, ~light breeze
    zero_at = 15.0            # m/s, ~strong wind -> score bottoms out
    if wind_speed_ms <= comfortable_up_to:
        return 100.0
    score = 100 - (wind_speed_ms - comfortable_up_to) * (
        100 / (zero_at - comfortable_up_to)
    )
    return _clamp(score)


def _score_cloudiness(cloud_pct: float) -> float:
    neutral_up_to = 50.0  # up to 50% cloud cover treated as fine
    if cloud_pct <= neutral_up_to:
        return 100.0
    score = 100 - (cloud_pct - neutral_up_to) * (100 / (100 - neutral_up_to))
    return _clamp(score)


WEIGHTS = {
    "temperature": 0.40,
    "humidity": 0.25,
    "wind": 0.20,
    "cloudiness": 0.15,
}


@dataclass
class ComfortBreakdown:
    temperature_score: float
    humidity_score: float
    wind_score: float
    cloudiness_score: float
    final_score: float


def compute_comfort_index(
    temp_c: float, humidity_pct: float, wind_speed_ms: float, cloud_pct: float
) -> ComfortBreakdown:
    t = _score_temperature(temp_c)
    h = _score_humidity(humidity_pct)
    w = _score_wind(wind_speed_ms)
    c = _score_cloudiness(cloud_pct)

    final = (
        t * WEIGHTS["temperature"]
        + h * WEIGHTS["humidity"]
        + w * WEIGHTS["wind"]
        + c * WEIGHTS["cloudiness"]
    )

    return ComfortBreakdown(
        temperature_score=round(t, 1),
        humidity_score=round(h, 1),
        wind_score=round(w, 1),
        cloudiness_score=round(c, 1),
        final_score=round(_clamp(final), 1),
    )
