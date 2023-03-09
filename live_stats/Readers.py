from live_stats.GlobalVars import GlobalVars
from live_stats.DataPayload import DataPayload
from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from collections.abc import Callable
import serial, io


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
    

    def parse_payload(raw_data:str, separator:str) -> DataPayload:
        if raw_data[0] != "!" or raw_data[-1] != "!":
            raise Exception("Bad format for payload. Missing ! at beginning/end")
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
        if parts[6] != "" and parts[7] != "-":
            data.x_rotation = float(parts[7])
        if parts[7] != "" and parts[8] != "-":
            data.y_rotation = float(parts[8])
        if parts[8] != "" and parts[9] != "-":
            data.internal_temperature_1 = float(parts[9])
        if parts[9] != "" and parts[10] != "-":
            data.internal_temperature_2 = float(parts[10])
        if parts[10] != "" and parts[11] != "-":
            data.external_temperature = float(parts[11])
        if parts[11] != "" and parts[12] != "-":
            data.iaq = float(parts[12])
        if parts[12] != "" and parts[13] != "-":
            data.pressure = float(parts[13])
        if parts[13] != "" and parts[14] != "-":
            data.humidity = float(parts[14])
        if parts[14] != "" and parts[15] != "-":
            data.bvoc = float(parts[15])
        if parts[15] != "" and parts[16] != "-":
            data.co2 = float(parts[16])
        if parts[16] != "" and parts[17] != "-":
            data.uva_1 = float(parts[17])
        if parts[17] != "" and parts[18] != "-":
            data.uva_2 = float(parts[18])
        if parts[18] != "" and parts[19] != "-":
            data.beta_particles = float(parts[19])
        if parts[19] != "" and parts[20] != "-":
            data.satellites_connected = float(parts[20])
        
        return data


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

    def _extract_payloads(self, data_str: str) -> tuple[str, list[DataPayload]]:
        ret = []
        current_str = data_str
        while True:
            match = GlobalVars.PAYLOAD_REGEX.search(current_str)
            if match is None:
                return current_str, ret
            start, end = match.span()[0], match.span()[1]
            new_payload = self.parse_payload(current_str[start:end], "|")
            if self._previous_payload is not None:
                print("Computing synthetics")
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