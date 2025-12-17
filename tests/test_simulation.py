import pandas as pd
import pytest
from src.simulation import compute_stats, run_simulation , run_many

# test function compute_stats()
@pytest.fixture(scope="module")
def mock_surfer_class():
    class MockSurfer:
        def __init__(self, success, collisions, wait_sum):
            self.stats = {"success": success, "collisions": collisions}
            self.waiting_time_sum = wait_sum
    return MockSurfer

def test_compute_stats_normal(mock_surfer_class):
    s1 = mock_surfer_class(5, 3, 100)
    s2 = mock_surfer_class(1, 2, 200)

    res = compute_stats([s1, s2], [1, 2, 3], "beginner", 0.5)

    assert res["avg_success_count"] == 3.0
    assert res["avg_collision_count"] == 2.5
    assert res["avg_waiting_time"] == 50.0
    assert res["fairness"] == pytest.approx(0.3333333333333333)

def test_compute_stats_failed(mock_surfer_class):
    s1 = mock_surfer_class(0, 0, 0)
    res = compute_stats([s1], [1], "advanced", 0.5)

    assert res["avg_success_count"] == 0.0
    assert res["avg_collision_count"] == 0.0
    assert res["avg_waiting_time"] > 0

# test function run_simulation()
@pytest.fixture
def wave_schedule():
    return [
        {'spawn_time': 0, 'height': 1.0, 'speed': 2, 'spawned': False},
        {'spawn_time': 5, 'height': 2.0, 'speed': 4, 'spawned': False}
    ]

def test_simulation(wave_schedule):
    stats = run_simulation(mode="realistic", wave_schedule=wave_schedule, duration=100, num_surfer=200)

    assert stats["avg_success_count"] >= 0
    assert stats["avg_collision_count"] >= 0
    assert stats["avg_waiting_time"] > 0
    assert stats["wave_counts"] == 2

def test_simulation_safe_distance():
    stats = run_simulation(mode="realistic", rule_type="safe_distance", duration=100, num_surfer=5)

    assert stats["avg_success_count"] >= 0
    assert stats["avg_collision_count"] >= 0
    assert stats["avg_waiting_time"] > 0

def test_simulation_validation():
    with pytest.raises(ValueError, match="ratio is not supported for realistic mode"):
        run_simulation(mode="realistic", ratio=0.5)

# test function run_many()
def test_run_many():
    n_runs = 2

    results, means, stds = run_many(number_of_runs=n_runs, mode="realistic", duration=100, num_surfer=1)

    assert len(results) == n_runs
    assert isinstance(means, pd.Series)
    assert isinstance(stds, pd.Series)

    expected_cols = ["n_surfers", "wave_counts", "avg_success_count", "avg_collision_count", "avg_waiting_time", "fairness"]

    for col in expected_cols:
        assert col in means.index
        assert col in stds.index