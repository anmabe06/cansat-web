import re
import math

class GlobalVars():
    PAYLOAD_REGEX = re.compile(r'!([^\|!]+\|){19}[^\|!]+!')
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
    BASE_ALTITUDE = 777
    METRES_TO_DEGREES_LATITUDE = 1 / 111_111
    def METRES_TO_DEGREES_LONGITUDE(latitude):
        return 1 / (111_111 * math.cos(latitude * math.pi / 180))