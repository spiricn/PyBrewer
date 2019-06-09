from rpi.DS18B20.TemperatureSensor import TemperatureSensor
import time
import random

class MockTemperatureSensor(TemperatureSensor):
    # Maximim change frquency
    UPDATE_DELTA_SEC = 2

    # Maximum update step
    UPDATE_STEP = 0.1

    # Temperature range
    TEMP_RANGE = (19, 23)

    def __init__(self, deviceId):
        self._deviceId = deviceId

        self._lastRead = 0

        minTemp, maxTemp = self.TEMP_RANGE

        # Pick a random starting tmeperature
        self._currTemp = minTemp + random.random() * (maxTemp - minTemp)

        # Pick a random direction
        self._direction = random.choice((-1, 1))

    def getTemperatureCelsius(self):
        currTime = time.time()

        if currTime - self._lastRead < self.UPDATE_DELTA_SEC:
            # Too fast
            return self._currTemp

        self._lastRead = currTime

        # Are we out of range ?
        if self._currTemp < self.TEMP_RANGE[0] or self._currTemp >  self.TEMP_RANGE[1]:
            # Change direction, and get back into range
            self._direction *= -1

            self._currTemp = max(self._currTemp, self.TEMP_RANGE[0])

            self._currTemp = min(self._currTemp, self.TEMP_RANGE[1])

        # Change temperature
        self._currTemp += self._direction * self.UPDATE_STEP * random.random()

        if random.random() < 0.1:
            self._direction *= -1

        return self._currTemp
