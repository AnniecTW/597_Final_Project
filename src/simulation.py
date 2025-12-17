import pandas as pd
from src.surfer import *
from src.wave import *

# AI idea check - 3
def gini(x):
    """
    Computes the Gini index to quantify the inequality of wave distribution among surfers.

    :param x: a list containing the success counts of each surfer
    :return: float, the computed Gini index (0.0 = perfect equality, 1.0 = max inequality)
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

def simulate_waves(duration, spot_conf):
    """
    Generate a schedule of waves for the simulation session based on spot configuration.

    :param duration: the total duration of simulation (sec)
    :param spot_conf: dictionary containing spot configuration
    :return: a list of wave dictionaries containing spawn time, height, speed, and status
    >>> from src.config import SPOT_CONF
    >>> simulate_waves(0.0, SPOT_CONF["beginner"])
    []
    >>> simulate_waves(1000, {})
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
            session_base_speed = np.random.uniform(s_min, s_max)

            wave_schedule.append({'spawn_time': spawn_time, 'height': height, 'speed': session_base_speed, 'spawned': False})
    return wave_schedule

# AI idea organization - 1
def prep_surfer_config(spot_level, mode, ratio, num_surfer):
    """
    Prepare the surfer configuration dictionary, including skill levels and counts.

    :param spot_level: the difficulty level of the spot
    :param mode: simulation mode ('realistic', 'experiment')
    :param ratio: ratio of beginner surfers
    :param num_surfer: the total number of surfers
    :return: a dictionary containing initialized surfer configuration
    >>> from src.config import SPOT_CONF
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

def compute_stats(surfers: list, wave_schedule: list, spot_level: str, ratio: float) -> dict:
    """
    Computes statistics for the simulation.

    :param surfers: a list of surfer statistics
    :param wave_schedule: a list of wave configurations
    :param spot_level: the difficulty level of the spot
    :param ratio: ratio of beginner surfers
    :return: dictionary of stats
    >>> compute_stats([], [], "mixed", 0.0)
    {'spot_level': 'mixed', 'n_surfers': 0, 'beginner_ratio': 0.0, 'wave_counts': 0, 'avg_success_count': 0.0, 'avg_collision_count': 0.0, 'avg_waiting_time': 0.0, 'fairness': 0.0}
    """
    success_wave_counts = [s.stats['success'] for s in surfers]  # success wave count for each person
    fairness = gini(success_wave_counts)
    total_collision = sum(s.stats['collisions'] for s in surfers)
    total_success = sum(s.stats['success'] for s in surfers)
    wait_sum = np.array([s.waiting_time_sum if s.waiting_time_sum > 0 else SESSION_DURATION for s in surfers ])

    if total_success > 0:
        avg_wait_time = wait_sum.sum() / total_success
    elif len(surfers) == 0:
        avg_wait_time = 0.0
    else:
        avg_wait_time = SESSION_DURATION

    return {
        "spot_level": spot_level,
        "n_surfers": len(surfers),
        "beginner_ratio": ratio,
        'wave_counts': len(wave_schedule),
        'avg_success_count': total_success / len(surfers) if len(surfers) else 0.0,
        'avg_collision_count': total_collision / len(surfers) if len(surfers) else 0.0,
        'avg_waiting_time': float(avg_wait_time),
        'fairness': float(fairness),
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
):
    """
    Runs a single simulation session.

    :param spot_level: the difficulty level of the spot
    :param rule_type: the rule set surfers follow ('free_for_all' or 'safe_distance')
    :param num_surfer: total number of surfers
    :param ratio: ratio of beginner surfers
    :param spot_conf: custom spot configuration dictionary
    :param wave_schedule: a list of wave configurations
    :param mode: simulation mode ('realistic', 'experiment')
    :param duration: duration of the simulation in seconds
    :return: a dictionary containing simulation statistics
    >>> res = run_simulation(wave_schedule=[])
    >>> [res["avg_success_count"], res["avg_collision_count"], res["fairness"]]
    [0.0, 0.0, 0.0]
    >>> res["avg_waiting_time"] == SESSION_DURATION
    True
    >>> res = run_simulation(mode="experiment", ratio=0.5)
    >>> res['beginner_ratio'] == 0.5
    True
    >>> run_simulation(mode="experiment")
    Traceback (most recent call last):
        ...
    ValueError: experiment mode requires ratio (beginner_ratio)
    """

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
    stats = compute_stats(surfers, wave_schedule, spot_level, ratio)

    return stats

def run_many(
        number_of_runs=100,
        mode=None,
        spot_level=None,
        rule_type=None,
        num_surfer=None,
        ratio=None,
        spot_conf=None,
        wave_schedule=None,
        duration=None,
):
    """
    Run multiple Monte Carlo simulations to gather statistical distributions.
    :param number_of_runs: number of simulations to run
    """
    if mode is None: mode=EXPR_CONF["mode"]
    if spot_level is None: spot_level=SPOT_LEVEL
    if rule_type is None: rule_type=RULE_TYPE
    if spot_conf is None: spot_conf=SPOT_CONF[spot_level]
    if duration is None: duration=SESSION_DURATION

    results = []

    print(f" Running {number_of_runs} Monte Carlo iterations...")

    for _ in range(number_of_runs):
        res = run_simulation(
            mode=mode,
            spot_level=spot_level,
            rule_type=rule_type,
            num_surfer=num_surfer,
            ratio=ratio if mode == "experiment" else None,
            spot_conf=spot_conf,
            wave_schedule=wave_schedule,
            duration=duration,
        )

        res_metrics = {
            "n_surfers": res["n_surfers"],
            "wave_counts": res["wave_counts"],
            "avg_success_count": res["avg_success_count"],
            "avg_collision_count": res["avg_collision_count"],
            "avg_waiting_time": res["avg_waiting_time"],
            "fairness": res["fairness"]
        }
        results.append(res_metrics)

    df = pd.DataFrame(results)
    return results, df.mean(), df.std()