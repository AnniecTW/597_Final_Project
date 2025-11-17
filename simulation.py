"""

"""

import numpy as np
from surfer import *
from config import *

def generate_wave_set(spot_level):
    """

    :param spot_level:
    :return:
    """
    lambda_set = SPOT_CONF[spot_level]['lambda_set']
    num = np.random.poisson(lambda_set)
    waves = []

    for _ in range(num):
        waves.append('something')
    return waves

def handle_wave(wave):
    pass


def main():

    t = 0
    collision_events = 0
    while t < SESSION_DURATION:

        # time interval between wave sets
        delta_t = np.random.gamma(WAVESET_ARRIVAL['shape'], WAVESET_ARRIVAL['scale'])
        waves = generate_wave_set(SPOT_LEVEL)  # a wave set for each session

        for wave in waves:
            handle_wave(wave)  # collision, update...
        t += delta_t
        pass

if __name__ == '__main__':
    main()

