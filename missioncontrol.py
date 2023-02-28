#!/usr/bin/python3

from abc import ABC, abstractmethod
import mysql.connector
from mysql.connector import Error
import argparse
import serial, io
from threading import Thread
import time
import datetime
import random
from collections.abc import Callable
import re
from googleearthplot.googleearthplot import googleearthplot
import datetime
import time


# pip install mysql-connector-python
# pip install googleearthplot
# Remove all prints from googleearthplot. They are useless.
# https://grafana.com/docs/grafana/latest/datasources/mysql

## Payload format, if separator is |
# !date|latitude|longitude|altitude|course|horizontal_speed|vertical_speed|x_rotation|y_rotation|internal_temperature_1|internal_temperature_2|external_temperature|iaq|pressure|humidity|bvoc|co2|uva_1|uva_2|beta_particles|satellites_connected!
# Data arrives in the form of a raw UTF-8 encoded string.

#TODO work this out with the cansat code.
PAYLOAD_REGEX = re.compile(r'!([^\|!]+\|){20}[^\|!]+!')
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class DataPayload:
    def __init__(self, date: str, lat: float = None, lon: float = None, altitude: float = None, 
                course: float = None, horizontal_speed: float = None, vertical_speed: float = None, 
                x_rotation: float = None, y_rotation: float = None, internal_temperature_1: float = None, 
                internal_temperature_2: float = None, external_temperature: float = None, iaq: float = None, 
                pressure: float = None, humidity: float = None, bvoc: float = None, co2: float = None, 
                uva_1: float = None, uva_2: float = None, beta_particles: float = None, satellites_connected: float = None):
        #TODO Tiny GPS is supposed to follow NMEA data format, meaning times are UTC.
        self.date = datetime.datetime.strptime(date, DATETIME_FORMAT)
        self.latitude = lat
        self.longitude = lon
        self.altitude = altitude
        self.course = course
        self.horizontal_speed = horizontal_speed
        self.vertical_speed = vertical_speed
        if horizontal_speed is not None and vertical_speed is not None:
            #self.net_speed = (horizontal_speed^2)*(vertical_speed^2)    # Calculated
            pass
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
        if self.altitude is not None and prev.altitude is not None and self.date != prev.date:
            d1, d0 = datetime.datetime.strptime(self.date, DATETIME_FORMAT), datetime.datetime.strptime(prev.date, DATETIME_FORMAT)
            elapsed_time = (d1-d0).seconds+(d1-d0).microseconds
            self.vertical_speed = (prev.altitude - self.altitude)/elapsed_time
            self.vertical_acceleration = None #TODO
        # if self.horizontal_speed is not None and prev.horizontal_speed is not None:
        #     self.horizontal_acceleration = None #TODO
        pass

def parse_payload(raw_data:str, separator:str) -> DataPayload:
    if raw_data[0] != "!" or raw_data[-1] != "!":
        raise Error("Bad format for payload. Missing ! at beginning/end")
    raw_data = raw_data[1:-1]
    parts = raw_data.split(separator)
    date = parts[0]
    data = DataPayload(date)
    if parts[1] != "" and parts[1] != "-":
        data.latitude = float(parts[1])
    if parts[2] != "" and parts[2] != "-":
        data.longitude = float(parts[2])
    if parts[3] != "" and parts[3] != "-":
        data.altitude = float(parts[3])
    if parts[4] != "" and parts[4] != "-":
        data.course = float(parts[4])
    if parts[5] != "" and parts[5] != "-":
        data.horizontal_speed = float(parts[5])
    if parts[6] != "" and parts[6] != "-":
        data.vertical_speed = float(parts[6])
    if parts[7] != "" and parts[7] != "-":
        data.x_rotation = float(parts[7])
    if parts[8] != "" and parts[8] != "-":
        data.y_rotation = float(parts[8])
    if parts[9] != "" and parts[9] != "-":
        data.internal_temperature_1 = float(parts[9])
    if parts[10] != "" and parts[10] != "-":
        data.internal_temperature_2 = float(parts[10])
    if parts[11] != "" and parts[11] != "-":
        data.external_temperature = float(parts[11])
    if parts[12] != "" and parts[12] != "-":
        data.iaq = float(parts[12])
    if parts[13] != "" and parts[13] != "-":
        data.pressure = float(parts[13])
    if parts[14] != "" and parts[14] != "-":
        data.humidity = float(parts[14])
    if parts[15] != "" and parts[15] != "-":
        data.bvoc = float(parts[15])
    if parts[16] != "" and parts[16] != "-":
        data.co2 = float(parts[16])
    if parts[17] != "" and parts[17] != "-":
        data.uva_1 = float(parts[17])
    if parts[18] != "" and parts[18] != "-":
        data.uva_2 = float(parts[18])
    if parts[19] != "" and parts[19] != "-":
        data.beta_particles = float(parts[19])
    if parts[20] != "" and parts[20] != "-":
        data.satellites_connected = float(parts[20])
    
    return data

