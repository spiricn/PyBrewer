# PyBrewer

Raspberry PI based homebrew temperature controller

## Dependencies

* Python3

* SSC ( https://github.com/spiricn/ssc )
  Used as a HTTP server backend library.

* PyRPI ( https://github.com/spiricn/PyRPi )
  Hardware control utility library.

* PyInstaller ( http://www.pyinstaller.org/ )
  Used to package PyBrewer into a binary application.

### Buildling PyBrewer

Steps necessary to build PyBrewer are described by the [Dockerfile](docker/Dockerfile).

You may build it manually, or simply by building the docker image and copying the pybrewer_x.y.z.deb file out of the container.

PyBrewer can then by installed by running:

```sh
sudo dpkg -i pybrewer_x.y.z.deb
```

### Service control
PyBrewer service can be started/stopped/restarted with the following commands:

```sh
sudo /etc/init.d/pybrewer start
sudo /etc/init.d/pybrewer stop
sudo /etc/init.d/pybrewer restart
```

By default PyBrewer web interface is available on port 8080 ( http://localhost:8080 )


### Quickstart

In order for the temperature control to work, the following needs to be configured in the *~/.pybrewer/config.py* file:

1. External sensor - A DS18B20 probe which monitors the temperature around the fermentation vessel.

```py
    'sensors': [
                {"NAME" : "Coolant Temperature", "ID" : "COOLANT_001", "DEV_ID" : "28-0516a0632dff", "COLOR" : "rgb(153, 217, 234)", "GRAPH" : True},
    ],

    'externalSensor': 'COOLANT_001',
```

2. Thermal switch - Relay switch which either turns on the heating or cooling depending on the mode configured.

```py
    'switches': [
                {"NAME" : "Heating", "ID" : "TEMP_001",  "GPIO_PIN" : 14, "COLOR" : "rgb(148, 12, 18)", "GRAPH" : True},
    ],

    'thermalSwitch': 'TEMP_001',
```

3. Coolant switch - Relay swithc which turns on the temperature dispersion unit (e.g. water pump, cooling fan, etc.)

```py
    'switches': [
                {"NAME" : "Pump", "ID" : "PUMP_001", "GPIO_PIN" : 18, "COLOR" : "rgb(63, 72, 204)", "GRAPH" : False},
    ],

    'pumpSwitch': 'PUMP_001',
```


Additional sensors or switches may be added, and will automatically be plotted in the history graphs.