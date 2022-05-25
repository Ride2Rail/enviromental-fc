#!/usr/bin/env python3
import os
import pathlib
import logging
import configparser as cp
import redis
import numpy as np
import json

from utils_environmental import *
from r2r_offer_utils  import normalization
from r2r_offer_utils  import cache_operations
from r2r_offer_utils.logging import setup_logger
from flask            import Flask, request


service_name = os.path.splitext(os.path.basename(__file__))[0]
#############################################################################
# init config
config = cp.ConfigParser()
config.read(f'{service_name}.conf')
#############################################################################
# init Flask
app          = Flask(service_name)
#############################################################################
# init cache
cache = redis.Redis(host=config.get('cache', 'host'),
                    port=config.get('cache', 'port'),
                    decode_responses=True)
#############################################################################
# init logging
logger, ch = setup_logger()

VERBOSE = int(str(pathlib.Path(config.get('running', 'verbose'))))
SCORES  = str(pathlib.Path(config.get('running',  'scores')))

#############################################################################
# A method listing out on the screen all keys that are in the cache.
@app.route('/test', methods=['POST'])
def test():
    data       = request.get_json()
    request_id = data['request_id']

    print("Listing cache.", flush=True)
    keys_sample = {}
    i = 0
    for key in cache.scan_iter():
        print(key, flush=True)
        keys_sample[i] = key
        i+=1
    return keys_sample;

    response   = app.response_class(
        response ='{{"request_id": "{}"}}'.format(request_id),
        status   =200,
        mimetype  ='application/json'
    )
    return response
#############################################################################
@app.route('/compute', methods=['POST'])
def extract():
    # import ipdb; ipdb.set_trace()
    data       = request.get_json()
    request_id = data['request_id']

    response   = app.response_class(
        response ='{{"request_id": "{}"}}'.format(request_id),
        status   =200,
        mimetype  ='application/json'
    )
    if VERBOSE== 1:
        print("______________________________", flush=True)
        print("environmental-fc start", flush=True)
        print("request_id = " + request_id, flush=True)
    #
    # extract data required by environmental-fc from cache
    #
    # Extraction of data required by environmental-fc feature collector from the cache. A     
    # dedicated procedure defined for this purpose in the unit "cache_operations.py" is utilized.

    try:
        output_offer_level, output_tripleg_level = cache_operations.read_data_from_cache_wrapper(
            cache,
            request_id,
            #["id","trip","bookable_total","complete_total","offer_items"],
            #["id","duration","start_time", "end_time","num_interchanges","legs"]
            ["num_interchanges"],
            ["start_time", "end_time","leg_stops","transportation_mode","number_of_persons_sharing_trip", "journey","duration","leg_track", "bike_on_board"]
            )
    except redis.exceptions.ConnectionError as exc:
        logging.debug("Reading from cache by environmental-fc feature collector failed.")
        response.status_code = 424
        return response

    if VERBOSE == 1:
        print("output_offer_level   = " + str(output_offer_level), flush=True)
        print("output_tripleg_level = " + str(output_tripleg_level), flush=True)
        
    #
    # II. compute values assigned to environmental-fc 
    #    

    res = collectENVFeatures({'output_offer_level': output_offer_level,'output_tripleg_level': output_tripleg_level}, SCORES = "minmax_scores")
    
    #
    # III. store the results produced by environmental-fc to cache
    #   
    try:
        cache_operations.store_simple_data_to_cache_wrapper(cache, request_id, res['total_co2_offer_norm'],
                                                            "total_co2_offer")
        cache_operations.store_simple_data_to_cache_wrapper(cache, request_id, res['co2_per_km_offer_norm'],
                                                            "co2_per_km_offer")
    except redis.exceptions.ConnectionError as exc:
        logging.debug("Writing outputs to cache by environmental-fc feature collector failed.")
   
    if VERBOSE == 1:
        print("environmental-fc end")
        print("______________________________")
    
    return res
#############################################################################

if __name__ == '__main__':
    import os

    FLASK_PORT = 5008
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    os.environ["FLASK_ENV"] = "development"
    cache        = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    app.run(port=FLASK_PORT, debug=True, use_reloader=False)
    exit(0)
