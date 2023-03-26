import time
from mysql.connector import Error
from Writers import SQLWriter
from Readers import SerialReader
from DataPayload import DataPayload
from GlobalVars import GlobalVars
import random
import datetime
from datetime import datetime, timezone




class Launch():
    def __init__(self, host, user, password, database, drop, serialport, baudrate, serialtimeout):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.drop_table = drop
        self.serialport = serialport
        self.baudrate = baudrate
        self.serialtimeout = serialtimeout

    def start(self):
        self.start_reception()

    def start_reception(self):
        self.SQLWriter = SQLWriter(self.host, self.user, self.password, self.database, self.drop_table)
        self.SERIALreader = SerialReader(self.serialport, self.baudrate, self.serialtimeout)
        self.SERIALreader.read(self.update_database)
    
    def update_database(self, data: DataPayload):
        self.SQLWriter.write(data)