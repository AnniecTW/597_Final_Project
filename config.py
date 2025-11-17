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
        "lambda_set": 2.5
    },
    "mixed": {
        "wave_height": {
            "min": 0.5,
            "max": 3.0,
            "mu": 0.8,
            "sigma": 0.35,
        },
        "skill": {
            "alpha": 5.0,
            "beta": 5.0,
        },
        "lambda_set": 3.5
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
        "lambda_set": 4.5
    },
}

# Behavioral parameters
ALPHA_SUCCESS = 0.5          # impact of wave height on success

# Wave set arrival parameters
WAVESET_ARRIVAL = {
    "shape": 2,
    "scale": 30,
}

# Simulation Setup
N_SURFERS = 30
SESSION_DURATION = 3600      # seconds

# Scenario settings
SPOT_LEVEL = "beginner"      # beginner / mixed / advanced
RULE_TYPE = "free_for_all"   # free_for_all / first_in_line
BOARD_TYPE = "longboard"     # shortboard / longboard


