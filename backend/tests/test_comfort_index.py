from app.comfort_index import compute_comfort_index


def test_ideal_conditions_score_near_100():
    result = compute_comfort_index(
        temp_c=22, humidity_pct=45, wind_speed_ms=1, cloud_pct=0
    )
    assert result.final_score > 95


def test_extreme_heat_scores_low():
    result = compute_comfort_index(
        temp_c=45, humidity_pct=90, wind_speed_ms=1, cloud_pct=0
    )
    assert result.final_score < 40


def test_extreme_cold_scores_low():
    # Temperature is only 40% of the weight, so even a temperature
    # sub-score of 0 still leaves up to 60 points from the other three
    # (perfect) parameters. This test checks the temperature sub-score
    # directly, plus that the final score is meaningfully worse than ideal.
    result = compute_comfort_index(
        temp_c=-10, humidity_pct=45, wind_speed_ms=1, cloud_pct=0
    )
    assert result.temperature_score == 0
    assert result.final_score < 65  # far below the ~98 ideal-conditions score


def test_score_is_always_within_bounds():
    for temp in [-40, 0, 22, 60]:
        for humidity in [0, 45, 100]:
            for wind in [0, 5, 40]:
                for cloud in [0, 50, 100]:
                    result = compute_comfort_index(temp, humidity, wind, cloud)
                    assert 0 <= result.final_score <= 100


def test_high_wind_penalizes_score():
    calm = compute_comfort_index(22, 45, 1, 0)
    windy = compute_comfort_index(22, 45, 20, 0)
    assert windy.final_score < calm.final_score


def test_overcast_penalizes_score():
    clear = compute_comfort_index(22, 45, 1, 10)
    overcast = compute_comfort_index(22, 45, 1, 100)
    assert overcast.final_score < clear.final_score
