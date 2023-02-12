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


# pip install mysql-connector-python
# pip install googleearthplot
# Remove all prints from googleearthplot. They are useless.
# https://grafana.com/docs/grafana/latest/datasources/mysql

## Payload format, if separator is |
# !date|latitude|longitude|altitude|course|speed|temperature|pressure|humidity|gas|co2|uva1|uva2!
# Data arrives in the form of a raw UTF-8 encoded string.

#TODO work this out with the cansat code.
PAYLOAD_REGEX = re.compile(r'!([^\|!]+\|){12}[^\|!]+!')
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class DataPayload:
    def __init__(self, date: str, lat: float = None, lon: float = None,
                 altitude: float = None, course: float = None, speed: float = None,
                 age: int = None, satellites: int = None, temperature: float = None,
                 pressure:float = None, humidity: float = None, co2: float = None,
                 iaq: int = None, bvoc: int = None, uva1: int = None,
                 uva2: int = None) -> None:
        self.date = date
        self.latitude = lat
        self.longitude = lon
        self.altitude = altitude
        self.course = course
        self.horizontal_speed = speed
        self.satellites = satellites
        self.temperature = temperature
        self.pressure = pressure
        self.humidity = humidity
        self.iaq = iaq
        self.bvoc = bvoc
        self.co2 = co2
        self.uva1 = uva1
        self.uva2 = uva2
        self.vertical_speed = None
        self.horizontal_acceleration = None
        self.vertical_acceleration = None
        self.calculated_altitude = None #TODO 44330 * [1-(pressure/p0)^(1/5.225)]
    
    def compute_synthetics(self, prev) -> None:
        if self.altitude is not None and prev.altitude is not None:
            d1, d0 = datetime.datetime.strptime(self.date, DATETIME_FORMAT), datetime.datetime.strptime(prev.date, DATETIME_FORMAT)
            elapsed_time = (d1-d0).seconds+(d1-d0).microseconds
            self.vertical_speed = (prev.altitude - self.altitude)/elapsed_time
            self.vertical_acceleration = None #TODO
        if self.horizontal_speed is not None and prev.horizontal_speed is not None:
            self.horizontal_acceleration = None #TODO

def parse_payload(raw_data:str, separator:str) -> DataPayload:
    if raw_data[0] != "!" or raw_data[-1] != "!":
        raise Error("Bad format for payload. Missing ! at beginning/end")
    raw_data = raw_data[1:-1]
    parts = raw_data.split(separator)
    date = parts[0]
    data = DataPayload(date)
    if parts[1] != "":
        data.latitude = float(parts[1])
    if parts[2] != "":
        data.longitude = float(parts[2])
    if parts[3] != "":
        data.altitude = float(parts[3])
    if parts[4] != "":
        data.course = float(parts[4])
    if parts[5] != "":
        data.horizontal_speed = float(parts[5])
    if parts[6] != "":
        data.temperature = float(parts[6])
    if parts[7] != "":
        data.pressure = float(parts[7])
    if parts[8] != "":
        data.humidity = float(parts[8])
    if parts[9] != "":
        pass
    if parts[10] != "":
        data.co2 = float(parts[10])
    if parts[11] != "":
        data.uva1 = int(parts[11])
    if parts[12] != "":
        data.uva2 = int(parts[12])
    return data

def pretty_print_payload(raw_data:DataPayload) -> str:
    return f"Date={raw_data.date}. "+\
        f"Lat={raw_data.latitude}. "+\
        f"Lon={raw_data.longitude}. "+\
        f"Alt={raw_data.altitude}. "+\
        f"Course={raw_data.course}. "+\
        f"HSpeed={raw_data.horizontal_speed}. "+\
        f"Satellites={raw_data.satellites}. "+\
        f"Temperature={raw_data.temperature}. "+\
        f"Pressure={raw_data.pressure}. "+\
        f"Humidity={raw_data.humidity}. "+\
        f"IAQ={raw_data.iaq}. "+\
        f"bVOC={raw_data.bvoc}. "+\
        f"CO2={raw_data.co2}. "+\
        f"UVA1={raw_data.uva1}. "+\
        f"UVA2={raw_data.uva2}. "+\
        f"VSpeed={raw_data.vertical_speed}. "

def serialize_payload(raw_data:DataPayload, separator:str) -> str:
    return f"!{raw_data.date}{separator}{raw_data.latitude}{separator}"+\
        f"{raw_data.longitude}{separator}{raw_data.altitude}{separator}"+\
        f"{raw_data.course}{separator}{raw_data.horizontal_speed}{separator}"+\
        f"{raw_data.temperature}{separator}{raw_data.pressure}{separator}"+\
        f"{raw_data.humidity}{separator}0{separator}"+\
        f"{raw_data.co2}{separator}{raw_data.uva1}{separator}{raw_data.uva2}!"

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
                passwd=password
            )
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
        #TODO readjust
        self._execute_query(f'''CREATE TABLE IF NOT EXISTS {SQLWriter.table_name}(
            time DATETIME NOT NULL,
            latitude FLOAT,
            longitude FLOAT,
            course FLOAT,
            horizontal_speed FLOAT,
            temperature FLOAT,
            pressure FLOAT,
            humidity FLOAT,
            gas FLOAT,
            co2 FLOAT,
            uva1 INT,
            uva2 INT);''')

    def write(self, data:DataPayload) -> None:
        try:
            self._execute_query(f'''INSERT into {SQLWriter.table_name} VALUES(
                "{data.date}",
                {data.latitude},
                {data.longitude},
                {data.course},
                {data.horizontal_speed},
                {data.temperature},
                {data.pressure},
                {data.humidity},
                0,
                {data.co2},
                {data.uva1},
                {data.uva2});''')
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
        #TODO readjust
        return DataPayload(
            now.strftime("%Y-%m-%d %H:%M:%S"),
            lat=random.uniform(40.41, 40.39),
            lon=random.uniform(-3.8, -3.7),
            altitude=random.uniform(600, 750),
            course=random.uniform(0, 359),
            speed=random.uniform(1, 10),
            temperature=random.uniform(10, 30),
            pressure=random.uniform(900, 1100),
            humidity=random.uniform(0, 100),
            co2=random.uniform(0, 300),
            uva1=random.randint(0, 12),
            uva2=random.randint(0, 12))

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
    parser.add_argument("--baudrate", default=19600, help="Serial port baud rate")
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
