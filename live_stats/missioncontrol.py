#!/usr/bin/python3
from GlobalVars import GlobalVars
from DataPayload import DataPayload
from Writers import FileWriter, ConsoleWriter, SQLWriter, GoogleEarthWriter
from Readers import SerialReader
from mysql.connector import Error
import argparse
from threading import Thread


# pip install mysql-connector-python
# pip install googleearthplot
# Remove all prints from googleearthplot. They are useless.
# https://grafana.com/docs/grafana/latest/datasources/mysql

## Payload format, if separator is |
# !date|latitude|longitude|altitude|course|horizontal_speed|x_rotation|y_rotation|internal_temperature_1|internal_temperature_2|external_temperature|iaq|pressure|humidity|bvoc|co2|uva_1|uva_2|beta_particles|satellites_connected!
# Data arrives in the form of a raw UTF-8 encoded string.


if __name__ == '__main__':
    # To create virtual COM ports when simulating run:
    # socat -d -d pty,link=/tmp/serialRead,raw,echo=0 pty,link=/tmp/serialWrite,raw,echo=0
    # Use /tmp/serialRead for the reader, /tmp/serialWrite for the simulator
    
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
    #parser.add_argument("--simulate", default="", help="Simulate input through a writable serial port")
    args = parser.parse_args()

    reader = SerialReader(args.serialport, args.baudrate, args.serialtimeout)
    writers = []

    if args.mysqlhost != "" and args.mysqluser != "" and args.mysqlpassword != "" and args.mysqldatabase != "":
        writers.append(SQLWriter(args.mysqlhost, args.mysqluser, args.mysqlpassword, args.mysqldatabase, args.mysqldrop))

    if args.console:
        writers.append(ConsoleWriter())

    if args.googleearthfile != "":
        writers.append(GoogleEarthWriter(args.googleearthfile))

    # if args.simulate != "":
    #     simulator = SerialSimulator(args.simulate, args.baudrate, args.serialtimeout)
    #     thread = Thread(target=simulator.write_data)
    #     thread.start()
    #
    #
    # def _writerFn(data: DataPayload) -> None:
    #     for writer in writers:
    #         try:
    #             writer.write(data)
    #         except Error as err:
    #             print(f"ERROR. Unable to comply: {err}")
    #
    # reader.read(_writerFn)
    