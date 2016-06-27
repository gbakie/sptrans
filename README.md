# sptrans
Extract Sao Paulo bus data using olhovivo API

To access OlhoVivo API you need to sign up for a token at http://www.sptrans.com.br/desenvolvedores/APIOlhoVivo.aspx. The token has to be put at the config file on the data directory.

Before running the code, you have to download the GTFS - General Transit Feed Specification, available at the same website. Its content should be extracted at the data directory.

extract_bus_info.py - using the data from the GTFS, extract the bus ids for all the existing routes.

collect_bus_positions.py - using the bus ids, collect real time position data of the buses.
