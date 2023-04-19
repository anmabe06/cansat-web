import time
from mysql.connector import Error
from Writers import SQLWriter
from DataPayload import DataPayload
from GlobalVars import GlobalVars
import random
import datetime
from datetime import datetime, timezone




class LaunchSimulator():
    def __init__(self, host, user, password, database, data_amount, delay, drop):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.data_amount = int(data_amount)
        self.delay = float(delay)
        self.drop_table = drop
        self.start_simulation()


    def start_simulation(self):
        self.SQLWriter = SQLWriter(self.host, self.user, self.password, self.database, self.drop_table)
        previous_data = None

        for _ in range(self.data_amount):
            print(_)
            provisional_payload = self._simulate_data(previous_data)
            self.SQLWriter.write(provisional_payload)

            time.sleep(self.delay / 1000)
            previous_data = provisional_payload

        return True


    def _simulate_data(self, previous_data):
        # provisional_date = str(datetime.datetime.now().strftime(GlobalVars.DATETIME_FORMAT))
        # IMPORTANT --> [:-6] was added to remove the +00:00 suffix
        provisional_date = str(datetime.now(timezone.utc))[:-6]
        provisional_latitude = random.randint(30, 50)
        provisional_longitude = random.randint(30, 50)
        provisional_altitude = random.randint(0, 1000)
        provisional_course = [0, "N"]
        provisional_horizontal_speed = random.randint(8, 13)
        provisional_x_rotation = random.randint(0, 359)
        provisional_y_rotation = random.randint(0, 359)
        provisional_internal_temperature_1 = random.randint(15, 30)
        provisional_internal_temperature_2 = random.randint(15, 30)
        provisional_external_temperature = random.randint(-5, 5)
        provisional_iaq = random.randint(5000, 6000)
        provisional_pressure = random.randint(100000, 102000)
        provisional_humidity = random.randint(85, 100)
        provisional_bvoc = 0
        provisional_co2 = random.uniform(0, 0.001)
        provisional_uva_1 = random.randint(100, 200)
        provisional_uva_2 = random.randint(100, 200)
        provisional_beta_particles = round(random.uniform(-0.5, 0.7))
        provisional_satellites_connected = random.randint(4, 5)

        provisional_payload = DataPayload(provisional_date, provisional_latitude, provisional_longitude, provisional_altitude, provisional_course, provisional_horizontal_speed, provisional_x_rotation, provisional_y_rotation, provisional_internal_temperature_1, provisional_internal_temperature_2, provisional_external_temperature, provisional_iaq, provisional_pressure, provisional_humidity, provisional_bvoc, provisional_co2, provisional_uva_1, provisional_uva_2, provisional_beta_particles, provisional_satellites_connected)
        
        if previous_data is not None:
            provisional_payload.compute_synthetics(previous_data)
        
        return provisional_payload