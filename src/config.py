"""
Stores all parameter settings for the surfing simulation.
"""

# ==========================================
# 1. USER CONTROL (Simulation Run Settings)
# ==========================================

SESSION_DURATION = 3600      # Simulation time in seconds
SPOT_LEVEL = "beginner"      # "beginner", "mixed", "advanced"
RULE_TYPE = "free_for_all"   # "free_for_all", "safe_distance"

EXPR_CONF = {
    "mode": "realistic",      # "realistic" or "experiment"

    # Experiment Mode Settings (ignored in realistic mode)
    "num_surfer_fixed": 80,
    "beginner_ratios": [0.0, 0.2, 0.4, 0.6, 0.8],
    "beginner_params": (0.0, 0.3),  # Skill range for beginners
    "advanced_params": (0.7, 1.0),  # Skill range for advanced
}


# ==========================================
# 2. ENVIRONMENT & PHYSICS (Map Dimensions)
# ==========================================
# Physical boundaries and locations in the simulation (Meters)

# Ocean Boundaries
OCEAN_Y_MIN = -50
OCEAN_Y_MAX = 50
OCEAN_X_MAX = 150

# Lineup Locations (X-coordinates)
LINEUP_X_NEAR_SHORE = 10
LINEUP_X_OUTSIDE = 90

# Best Position (BP) Range
BP_X_MIN = 30
BP_X_MAX = 80


# ==========================================
# 3. SURFER BEHAVIOR & LOGIC
# ==========================================

# Distance Thresholds (Meters)
SUCCESS_DISTANCE = 10      # Distance required to count as a successful ride
SAFE_DISTANCE = 10         # Radius for safe_distance rule
PADDLE_THRESHOLD = 5       # Distance to BP to stop paddling and start waiting
CATCH_WAVE_THRESHOLD = 2   # Max distance to wave peak to attempt catching

# Probability Model Parameters
ATTEMPT_RATE_MIN = 0.1
ATTEMPT_RATE_MAX = 0.9
ALPHA_SUCCESS = 1.0        # Impact of wave height on success probability (0 to 1)

# Normalization bounds for probability calculations
NORMALIZATION = {
    "wave_height": {
        "min": 0.5,
        "max": 3.0,
    }
}


# ==========================================
# 4. STATISTICAL CONFIGURATIONS (Data)
# ==========================================
# Detailed statistical parameters for different spot levels.

WAVESET_ARRIVAL = {
    "shape": 2,
    "scale": 3,
}

SPOT_CONF = {
    "beginner": {
        "wave_height": {"min": 0.3, "max": 1.2, "mu": -0.5, "sigma": 0.4}, # Lognormal
        "skill":       {"alpha": 2.0, "beta": 8.0},                        # Beta dist
        "lambda_set":  3.5,                                                # Poisson rate
        "num_surfer":  {"mean": 70, "std": 20},
        "wave_speed":  {"min": 2.0, "max": 4.0}
    },
    "mixed": {
        "wave_height": {"min": 0.8, "max": 2.0, "mu": 0.25, "sigma": 0.35},
        "skill":       {"alpha": 5.0, "beta": 5.0},
        "lambda_set":  4.5,
        "num_surfer":  {"mean": 40, "std": 30},
        "wave_speed":  {"min": 3.5, "max": 5.5}
    },
    "advanced": {
        "wave_height": {"min": 1.0, "max": 3.5, "mu": 0.7, "sigma": 0.4},
        "skill":       {"alpha": 8.0, "beta": 2.0},
        "lambda_set":  5.5,
        "num_surfer":  {"mean": 30, "std": 10},
        "wave_speed":  {"min": 4.5, "max": 7.5}
    },
}