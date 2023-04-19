from GlobalVars import GlobalVars
from DataPayload import DataPayload
from abc import ABC, abstractmethod
import mysql.connector
from mysql.connector import Error
import math

class Writer(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def write(self, data:DataPayload) -> None:
        pass

class FileWriter(Writer):
    def __init__(self, filename) -> None:
        super().__init__()

    def write(self, data:DataPayload) -> None:
        pass

class ConsoleWriter(Writer):
    def __init__(self) -> None:
        super().__init__()

    def pretty_print_payload(self, raw_data:DataPayload) -> str:
        return f"Date={raw_data.date}. "+\
            f"Lat={raw_data.latitude}. "+\
            f"Lon={raw_data.longitude}. "+\
            f"Alt={raw_data.altitude}. "+\
            f"Course={raw_data.course}. "+\
            f"HSpeed={raw_data.horizontal_speed}. "+\
            f"VSpeed={raw_data.vertical_speed}. "+\
            f"XRotation={raw_data.x_rotation}. "+\
            f"YRotation={raw_data.y_rotation}. "+\
            f"IntTemp1={raw_data.internal_temperature_1}. "+\
            f"IntTemp2={raw_data.internal_temperature_2}. "+\
            f"ExtTemp={raw_data.external_temperature}. "+\
            f"IAQ={raw_data.iaq}. "+\
            f"Pressure={raw_data.pressure}. "+\
            f"Humidity={raw_data.humidity}. "+\
            f"bVOC={raw_data.bvoc}. "+\
            f"CO2={raw_data.co2}. "+\
            f"uva_1={raw_data.uva_1}. "+\
            f"uva_2={raw_data.uva_2}. "+\
            f"Temperature={raw_data.beta_particles}. "+\
            f"Satellites={raw_data.satellites_connected}. "

            # TODO: Move upwards
            # f"NSpeed={raw_data.net_speed}. "+\

    def write(self, data:DataPayload) -> None:
        print(self.pretty_print_payload(data))

class SQLWriter(Writer):
    table_name = 'cansat_data'
    def __init__(self, endpoint:str, user:str, password:str, database:str, drop:bool) -> None:
        super().__init__()
        connection = None
        try:
            connection = mysql.connector.connect(
                host=endpoint,
                user=user,
                password=password
            )

            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("You're connected to database: ", record)

        except Error as err:
            raise Error(f"Unable to connect to database: '{err}'")
        self._connection = connection
        self._execute_query(f"USE {database};")
        if drop:
            self._execute_query(f"DROP TABLE IF EXISTS {SQLWriter.table_name}")
        self._create_table()

    def _execute_query(self, query:str) -> None:
        cursor = self._connection.cursor()
        try:
            cursor.execute(query)
            self._connection.commit()
        except Error as err:
            raise Error(f"Error executing query '{query}': '{err}'")

    def _create_table(self) -> None:
        #SET @@sql_mode = sys.list_add(@@sql_mode, 'TIME_TRUNCATE_FRACTIONAL');
        self._execute_query(f'''CREATE TABLE IF NOT EXISTS {SQLWriter.table_name}(
            time DATETIME NOT NULL,
            etl FLOAT,
            latitude FLOAT,
            longitude FLOAT,
            altitude FLOAT,
            et_latitude FLOAT,
            et_longitude FLOAT,
            course FLOAT,
            net_velocity FLOAT,
            vertical_acceleration FLOAT,
            horizontal_speed FLOAT,
            vertical_speed FLOAT,
            x_rotation FLOAT,
            y_rotation FLOAT,
            internal_temperature_1 FLOAT,
            internal_temperature_2 FLOAT,
            external_temperature FLOAT,
            iaq FLOAT,
            pressure FLOAT,
            humidity FLOAT,
            bvoc FLOAT,
            co2 FLOAT,
            uva_1 FLOAT,
            uva_2 FLOAT,
            beta_particles FLOAT,
            satellites_connected FLOAT);''')

    def write(self, data:DataPayload) -> None:
        try:
            for idx in range(0, len(data.__dict__.keys())):
                key = list(data.__dict__.keys())[idx]
                value = list(data.__dict__.values())[idx]

                if value is None:
                    data.__dict__[key] = "NULL"
                
                if value == "NAN" or value == "nan":
                    data.__dict__[key] = "NULL"

                if isinstance(value, float):
                    if math.isnan(value):
                        data.__dict__[key] = "NULL"
            

            temporary_vertical_acceleration = data.vertical_acceleration if hasattr(data, "vertical_acceleration") else 0
            temporary_vertical_speed = data.vertical_speed if hasattr(data, "vertical_speed") else 0
            temporary_net_velocity = data.net_velocity if hasattr(data, "net_velocity") else 0
            temporary_elt = data.etl if hasattr(data, "etl") else 0
            temporary_et_latitude = data.etl if hasattr(data, "et_latitude") else 0
            temporary_et_longitude = data.etl if hasattr(data, "et_longitude") else 0

            print(f"\033[94m{data.__dict__}\033[0m\n")

            self._execute_query(f'''INSERT into {SQLWriter.table_name} 
                (time, etl, latitude, longitude, altitude, et_latitude, et_longitude, course, net_velocity, vertical_acceleration, horizontal_speed, vertical_speed, x_rotation, y_rotation, internal_temperature_1, internal_temperature_2, external_temperature, iaq, pressure, humidity, bvoc, co2, uva_1, uva_2, beta_particles, satellites_connected) 
                VALUES(
                '{data.date}',
                {temporary_elt},
                {data.latitude},
                {data.longitude},
                {data.altitude},
                {temporary_et_latitude},
                {temporary_et_longitude},
                {data.course[0]},
                {temporary_net_velocity},
                {temporary_vertical_acceleration},
                {data.horizontal_speed},
                {temporary_vertical_speed},
                {data.x_rotation},
                {data.y_rotation},
                {data.internal_temperature_1},
                {data.internal_temperature_2},
                {data.external_temperature},
                {data.iaq},
                {data.pressure},
                {data.humidity},
                {data.bvoc},
                {data.co2},
                {data.uva_1},
                {data.uva_2},
                {data.beta_particles},
                {data.satellites_connected});''')

                # TODO: Add {data.vertical_speed},
        except Error as err:
            raise Error(f"Error inserting values: '{err}'")
