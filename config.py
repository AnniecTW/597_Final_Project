"""
Stores all parameter settings for the surfing simulation.

This file keeps all scenario parameters, including:
- number of surfers (N)
- skill and wave distributions
- session duration
- rule type and spot level
- parameters used by behavioral models (e.g., alpha for success)

These values are imported by the simulation code to run different experimental conditions.
"""

# AI idea check - 1
# Distribution parameters for wave height (lognormal) and skill (beta)
SPOT_CONF = {
    "beginner": {
        "wave_height": {
            "min": 0.3,
            "max": 1.5,
            "mu": 0.2,
            "sigma": 0.25,
        },
        "skill": {
            "alpha": 2.0,
            "beta": 8.0,
        },
        "lambda_set": 3.5,
        "num_surfer": {
            "mean": 70,
            "std": 20
        },
        "wave_speed": {
            "min": 2.2,
            "max": 4.5,
        }
    },
    "mixed": {
        "wave_height": {
            "min": 0.5,
            "max": 3.5,
            "mu": 0.8,
            "sigma": 0.35,
        },
        "skill": {
            "alpha": 5.0,
            "beta": 5.0,
        },
        "lambda_set": 4.5,
        "num_surfer": {
            "mean": 40,
            "std": 30
        },
        "wave_speed": {
            "min": 4.5,
            "max": 6.7,
        }
    },
    "advanced": {
        "wave_height": {
            "min": 0.8,
            "max": 5.5,
            "mu": 1.2,
            "sigma": 0.4,
        },
        "skill": {
            "alpha": 8.0,
            "beta": 2.0,
        },
        "lambda_set": 5.5,
        "num_surfer": {
            "mean": 30,
            "std": 10
        },
        "wave_speed": {
            "min": 6.7,
            "max": 8.9,
        }
    },
}

# Wave set arrival parameters
WAVESET_ARRIVAL = {
    "shape": 2,
    "scale": 3,
}

# Simulation Setup
SESSION_DURATION = 3600      # seconds
NORMALIZATION = {
    "wave_height": {
        "min": 0.5,
        "max": 3.0,
    }
}

# AI idea check - 2
EXPR_CONF = {
    "mode": "realistic",      # or "controlled"

    # Only used in controlled mode
    "num_surfer_fixed": 80,
    "beginner_ratios": [0.0, 0.2, 0.4, 0.6, 0.8],
    "beginner_params": (0.0, 0.3),
    "advanced_params": (0.7, 1.0),
}

# Scenario settings
SPOT_LEVEL = "mixed"      # beginner / mixed / advanced
RULE_TYPE = "free_for_all"   # free_for_all / first_in_line
BOARD_TYPE = "longboard"     # shortboard / longboard

# Surfer settings
LINEUP_X_NEAR_SHORE = 10
LINEUP_X_OUTSIDE = 90
ATTEMPT_RATE_MIN = 0.1
ATTEMPT_RATE_MAX = 0.9
OCEAN_Y_MIN = -50
OCEAN_Y_MAX = 50
OCEAN_X_MAX = 150
BP_X_MIN = 30
BP_X_MAX = 80
ALPHA_SUCCESS = 1          # impact of wave height on success
SUCCESS_DISTANCE = 10
