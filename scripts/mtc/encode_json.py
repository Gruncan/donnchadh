import json
import os
import sys
from datetime import datetime


date_format = "%Y-%m-%d %H:%M:%S.%f"

VERSION = 1

def encode_datetime(dt):
    obj = datetime.strptime(dt, date_format)
    year_bits = int(str(obj.year)[2:])
    month_bits = obj.month - 1
    day_bits = obj.day - 1
    hour_bits = obj.hour
    minute_bits = obj.minute - 1
    second_bits = obj.second - 1

    offsets = [6, 4, 5, 5, 6, 6]
    datetime_bits = [year_bits, month_bits, day_bits, hour_bits, minute_bits, second_bits]

    summation = 0b0
    offset = sum(offsets)
    for bits, os in zip(datetime_bits, offsets):
        offset -= os
        v = min(bits, (2 ** os)) << offset
        summation |= v

    return hex(summation)[2:]

def encode_milliseconds(current_dt, prev_dt):
    obj = datetime.strptime(current_dt, date_format)
    prev_dt_obj = datetime.strptime(prev_dt, date_format)

    milliseconds = (obj.microsecond - prev_dt_obj.microsecond) # This is actually milliseconds offset

    return hex(milliseconds & 24)[2:]

def encode_version(vers):
    return hex(vers)[2:]

def encode_mem_data(mem_data):
    sb = ""

    for key, value in mem_data.items():
        sb += mem_key_table[key][2:]
        value = max(int(value), 0)
        value = min(value, (2 ** 16)-1)
        hex_value = hex(value)[2:]
        l = hex(len(str(value)))[2:]
        sb += l + hex_value

    return sb

def encode_mem_file(mem_file):
    lines = []
    with open(mem_file, "r") as f:
        for line in f.readlines():
            try:
                lines.append(json.loads(line))
            except:  # Potentially write failed..
                continue

    sb = ""
    sb += encode_version(VERSION)

    prev_date = list(lines[0].keys())[0]

    sb += encode_datetime(prev_date)

    for line in lines:
        date = list(line.keys())[0]
        sb += encode_milliseconds(date, prev_date)

        values = line[date]
        v = encode_mem_data(values)

        sb += v

    length = len(sb)
    if length % 2 != 0:
        sb = sb.zfill(length+1)

    return sb



def main():
    args = sys.argv[1:]
    if len(args) < 1 or len(args) > 3:
        print("Unsure how to parse!", file=sys.stderr)
        return

    filename = args[0]
    output_file = filename.replace(".json", ".mtc")
    if len(args) == 2:
        output_file = args[1]
        if not output_file.endswith(".mtc"):
            output_file += ".mtc"


    encoded = encode_mem_file(filename)

    with open(output_file, "wb") as f:
        f.write(bytes.fromhex(encoded))

    i_size = os.stat(filename).st_size
    o_size = os.stat(output_file).st_size
    print(f"Input file size: {i_size}\n")
    print(f"Output file size: {o_size}")
    print(f"Reduced by {100 - (round(o_size / i_size, 5) * 100)}%")



if __name__ == "__main__":
    with open("v1_encoding_key_map.json", "r") as f:
        mem_key_table = json.load(f)
    main()


