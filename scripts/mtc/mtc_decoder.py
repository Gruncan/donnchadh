import json
from datetime import datetime


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


    def load_content(self):
        with open(self.filename, "rb") as f:
            self.content = f.read()

        self.content = self.convert_to_bits(self.content)

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

        bits = self.content[start_offset:sum(header_bits)]


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
        return MtcObject(version, datetime(**mappings)), prev

    def __decode_mem_time_offset(self, start_offset):
        offset = start_offset + 12
        millisecond_timestamp = self.content[start_offset:offset]
        return int(millisecond_timestamp, 2), offset

    def __decode_mem_data_length(self, start_offset):
        offset = start_offset + 16
        stamp_size = self.content[start_offset:offset]
        return int(stamp_size, 2) + 1, offset

    def __decode_mem_data_bytes(self, length, offset):

        if length % 24 != 0:
            raise MtcDecoderException(f"Failed to parse: The 16 bit length parameter has been corrupted, it must be dividable by 16!")

        mem_data = []
        for i in range(0, length, 24):
            data = self.content[offset + i: offset + i + 24]
            data_key, data_value = int(data[:8], 2), int(data[8:], 2)
            mem_data.append((hex(data_key), data_value))

        return mem_data, offset + length


    def decode(self):
        if self.content is None:
            self.load_content()

        mtc_object, offset = self._decode_header()
        length_of_file = len(self.content)

        data_points = []
        while offset <= length_of_file:
            try:
                millisecond_offset, offset = self.__decode_mem_time_offset(offset)
                length, offset = self.__decode_mem_data_length(offset)

                mem_data, offset = self.__decode_mem_data_bytes(length, offset)

                data_points.append(MtcPoint(millisecond_offset, {key:value for key, value in mem_data}))
            except:
                break # We most likely broken something when force exiting

        mtc_object.set_data_points(data_points)

        return mtc_object




    @staticmethod
    def load_key_map(filename):
        with open(filename, "r") as f:
            name_map = json.load(f)

        MtcDecoder.key_map = {v:k for k, v in name_map.items()}












# MtcDecoder("memlog.mtc").decode()

mtcd = MtcDecoder("/home/duncan/Development/Uni/Thesis/system_test.mtc")
obj = mtcd.decode()
print(obj)

