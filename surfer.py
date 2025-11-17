class Surfer:
    """

    """

    MIN_ATTEMPT_RATE = 0.1
    MAX_ATTEMPT_RATE = 0.9

    def __init__(self, skill, board_type):
        self.skill = skill
        self.board_type = board_type

    def prob_attempt(self, wave_height, h_min, h_max):
        """
        Returns the probability that a surfer attempts the wave.

        Idea:
        - High waves → skilled surfers attempt more, beginners attempt less.
        - Low waves → beginners attempt more, skilled surfers have lower interest.

        Model:
        1. Normalize wave height to [0, 1].
        2. Compute "comfort" = how well the wave height matched the surfer's skill
        3. Map comfort to probability between 0.1 and 0.9

        :param wave_height:
        :param h_min:
        :param h_max:
        :return:
        """
        # Convert wave height to [0, 1] to match skill scale
        h = max(0, (wave_height - h_min) / (h_max - h_min))

        # Compute comfort representing the similarity between skill and wave height
        comfort = max(0, 1 - abs(h - self.skill))

        # Map comfort to attempt rate between 0.1 and 0.9
        attempt_rate = self.MIN_ATTEMPT_RATE + (self.MAX_ATTEMPT_RATE - self.MIN_ATTEMPT_RATE) * comfort
        return attempt_rate

    def prob_success(self, wave_height, h_min, h_max, alpha):
        """
        Returns the probability that a surfer successfully rides the current wave.

        Idea:
        Higher waves reduce success rates, but skilled surfers are less sensitive to wave height.

        :param wave_height:
        :param h_min:
        :param h_max:
        :param alpha: coefficient controlling how strongly wave height affects success
        :return:
        """
        # Convert wave height to [0, 1] to measure its impact on a surfer
        h = (wave_height - h_min) / (h_max - h_min)
        h = min(max(0, h), 1)
        return self.skill * (1 - alpha * h * (1 - self.skill))
