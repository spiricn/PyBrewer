import random


class TemperatureSensor:
    '''
    Reads temperatures from liquid & ambient sensors
    '''

    def __init__(self):
        pass

    def getAmbientCelsius(self):
        '''
        Ambient temperature
        '''

        # TODO Implement
        return random.randrange(20, 30)

    def getLiquidCelsius(self):
        '''
        Liquid temperature
        '''

        # TODO Implement
        return random.randrange(20, 30)
