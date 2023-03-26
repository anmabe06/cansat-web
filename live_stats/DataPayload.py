import time
import datetime
from datetime import datetime, timezone
from GlobalVars import GlobalVars

class DataPayload:
    def __init__(self, date: str, lat: float = None, lon: float = None, altitude: float = None, 
                course: float = None, horizontal_speed: float = None, 
                x_rotation: float = None, y_rotation: float = None, internal_temperature_1: float = None, 
                internal_temperature_2: float = None, external_temperature: float = None, iaq: float = None, 
                pressure: float = None, humidity: float = None, bvoc: float = None, co2: float = None, 
                uva_1: float = None, uva_2: float = None, beta_particles: float = None, satellites_connected: float = None):
        #self.date = date
        #Currently ignoring time
        self.date = str(datetime.now(timezone.utc))[:-6]
        self.latitude = lat
        self.longitude = lon
        self.altitude = altitude
        self.course = course
        self.vertical_acceleration = 0
        self.horizontal_speed = horizontal_speed
        self.vertical_speed = 0
        self.x_rotation = x_rotation
        self.y_rotation = y_rotation
        self.internal_temperature_1 = internal_temperature_1
        self.internal_temperature_2 = internal_temperature_2
        self.external_temperature = external_temperature
        self.iaq = iaq
        self.pressure = pressure
        self.humidity = humidity
        self.bvoc = bvoc
        self.co2 = co2
        self.uva_1 = uva_1
        self.uva_2 = uva_2
        self.beta_particles = beta_particles
        self.satellites_connected = satellites_connected
    
    def compute_synthetics(self, prev) -> None:
        if  self.date != prev.date:
            d1, d0 = datetime.strptime(self.date, GlobalVars.DATETIME_FORMAT), datetime.strptime(prev.date, GlobalVars.DATETIME_FORMAT)
            elapsed_time = (d1-d0).seconds+(d1-d0).microseconds

        if self.altitude is not None and prev.altitude is not None:
            self.vertical_speed = (self.altitude - prev.altitude)/elapsed_time
        
        if prev.vertical_speed is not None:
            self.vertical_acceleration = (self.vertical_speed - prev.vertical_speed)/elapsed_time
        pass