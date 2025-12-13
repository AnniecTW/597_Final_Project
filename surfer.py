from config import *
import numpy as np
from collections import Counter

class Surfer:
    """

    """

    PADDLE_SPEED_SKILL_COEFF = 0.1
    PADDLE_SPEED_BASE = 0.8

    all_surfers = [] # automatically track all surfers

    def __init__(self, skill, board_type="longboard", distance_on_wave=0.0 ):
        self.skill = skill

        # initial position
        self.y = np.random.uniform(OCEAN_Y_MIN, OCEAN_Y_MAX)
        self.x = self.initial_x()

        # paddling speed
        self.speed = self.PADDLE_SPEED_BASE + skill * self.PADDLE_SPEED_SKILL_COEFF

        # best x position (bp)
        self.bp = BP_X_MIN + self.skill * (BP_X_MAX - BP_X_MIN)

        # waiting / paddling
        self.state = self.initial_state()  # AI idea check - 3

        self.board_type = board_type

        self.stats = Counter()
        self.curr_riding_wave = None
        self.distance_on_wave = distance_on_wave
        self.ride_already_counted = False
        self.last_catch_time = None
        self.waiting_time_sum = 0

        Surfer.all_surfers.append(self)

    def initial_x(self):
        loc = np.interp(self.skill, [0, 1], [LINEUP_X_NEAR_SHORE, LINEUP_X_OUTSIDE])
        return max(0, np.random.normal(loc=loc, scale=5))

    def initial_state(self):
        if abs(self.x - self.bp) <= 10:
            return 'waiting'
        else:
            return 'paddling'

    def check_collisions(self, threshold=3):
        for other in Surfer.all_surfers:
            if other is self:
                continue

            # case 1: both floaters -> skip
            if self.curr_riding_wave is None and other.curr_riding_wave is None:
                continue

            # case 2: both riding but on different waves -> skip
            if self.curr_riding_wave is not None and other.curr_riding_wave is not None:
                if self.curr_riding_wave != other.curr_riding_wave:
                    continue

            # other situations:
            #  - both riding same wave
            #  - rider vs floater
            dx = self.x - other.x
            dy = self.y - other.y

            if dx ** 2 + dy ** 2 < threshold ** 2:
                return True
        return False

    def prob_attempt(self, wave_height):
        """
        Returns the probability that a surfer attempts the wave.

        Idea:
        - High waves → skilled surfers attempt more, beginners attempt less.
        - Low waves → beginners attempt more, skilled surfers still have some interest.

        Model:
        1. Normalize wave height to [0, 1].
        2. Compute "comfort" = how well the wave height matched the surfer's skill
        3. Map comfort to probability between 0.1 and 0.9

        :param wave_height:
        :return:
        """
        h_min = NORMALIZATION["wave_height"]["min"]
        h_max = NORMALIZATION["wave_height"]["max"]

        # Normalize wave height to [0, 1] to match skill scale
        h = max(0, (wave_height - h_min) / (h_max - h_min))

        # Compute comfort representing the similarity between skill and wave height
        comfort = max(0, 1 - abs(h - self.skill))

        # higher skill, often higher attempt rate
        baseline_interest = 0.2 * self.skill

        factor = 0.7 * comfort + 0.3 * baseline_interest  # AI idea check - 4

        # Map comfort to attempt rate between 0.1 and 0.9
        attempt_rate = ATTEMPT_RATE_MIN + (ATTEMPT_RATE_MAX - ATTEMPT_RATE_MIN) * factor
        return min(1, max(0, attempt_rate))

    def prob_success(self, wave_height):
        """
        Returns the probability that a surfer successfully catch a wave and pop up.

        Idea:
        Higher waves reduce success rates, but skilled surfers are less sensitive to wave height.

        :param wave_height:
        :return:
        """
        h_min = NORMALIZATION["wave_height"]["min"]
        h_max = NORMALIZATION["wave_height"]["max"]

        # Convert wave height to [0, 1] to measure its impact on a surfer
        h = (wave_height - h_min) / (h_max - h_min)
        h = min(max(0, h), 1)

        skill_factor = 1 - self.skill # higher skill, lower sensitivity to wave height

        return min(1, max(0, self.skill * (1 - ALPHA_SUCCESS * h * skill_factor)))  # AI idea check - 4

    def prob_wipeout(self, wave_height):

        h_min = NORMALIZATION["wave_height"]["min"]
        h_max = NORMALIZATION["wave_height"]["max"]

        # Normalize wave height to [0, 1]
        h = (wave_height - h_min) / (h_max - h_min)
        h = min(max(0, h), 1)

        base = 0.05 + 0.3 * h              # higher wave, higher wipe out base rate
        skill_factor = 1 - self.skill      # higher skill, less wipe out rate

        p = base * skill_factor
        return min(0.7, max(0.01, p))

    def update_waiting_state(self, rule_type, active_waves):
        for wave in active_waves:
            if rule_type == "safe_distance":
                if any(abs(self.y - oy) <= 10 for oy in wave.occupied_y):
                    continue
            if abs(wave.x - self.x) <= 2:
                attempt = np.random.rand() < self.prob_attempt(wave.height)
                if attempt:
                    stood_up = np.random.rand() < self.prob_success(wave.height)
                    if stood_up:
                        self.state = 'surfing'
                        self.curr_riding_wave = wave
                        self.distance_on_wave = 0
                        self.ride_already_counted = False
                        wave.occupied_y.append(self.y)
                        break
    def update_paddling_state(self):
        if self.x > self.bp:
            self.x -= self.speed
        else:
            self.x += self.speed

        if abs(self.x - self.bp) <= 2:
            self.state = 'waiting'

    def update_surfing_state(self, current_time):
        # update position
        self.x -= self.curr_riding_wave.speed
        self.distance_on_wave += self.curr_riding_wave.speed

        # if the surfer rides safely all the way and reaches the shore,
        # switch back to paddling and reset wave-related states
        if self.x <= 0:
            self.state = 'paddling'
            self.distance_on_wave = 0
            self.curr_riding_wave = None
            self.ride_already_counted = False
        # check collision by comparing positions with other surfers
        elif self.check_collisions():
            self.stats['collisions'] += 1
            self.state = 'wipeout'
            return
        # check wipeout probability
        elif np.random.rand() < self.prob_wipeout(self.curr_riding_wave.height):
            self.stats['wipeout'] += 1
            self.state = 'wipeout'
            return
        # if none of the above events occur, update ride distance
        # count a successful ride once the threshold is reached
        elif (self.distance_on_wave >= SUCCESS_DISTANCE) and (not self.ride_already_counted):
            self.stats['success'] += 1
            self.ride_already_counted = True

            if self.last_catch_time is None:
                self.last_catch_time = current_time
            else:
                self.waiting_time_sum += current_time - self.last_catch_time
                self.last_catch_time = current_time

    def update_wipeout_state(self):
        """

        :return:
        """
        # move all the way toward the shore during a wipeout
        if self.curr_riding_wave:
            self.x -= self.curr_riding_wave.speed
        # once the surfer reaches the shore, reset state to paddling
        if self.x <= 0:
            self.state = 'paddling'
            self.distance_on_wave = 0
            self.curr_riding_wave = None
            self.ride_already_counted = False

    # Update single surfer
    def update_state_and_position(self, rule_type, active_waves, current_time):
        """

        :param rule_type:
        :param active_waves:
        :param current_time:
        :return:

        """
        if self.state == 'waiting':
            self.update_waiting_state(rule_type, active_waves)
        elif self.state == 'paddling':
            self.update_paddling_state()
        elif self.state == 'surfing':
            self.update_surfing_state(current_time)
        elif self.state == 'wipeout':
            self.update_wipeout_state()

    @classmethod
    # Update all surfers
    def update_all(cls, rule_type, active_waves, current_time):
        for surfer in list(cls.all_surfers):
            surfer.update_state_and_position(rule_type, active_waves, current_time)