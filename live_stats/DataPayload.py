import time
import datetime
from datetime import datetime, timezone
from GlobalVars import GlobalVars
import math

class DataPayload:
    def __init__(self, date: str, lat: float = None, lon: float = None, altitude: float = None, 
                course: list = None, horizontal_speed: float = None, 
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
        
        if hasattr(self, "vertical_speed"):
            self.net_velocity = math.sqrt((self.vertical_speed)**2 + (self.horizontal_speed)**2)
            #print(f'net velocity: {self.net_velocity}')
        
        if GlobalVars.BASE_ALTITUDE != None:
            if self.vertical_speed == 0:
                self.etl = 0
            else:
                self.etl = abs(self.altitude - GlobalVars.BASE_ALTITUDE) / abs(self.vertical_speed)
                # In case velocity is almost cero, to avoid an etl of a magnitude of days, weeks or years
                if self.etl > 3600:
                    self.etl = 0

        if hasattr(self, "course") and self.etl != 0 and hasattr(self, "horizontal_speed"):
            angle = (-self.course[0] + 90) * math.pi / 180
            et_distance = self.horizontal_speed * self.etl
            
            self.et_latitude = self.latitude + (et_distance * math.cos(angle)) * GlobalVars.METRES_TO_DEGREES_LATITUDE
            self.et_longitude = self.longitude + (et_distance * math.sin(angle)) * GlobalVars.METRES_TO_DEGREES_LONGITUDE(self.et_latitude)
            print(f"Estimated Latitude: {self.et_latitude}\nEstimated Longitude {self.et_longitude}")

        else:
            self.et_latitude = self.latitude
            self.et_longitude = self.longitude
