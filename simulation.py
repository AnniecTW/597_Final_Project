"""
Simulation Framework
"""

import numpy as np
from surfer import *
from wave import *


def simulate_waves(duration, spot_conf):
    """

    :param duration:
    :param spot_conf:
    :return:
    >>> from config import SPOT_CONF
    >>> simulate_waves(0.0, SPOT_CONF["beginner"])
    []
    >>> simulate_waves(1000, {}) # edge case
    []
    >>> w = simulate_waves(1000, SPOT_CONF["beginner"])
    >>> len(w) > 0
    True
    >>> w # doctest: +ELLIPSIS
    [..., {'spawn_time': ..., 'height': ..., 'speed': ..., 'spawned': ...}, ...]
    >>> waves = simulate_waves(1000, SPOT_CONF["mixed"])
    >>> all([0 <= w['spawn_time'] <= 1000 for w in waves])
    True
    >>> waves = simulate_waves(1000, SPOT_CONF["advanced"])
    >>> h_min = SPOT_CONF["advanced"]["wave_height"]["min"]
    >>> h_max = SPOT_CONF["advanced"]["wave_height"]["max"]
    >>> all([h_min <= w['height'] <= h_max for w in waves])
    True
    """
    if not spot_conf:
        return []

    wave_schedule = []
    t = 0
    lambda_wavecount = spot_conf['lambda_set']

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
            wave_height_settings = spot_conf['wave_height']
            h_max = wave_height_settings['max']
            h_min = wave_height_settings['min']
            h_avg = wave_height_settings['mu']
            h_sigma = wave_height_settings['sigma']
            h = np.random.lognormal(h_avg, h_sigma)
            height = min(max(h, h_min), h_max)

            # handle wave speed
            s_min = spot_conf['wave_speed']['min']
            s_max = spot_conf['wave_speed']['max']
            speed = np.random.uniform(s_min, s_max)

            wave_schedule.append({'spawn_time': spawn_time, 'height': height, 'speed': speed, 'spawned': False})
    return wave_schedule

# AI idea check - 4
def gini(x):
    """

    :param x:
    :return:
    >>> gini([])
    0.0
    >>> gini([1])
    0.0
    >>> g = gini([1, 2, 3, 4, 5])
    >>> 0 <= g <= 1
    True
    >>> gini(20) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: x must be list
    """
    if not isinstance(x, list):
        raise TypeError("x must be list")

    x = np.array(x, dtype=np.float64)

    if np.all(x == 0):
        return 0.0

    if np.any(x < 0):
        x -= np.min(x)

    mean_x = x.mean()

    # pairwise absolute differences
    diff_sum = np.abs(x[:, None] - x[None, :]).sum()
    n = len(x)

    return float(diff_sum / (2 * n ** 2 * mean_x))

# AI idea organization - 1
def prep_surfer_config(spot_level, mode, ratio, num_surfer):
    """

    :param spot_level:
    :param mode:
    :param ratio:
    :param num_surfer:
    :return:
    >>> from config import SPOT_CONF
    >>> s_config = prep_surfer_config("beginner", "realistic", None, None)
    >>> s_config # doctest: +ELLIPSIS
    {'skills': array(...), 'num_surfer': ..., 'mode': 'realistic'}
    >>> # range check
    >>> 10 <= s_config['num_surfer'] <= 150
    True
    >>> all(0 <= s <= 1 for s in s_config['skills'])
    True
    >>> sur_config = prep_surfer_config("mixed", "experiment", 1, 40)
    >>> sur_config # doctest: +ELLIPSIS
    {'skills': array(...), 'num_surfer': 40, 'mode': 'experiment', 'beginner_ratio': 1}
    >>> all(0 <= sur <= 1 for sur in sur_config['skills'])
    True
    """

    config = {}

    if mode == "realistic":
        # decide number of surfers
        mean = SPOT_CONF[spot_level]["num_surfer"]["mean"]
        std = SPOT_CONF[spot_level]["num_surfer"]["std"]
        if num_surfer is None:
            num_surfer = max(10, min(int(np.random.normal(mean, std)), 150))

        # decide skill distribution
        alpha = SPOT_CONF[spot_level]["skill"]["alpha"]
        beta = SPOT_CONF[spot_level]["skill"]["beta"]
        skills = np.random.beta(alpha, beta, size=num_surfer)

        config["skills"] = skills
        config["num_surfer"] = num_surfer
        config["mode"] = "realistic"

    elif mode == "experiment":

        if num_surfer is None:
            num_surfer = EXPR_CONF["num_surfer_fixed"]
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

def compute_stats(surfers, wave_schedule, spot_level, ratio, seed):
    """

    :param surfers:
    :param wave_schedule:
    :param spot_level:
    :param ratio:
    :param seed:
    :return:

    """
    success_wave_counts = [s.stats['success'] for s in surfers]  # success wave count for each person
    fairness = gini(success_wave_counts)

    total_collision = sum(s.stats['collisions'] for s in surfers)
    total_success = sum(s.stats['success'] for s in surfers)
    wait_sum = np.array([s.waiting_time_sum for s in surfers])
    success_counts = np.array([max(1, s.stats['success']) for s in surfers])
    avg_wait_per_wave = wait_sum.sum() / success_counts.sum() if success_counts.sum() else 0

    return {
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

# AI logic organization -1
def run_simulation(
        spot_level=SPOT_LEVEL,
        rule_type=RULE_TYPE,
        num_surfer=None,
        ratio=None,
        spot_conf=None,
        wave_schedule=None,
        mode=EXPR_CONF["mode"],
        duration=SESSION_DURATION,
        seed=None,
):

    # Random seed
    if seed is not None:
        np.random.seed(seed)

    # Reset global trackers
    Wave.all_waves = []
    Surfer.all_surfers = []

    # Prepare spot config:
    if spot_conf is None:
        spot_conf = SPOT_CONF[spot_level]

    # Prepare surfers
    if mode == "realistic":
        if ratio is not None:
            raise ValueError("ratio is not supported for realistic mode")

        surfer_config = prep_surfer_config(spot_level, mode, ratio, num_surfer)

    elif mode == "experiment":
        if ratio is None:
            raise ValueError("experiment mode requires ratio (beginner_ratio)")

        surfer_config = prep_surfer_config(spot_level, mode, ratio, num_surfer)

    # Create surfers
    surfers = [Surfer(skill=s) for s in surfer_config["skills"]]

    # Generate wave schedule (if not provided)
    if wave_schedule is None:
        wave_schedule = simulate_waves(duration, spot_conf)

    # Run simulation per second
    for t in range(duration):

        # spawn new waves
        for w in wave_schedule:
            if (not w['spawned']) and w['spawn_time'] <= t:
                Wave(w['height'], w['speed'])
                w['spawned'] = True

        # update waves
        Wave.update_all()

        # update surfers
        Surfer.update_all(rule_type, Wave.all_waves, t)

    # Compute statistics
    stats = compute_stats(surfers, wave_schedule, spot_level, ratio, seed)

    return stats

def main():
    waves, surfers, stats = run_simulation()
    print(f"Mode: {EXPR_CONF['mode']}")
    print(f"Rule type: {RULE_TYPE}")
    print(stats)


if __name__ == '__main__':
    main()

