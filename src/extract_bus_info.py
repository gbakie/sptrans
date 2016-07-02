__author__ = "gbakie"

import configparser
import os
import sys
import pandas as pd
import numpy as np
import progressbar
from time import sleep

from olhovivo_api import OlhoVivoAPI

DATA_DIR = '../data'
TIME_BETWEEN_REQS = 1.

def main():
    config_file = os.path.join(DATA_DIR, 'config.dat')
    config = configparser.ConfigParser()

    try:
        config.read(config_file)
        token = config['sptrans']['token']
    except Exception:
        print "Error reading config file"
        sys.exit(1)

    api = OlhoVivoAPI(token)
    if not api.authenticate():
        print "Could not authenticate access"
        sys.exit(1)

    # read trip files from the GTFS and get unique routes
    trips_file = os.path.join(DATA_DIR, "trips.txt")
    trips = pd.read_csv(trips_file)
    route_ids = np.unique(trips.route_id.values)

    print "Extracting bus info table from the API"
    bar = progressbar.ProgressBar(maxval=len(route_ids)).start()

    bus_info_table = []
    for i, route_id in enumerate(route_ids):
        bar.update(i+1) 

        route_info = api.get_bus_info(route_id)
        if not route_info:
            print "Could not extract info for route_id: %s" % route_id
            continue
        for info in route_info:
            rec = [route_id, info['CodigoLinha'], info['Circular'], info['Sentido']]
            bus_info_table.append(rec)

        sleep(TIME_BETWEEN_REQS)
        # DEBUG
        #break

    bar.finish()
    
    # export to a new csv file, relating route_id to bus_code
    bus_info_df = pd.DataFrame(data=bus_info_table,
                            columns=["route_id", "bus_code", "circular", "direction"])
    bus_info_df.to_csv(os.path.join(DATA_DIR, "bus_info.txt"), index=False)

if __name__ == '__main__':
    main()
