import re

class GlobalVars():
    PAYLOAD_REGEX = re.compile(r'!([^\|!]+\|){19}[^\|!]+!')
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'