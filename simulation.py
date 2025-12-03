"""
Simulation Framework
"""

import numpy as np
from surfer import *
from wave import *


def simulate_waves(duration):
    wave_schedule = []
    t = 0
    lambda_wavecount = SPOT_CONF[SPOT_LEVEL]['lambda_set']

    while t < duration:
        # next wave set generation time
        delta_t = np.random.gamma(WAVESET_ARRIVAL['shape'], WAVESET_ARRIVAL['scale'])
        t += delta_t
        if t > duration:
            break

        # wave count in a set
        num_waves = np.random.poisson(lambda_wavecount)

        # generate waves in a set
        for i in range(num_waves):
            offset = np.random.uniform(3, 8)

            spawn_time = t + offset
            if spawn_time >= duration:
                break

            # handle wave height
            wave_height_settings = SPOT_CONF[SPOT_LEVEL]['wave_height']
            h_max = wave_height_settings['max']
            h_min = wave_height_settings['min']
            h_avg = wave_height_settings['mu']
            h_sigma = wave_height_settings['sigma']
            h = np.random.lognormal(h_avg, h_sigma)
            height = min(max(h, h_min), h_max)

            # handle wave speed
            s_min = SPOT_CONF[SPOT_LEVEL]['wave_speed']['min']
            s_max = SPOT_CONF[SPOT_LEVEL]['wave_speed']['max']
            speed = np.random.uniform(s_min, s_max)

            wave_schedule.append({'spawn_time': spawn_time, 'height': height, 'speed': speed, 'spawned': False})
    return wave_schedule

# AI idea check - 4
def gini(x):
    x = np.array(x, dtype=np.float64)

    if np.all(x == 0):
        return 0.0

    if np.any(x < 0):
        x -= np.min(x)

    mean_x = x.mean()

    # pairwise absolute differences
    diff_sum = np.abs(x[:, None] - x[None, :]).sum()
    n = len(x)

    return diff_sum / (2 * n ** 2 * mean_x)

# AI idea organization - 1
def prep_surfer_config(spot_level, mode, num_surfer, ratio=None):
    config = {}

    if mode == "realistic":
        # decide number of surfers
        mean = SPOT_CONF[spot_level]["num_surfer"]["mean"]
        std = SPOT_CONF[spot_level]["num_surfer"]["std"]
        num_surfer = max(1, int(np.random.normal(mean, std)))

        # decide skill distribution
        alpha = SPOT_CONF[spot_level]["skill"]["alpha"]
        beta = SPOT_CONF[spot_level]["skill"]["beta"]
        skills = np.random.beta(alpha, beta, size=num_surfer)

        config["skills"] = skills
        config["num_surfer"] = num_surfer
        config["mode"] = "realistic"

    elif mode == "experiment":

        # number of beginners and skilled surfers
        n_beginner = int(round(num_surfer * ratio))
        n_advanced = num_surfer - n_beginner

        # skill distribution
        b_low, b_high = EXPR_CONF["beginner_params"]
        beginner = np.random.uniform(b_low, b_high, size=n_beginner)

        a_low, a_high = EXPR_CONF["advanced_params"]
        advanced = np.random.uniform(a_low, a_high, size=n_advanced)

        # merge and shuffle
        skills = np.concatenate((beginner, advanced))
        np.random.shuffle(skills)

        config["skills"] = skills
        config["num_surfer"] = num_surfer
        config["mode"] = "experiment"
        config["beginner_ratio"] = ratio

    return config

def run_simulation(wave_schedule=None, mode=EXPR_CONF["mode"], spot_level=SPOT_LEVEL, num_surfer=EXPR_CONF["num_surfer_fixed"], rule_type=RULE_TYPE, ratio=None, duration=SESSION_DURATION, seed=None):
    if seed is not None:
        np.random.seed(seed)

    if mode == "realistic":
        if ratio is not None:
            raise ValueError("ratio is not supported for realistic mode")
        surfer_config = prep_surfer_config(spot_level, mode, num_surfer)
    elif mode == "experiment":
        if ratio is None:
            raise ValueError("experiment mode requires ratio (beginner_ratio)")
        surfer_config = prep_surfer_config(spot_level, mode, num_surfer, ratio)

    Wave.all_waves = []
    Surfer.all_surfers = []

    skills = surfer_config["skills"]
    surfers = [Surfer(skill=s) for s in skills]

    # initialize wave schedule
    if wave_schedule is None:
        wave_schedule = simulate_waves(duration)

    for t in range(duration): # per second

        # each second, update arriving waves and check if the session has ended
        for w in wave_schedule:
            if (not w['spawned']) and w['spawn_time'] <= t:
                Wave(w['height'], w['speed'])
                w['spawned'] = True

        # update each wave's position and existence
        Wave.update_all()

        # update each surfer's position and state
        for surfer in surfers:
            surfer.update_state_and_position(rule_type, Wave.all_waves, t)


    # calculate statistics
    success_wave_counts = [s.stats['success'] for s in surfers] # success wave count for each person
    fairness = gini(success_wave_counts)

    total_collision = sum(s.stats['collisions'] for s in surfers)
    total_success = sum(s.stats['success'] for s in surfers)
    wait_sum = np.array([s.waiting_time_sum for s in surfers])
    success_counts = np.array([max(1, s.stats['success']) for s in surfers])
    avg_wait_per_wave = wait_sum.sum() / success_counts.sum() if success_counts.sum() else 0

    session_stats = {
        "spot_level": spot_level,
        "n_surfers": len(surfers),
        "beginner_ratio": ratio,
        'wave_counts': len(wave_schedule),
        'success_rate': total_success / len(surfers) if len(surfers) else 0.0,
        'collision_rate': total_collision / len(surfers) if len(surfers) else 0.0,
        'avg_waiting_time': float(avg_wait_per_wave),
        'fairness': float(fairness),
        "seed": seed,
    }

    return session_stats

def main():
    waves, surfers, stats = run_simulation(seed=40)
    print(f"Mode: {EXPR_CONF['mode']}")
    print(f"Rule type: {RULE_TYPE}")
    print(stats)


if __name__ == '__main__':
    main()

