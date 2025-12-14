"""

"""
from config import *

class Wave:

    all_waves = []

    def __init__(self, height, speed):
        self.x = OCEAN_X_MAX
        self.height = height
        self.speed = speed
        self.occupied_y = []


        Wave.all_waves.append(self)

    # AI logic Check - 2
    @classmethod
    def update_all(cls):
        """
        Update the position of all waves and remove those that have moved out of bounds.
        :return: None
        >>> from config import *
        >>> Wave.all_waves = []
        >>> w1 = Wave(1.5, 10)
        >>> w2 = Wave(5, 160)
        >>> len(Wave.all_waves)
        2
        >>> Wave.update_all()
        >>> len(Wave.all_waves)
        1
        >>> Wave.all_waves[0].x
        140
        """
        for wave in list(cls.all_waves):
            wave.x -= wave.speed

            if wave.x <= 0:
                cls.all_waves.remove(wave)


