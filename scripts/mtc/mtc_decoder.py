import json
from datetime import datetime
import time

class MtcDecoderException(Exception):
    pass


class MtcPoint:

    def __init__(self, time_offset, value_map):
        self.time_offset = time_offset
        self.value_map = value_map

    def __getitem__(self, item):
        return self.value_map.get(item, None)


class MtcObject:

    def __init__(self, version, date):
        self.version = version
        self.date = date
        self.data = None


    def set_data_points(self, mtc_data_points):
        self.data = mtc_data_points


class MtcDecoder:

    key_map = {}

    def __init__(self, filename):
        self.filename = filename
        self.content = None
        self.header_bits = None


    def load_content(self):
        with open(self.filename, "rb") as f:
            self.content = f.read()

        self.header_bits = self.convert_to_bits(self.content[:5])
        self.content = self.content[5:]

    def convert_to_bits(self, bbytes):
        return ''.join([format(byte, '08b') for byte in bbytes])

    def __header_decode_check(self, header_mappings):
        if header_mappings["version"] != 1:
            raise MtcDecoderException(f"Failed to parse: Header version {header_mappings['version']}, not recognised!")

        year = header_mappings["year"]
        if year < 00 or year >= 63:
            raise MtcDecoderException(f"Failed to parse: You must be a time traveller this version does not support years that big!")

        month = header_mappings["month"]
        if month < 1 or month > 12:
            raise MtcDecoderException(f"Failed to parse: A month must be between 1 and 12!")
            # This should be impossible give the number of bits unless we somehow parse more?

        day = header_mappings["day"]
        if day < 1 or day > 31:
            raise MtcDecoderException(f"Failed to parse: A day must be between 1 and 31!")

        hour = header_mappings["hour"]
        if hour < 0 or hour > 23:
            raise MtcDecoderException(f"Failed to parse: A hour must be between 0 and 23!")

        minute = header_mappings["minute"]
        if minute < 0 or minute > 59:
            raise MtcDecoderException(f"Failed to parse: A minute must be between 0 and 59!")

        second = header_mappings["second"]
        if second < 0 or second > 59:
            raise MtcDecoderException(f"Failed to parse: A second must be between 0 and 59!")

        return True


    def _decode_header(self, start_offset=0):
        header_bits = [8, 6, 4, 5, 5, 6, 6]
        header_names = ["version", "year", "month", "day", "hour", "minute", "second"]

        bits = self.header_bits

        prev = start_offset
        mappings = {}
        for h_bits, name in zip(header_bits, header_names):
            value = int(bits[prev: prev + h_bits], 2)
            if name in ("month"):
                value += 1
            mappings[name] = value

            prev += h_bits

        self.__header_decode_check(mappings)
        version = mappings.pop("version")

        mappings["year"] += 2000
        return MtcObject(version, datetime(**mappings)), 0

    def __decode_mem_time_offset(self, start_offset):
        millisecond_timestamp = int.from_bytes(self.content[start_offset: start_offset+2])
        return millisecond_timestamp, start_offset + 2

    def __decode_mem_data_length(self, start_offset):
        stamp_size = int.from_bytes(self.content[start_offset: start_offset + 2])
        return stamp_size, start_offset + 2

    def __decode_mem_data_bytes(self, length, offset):

        # if length % 24 != 0:
        #     raise MtcDecoderException(f"Failed to parse: The 16 bit length parameter has been corrupted, it must be dividable by 16!")

        mem_data = []
        for i in range(0, length, 3):
            data = self.content[offset + i: offset + i + 3]
            data_key = int.from_bytes([data[0]])
            data_value = int.from_bytes(data[1:])
            mem_data.append((hex(data_key), data_value))

        return mem_data


    def decode(self):
        if self.content is None:
            self.load_content()

        mtc_object, offset = self._decode_header()
        length_of_file = len(self.content)

        tasks = []
        while offset < length_of_file:
            try:
                millisecond_offset, offset = self.__decode_mem_time_offset(offset)
                length, offset = self.__decode_mem_data_length(offset)

                mem_data = self.__decode_mem_data_bytes(length, offset)
                tasks.append((millisecond_offset, {k:v for k, v in mem_data}))

                offset += length
            except Exception as e:
                print(e)
                break  # We most likely broken something when force exiting

        mtc_object.set_data_points(tasks)
        return mtc_object

    @staticmethod
    def load_key_map(filename):
        with open(filename, "r") as f:
            name_map = json.load(f)

        MtcDecoder.key_map = {v:k for k, v in name_map.items()}












# MtcDecoder("memlog.mtc").decode()

start_time = time.time()
mtcd = MtcDecoder("/home/duncan/Development/C/mem-monitor/full_decode_test2.mtc")
MtcDecoder.load_key_map("v1_encoding_key_map.json")
print(len(MtcDecoder.key_map))

obj = mtcd.decode()

end_time = time.time()

elapsed_time = end_time - start_time

print(f"Elapsed time: {elapsed_time} seconds")

