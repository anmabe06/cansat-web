import datetime
import random

for i in range(10):
    statement = f'''INSERT into cansat.cansat_data 
                    (time, latitude, longitude, altitude, course, horizontal_speed, x_rotation, y_rotation, internal_temperature_1, internal_temperature_2, external_temperature, iaq, pressure, humidity, bvoc, co2, uva_1, uva_2, beta_particles, satellites_connected) 
                    VALUES(
                    '{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}',
                    {random.randint(30, 50)},
                    {random.randint(60, 150)},
                    {random.randint(575, 700)},
                    {0},
                    {random.randint(9, 10)},
                    {random.randint(0, 359)},
                    {random.randint(0, 359)},
                    {random.randint(28, 30)}.{random.randint(0, 9)},
                    {random.randint(28, 30)}.{random.randint(0, 9)},
                    {random.randint(15, 25)}.{random.randint(0, 9)},
                    {0},
                    {random.randint(101000, 102000)},
                    {random.randint(40, 100)},
                    {0},
                    0.{random.randint(0, 6000)},
                    {0},
                    {0},
                    {0},
                    {5});'''
    print(statement)