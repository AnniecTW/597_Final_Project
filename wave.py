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
        for wave in list(cls.all_waves):
            wave.x -= wave.speed

            if wave.x <= 0:
                cls.all_waves.remove(wave)


