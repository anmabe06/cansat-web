import mysql.connector
import numpy as np
import extcolors

# Define the acceptable ranges for each parameter
RANGES = {
    "external_temperature": (10, 30),  # In Celsius
    "iaq": (0, 500),  # Indoor Air Quality Index  TODO: Check
    "pressure": (500, 1100),  # In hPa  TODO: Check
    "humidity": (50, 90),  # In percentage
    "bvoc": (0, 2000),  # In ppb  TODO: Check
    "co2": (100, 500),  # In ppm
    "uva_1": (0, 10),  # UV Index
}

# Function to check if a value is within the acceptable range
def is_in_range(value, param):
    min_value, max_value = RANGES[param]
    average = (min_value + max_value) / 2

    is_habitable = min_value <= value <= max_value
    if not is_habitable:
        return is_habitable, 0

    top_percentage_value = average - min_value
    if value > average:
        curret_value = max_value - value
    else:
        curret_value = value

    percentage = 100 * curret_value / top_percentage_value

    return is_habitable, percentage


# Connect to the database
db = mysql.connector.connect(
    host="qagi935.anmabe.es",
    user="qahu260",
    password="tZz5kw42sautFMbBozJ7uc38JNu4TKFkfJZyxAwJUpNTbUfXyx",
    database="qagi935"
)

cursor = db.cursor()

# Query the database for the environmental parameters
query = "SELECT external_temperature, iaq, pressure, humidity, bvoc, co2, uva_1 FROM cansat_data;"
cursor.execute(query)

# Check the data against the acceptable rang
sustains_life = True

percentages = []
wrong_values = {
    "external_temperature": 0,
    "iaq": 0,
    "pressure": 0,
    "humidity": 0,
    "bvoc": 0,
    "co2": 0,
    "uva_1": 0
}


for row in cursor:
    print(row)
    external_temperature, iaq, pressure, humidity, bvoc, co2, uva_1 = row

    params_variables = [external_temperature, iaq, pressure, humidity, bvoc, co2, uva_1]
    params_str = ["external_temperature", "iaq", "pressure", "humidity", "bvoc", "co2", "uva_1"]

    for idx in range(0, len(params_str)):
        is_habitable, percentage = is_in_range(params_variables[idx], params_str[idx])
        percentages.append(percentage)
        if not is_habitable:
            wrong_values[params_str[idx]] += 1

cursor.close()
db.close()

overall_habitability = np.mean(np.array(percentages))
if overall_habitability > 75:
    print(f"\033[92m" + "\033[1m" + f"[√] The overall percentage of habitability is {overall_habitability}" + "\033[0m")
elif overall_habitability > 50:
    print("\033[93m" + "\033[1m" + f"[~] The overall percentage of habitability is {overall_habitability}" + "\033[0m")
else:
    print("\033[91m" + "\033[1m" + f"[X] The overall percentage of habitability is {overall_habitability}" + "\033[0m")

for key, value in wrong_values.items():
    if value > 0:
        print("\033[91m" + "The value " + "\033[1m" + key + "\033[0m" + "\033[91m" + "has been found to deviate from the expected range of values " + "\033[1m" + value + "\033[0m\033[91m" + "time(s)" + "\033[0m")