def pretty_print_payload(raw_data:DataPayload) -> str:
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

def serialize_payload(raw_data:DataPayload, separator:str) -> str:
    return f"!{raw_data.date}{separator}{raw_data.latitude}{separator}"+\
        f"{raw_data.longitude}{separator}{raw_data.altitude}{separator}"+\
        f"{raw_data.course}{separator}{raw_data.horizontal_speed}{separator}"+\
        f"{raw_data.vertical_speed}{separator}{raw_data.x_rotation}{separator}"+\
        f"{raw_data.y_rotation}{separator}{raw_data.internal_temperature_1}{separator}"+\
        f"{raw_data.internal_temperature_2}{separator}{raw_data.external_temperature}{separator}"+\
        f"{raw_data.iaq}{separator}{raw_data.pressure}{separator}"+\
        f"{raw_data.humidity}{separator}{raw_data.bvoc}{separator}"+\
        f"{raw_data.co2}{separator}{raw_data.uva_1}{separator}{raw_data.uva_2}{separator}"+\
        f"{raw_data.beta_particles}{separator}{raw_data.satellites_connected}!"

class Reader(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def read(self, callback: Callable[[DataPayload], None]) -> None:
        pass

class SerialReader(Reader):
    def __init__(self, name:str, baud:int, timeout:int) -> None:
        super().__init__()
        self._serial = serial.Serial(name, baud, timeout=timeout)
        self._previous_payload = None

    def _extract_payloads(self, data_str: str) -> tuple[str, list[DataPayload]]:
        ret = []
        current_str = data_str
        while True:
            match = PAYLOAD_REGEX.search(current_str)
            if match is None:
                return current_str, ret
            start, end = match.span()[0], match.span()[1]
            new_payload = parse_payload(current_str[start:end], "|")
            if self._previous_payload is not None:
                new_payload.compute_synthetics(self._previous_payload)
            self._previous_payload = new_payload
            ret.append(new_payload)
            if end == len(current_str):
                return "", ret
            current_str = current_str[end:]

    def read(self, callback: Callable[[DataPayload], None]) -> None:
        buffer = ""
        while True:
            result = self._serial.read(100)
            buffer += (result.decode('utf-8'))
            buffer, payloads = self._extract_payloads(buffer)
            for payload in payloads:
                callback(payload)

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

    def write(self, data:DataPayload) -> None:
        print(pretty_print_payload(data))

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
            latitude FLOAT,
            longitude FLOAT,
            altitude FLOAT,
            course FLOAT,
            horizontal_speed FLOAT,
            vertical_speed FLOAT,
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
            for value_key in data.__dict__:
                if value_key is None:
                    data.__dict__[value_key] = "NULL"

            self._execute_query(f'''INSERT into {SQLWriter.table_name} 
                (time, latitude, longitude, altitude, course, horizontal_speed, x_rotation, y_rotation, internal_temperature_1, internal_temperature_2, external_temperature, iaq, pressure, humidity, bvoc, co2, uva_1, uva_2, beta_particles, satellites_connected) 
                VALUES(
                '{data.date}',
                {data.latitude},
                {data.longitude},
                {data.altitude},
                {data.course},
                {data.horizontal_speed},
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

class GoogleEarthWriter(Writer):
    def __init__(self, filename:str) -> None:
        super().__init__()
        self._filename = filename
        self._latitudes = []
        self._longitudes = []
        self._altitudes = []

    def write(self, data:DataPayload) -> None:
        self._latitudes.append(data.latitude)
        self._longitudes.append(data.longitude)
        self._altitudes.append(data.altitude)
        # For this to display right it needs the following changes in the library:
        # Within PlotLineChart:
        # ls.style.polystyle.outline = 1 and
        # ls.style.polystyle.fill = 0
        # ls.altitudemode = simplekml.AltitudeMode.absolute
        gep = googleearthplot()
        gep.PlotLineChart(
            latList = self._latitudes,
            lonList = self._longitudes,
            heightList = self._altitudes,
            name = "Trajectory",
            color = "cyan",
            width = 3)
        gep.GenerateKMLFile(filepath = self._filename)

class SerialSimulator:
    def __init__(self, name:str, baud:int, timeout:int) -> None:
        self._serial = serial.Serial(name, baud, timeout=timeout)
        self._io = io.TextIOWrapper(io.BufferedWriter(self._serial))

    def write_data(self):
        while True:
            data = self._random_payload()
            data_bytes = str.encode(serialize_payload(data, "|"))
            self._serial.write(data_bytes)
            time.sleep(1)
    
    def _random_payload(self) -> str:
        now = datetime.datetime.now(datetime.timezone.utc)
        return DataPayload(
            now.strftime("%Y-%m-%d %H:%M:%S"),
            lat=random.uniform(40.41, 40.39),
            lon=random.uniform(-3.8, -3.7),
            altitude=random.uniform(600, 750),
            course=random.uniform(0, 359),
            horizontal_speed=random.uniform(1, 10),
            vertical_speed=random.uniform(1, 10),
            x_rotation=random.uniform(0, 359),
            y_rotation=random.uniform(0, 359),
            internal_temperature_1=random.uniform(10, 30),
            internal_temperature_2=random.uniform(10, 30),
            external_temperature=random.uniform(10, 30),
            iaq=random.uniform(900, 1100),
            pressure=random.uniform(900, 1100),
            humidity=random.uniform(0, 100),
            bvoc=random.uniform(0, 100),
            co2=random.uniform(0, 300),
            uva_1=random.randint(0, 12),
            uva_2=random.randint(0, 12),
            beta_particles=random.randint(0, 3),
            satellites_connected=random.randint(1, 5))

if __name__ == '__main__':
    # To create virtual COM ports when simulating run:
    # socat -d -d pty,link=/tmp/serialRead,raw,echo=0 pty,link=/tmp/serialWrite,raw,echo=0
    # Use /tmp/serialRead for the reader, /tmp/serialWrite for the simulator
    #
    # s = SQLWriter(
    #     endpoint="qagi935.anmabe.es",
    #     user="qahn185",
    #     password="R2x0tuA8DhPbKE67")
    parser = argparse.ArgumentParser()
    parser.add_argument("--serialport", default="/dev/ttyREAD", help="Serial port device")
    parser.add_argument("--baudrate", default=9600, help="Serial port baud rate")
    parser.add_argument("--serialtimeout", default=1, help="Serial port timeout in seconds")
    parser.add_argument("--mysqlhost", default="", help="MySQL database host")
    parser.add_argument("--mysqluser", default="", help="MySQL database user name")
    parser.add_argument("--mysqlpassword", default="", help="MySQL database password")
    parser.add_argument("--mysqldatabase", default="", help="MySQL database name")
    parser.add_argument("--mysqldrop", default=False, action='store_true', help="MySQL automatic table drop on start")
    parser.add_argument("--outfile", help="File to write CSV output")
    parser.add_argument("--console", action="store_true", default=False, help="Console output")
    parser.add_argument("--googleearthfile", default="", help="Google Earth Pro KML file name")
    parser.add_argument("--simulate", default="", help="Simulate input through a writable serial port")
    args = parser.parse_args()

    reader = SerialReader(args.serialport, args.baudrate, args.serialtimeout)
    writers = []

    if args.mysqlhost != "" and args.mysqluser != "" and args.mysqlpassword != "" and args.mysqldatabase != "":
        writers.append(SQLWriter(args.mysqlhost, args.mysqluser, args.mysqlpassword, args.mysqldatabase, args.mysqldrop))

    if args.console:
        writers.append(ConsoleWriter())

    if args.googleearthfile != "":
        writers.append(GoogleEarthWriter(args.googleearthfile))

    if args.simulate != "":
        simulator = SerialSimulator(args.simulate, args.baudrate, args.serialtimeout)
        thread = Thread(target=simulator.write_data)
        thread.start()
    
    def _writerFn(data: DataPayload) -> None:
        for writer in writers:
            try:
                writer.write(data)
            except Error as err:
                print(f"ERROR. Unable to comply: {err}")
    
    reader.read(_writerFn)
    