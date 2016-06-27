"""
Collect bus real time positions from OlhoVivo API and export the data to 
text files
"""
__author__ = "gbakie"

import configparser
import os
import sys
import pandas as pd
import numpy as np
import progressbar
import datetime
import logging
from time import sleep

from olhovivo_api import OlhoVivoAPI

DATA_DIR = '../data'
TIME_BETWEEN_REQS = 5
TIME_BETWEEN_UPDATES = 60 * 60 # 1 hour

def main():
    config_file = os.path.join(DATA_DIR, 'config.dat')
    config = configparser.ConfigParser()

    try:
        config.read(config_file)
        token = config['sptrans']['token']
    except Exception:
        print "Error reading config file"
        sys.exit(1)

    logging.basicConfig(filename='extract.log', level=logging.DEBUG)

    bus_info_df = pd.read_csv(os.path.join(DATA_DIR, "bus_info.txt"))
    buses_codes = bus_info_df['bus_code'].values

    while True:
        start = datetime.datetime.now()
        date_str = "%d-%02d-%02d" % (start.year, start.month, start.day)

        np.random.shuffle(buses_codes)
        pos_table = extract_positions(buses_codes, date_str, token)

        buses_pos_df = pd.DataFrame(data=pos_table, columns=["bus_code", "date_time",
                                                            "active", "bus_id", 
                                                            "latitute", "longitude"])
        #print buses_pos_df

        output_filename = "buses_position_%d_%02d_%02d_%02d_%02d.txt" % (start.year, 
                                                                        start.month, 
                                                                        start.day, 
                                                                        start.hour, 
                                                                        start.minute)

        buses_pos_df.to_csv(os.path.join(DATA_DIR, output_filename), index=False)

        end = datetime.datetime.now()

        time_dif = end - start
        if time_dif.total_seconds() < TIME_BETWEEN_UPDATES:
            time_sleep = TIME_BETWEEN_UPDATES - time_dif.total_seconds()
            print "Sleeping for %f seconds" % time_sleep
            sleep(time_sleep)


def extract_positions(buses_codes, date_str, token):
    api = OlhoVivoAPI(token)
    if not api.authenticate():
        print "Could not authenticate access"
        return 

    print "Extracting bus pos table from the API"
    bar = progressbar.ProgressBar(maxval=len(buses_codes)).start()
    buses_pos_table = []
    for i, bus_code in enumerate(buses_codes):
        pos = api.get_bus_pos(str(bus_code))
        if pos == None:
            break

        logging.debug(str(pos))

        if 'vs' not in pos or 'hr' not in pos:
            continue

        time = pos['hr']
        date_time = "%s %s" % (date_str, time)

        buses_pos = pos['vs'] 
        for bus_pos in buses_pos:
            active = bus_pos['a']
            bus_id = bus_pos['p']
            bus_lat = bus_pos['py']
            bus_lon = bus_pos['px']

            buses_pos_table.append([bus_code, date_time, active, 
                                    bus_id, bus_lat, bus_lon])

        # DEBUG
        #break
        bar.update(i+1)

        if i % 10 == 0:
            sleep(TIME_BETWEEN_REQS)

    bar.finish()

    return buses_pos_table

if __name__ == '__main__':
    main()
