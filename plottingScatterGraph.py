import json
import matplotlib.pyplot as plt
import numpy as np


def parse_json(json_data):
    data_types = {
        "timestamp": int,
        "imu": {
            "accel": list,
            "gyro": list
        },
        "dht": {
            "temp": list,
            "humidity": list
        },
        "bme": {
            "temp": list,
            "humidity": list,
            "pressure": list,
            "voc": {
                "ppm": float,
                "airQuality": int,
                "heaterTemp": int
            }
        },
        "windSpeed": int,
        "gps": {
            "absoluteTimestamp": int,
            "latitude": float,
            "longitude": float,
            "altitude": int,
            "bearing": int,
            "speed": int,
            "satellites": int,
            "fix": int,
            "quality": int
        },
        "computed": {
            "hasLanded": bool,
            "hasReachedTerminal": bool
        }
    }

    parsed_data = {}

    def parse_recursive(json_obj, data_type):
        if isinstance(data_type, dict):
            result = {}
            for key, value in data_type.items():
                result[key] = parse_recursive(json_obj.get(key, {}), value)
            return result
        elif isinstance(data_type, list):
            return [parse_recursive(item, data_type[0]) for item in json_obj]
        else:
            return data_type(json_obj) if json_obj is not None else None

    parsed_data = parse_recursive(json_data, data_types)
    return parsed_data

# Example usage

f = open("package.json")
json_data = json.load(f)
parsed_data = parse_json(json_data)

plt.scatter(parsed_data["imu"]["accel"], parsed_data["imu"]["gyro"])
plt.show()