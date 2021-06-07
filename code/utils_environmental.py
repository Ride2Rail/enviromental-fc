import numpy as np 
import math
import json 
from typing import Mapping
import sys
# continuous_leg = ['walking', 'bike', 'car']
# timed_leg = ['train', 'taxi', 'change', 'bus', 'subway', 'tram', 'genericpubtrans', 'boat', 'funicular']
# ridesharing_leg = ['carsharing', 'bikesharing']

# CO2_DICT = {'walking' : 0 , 'bike' : 0 , 'car' : 180 , 'train': 40, 'taxi': 150, 'change' : 0 , 'bus' : 100 ,\
#      'subway' : 50, 'tram' : 50 , 'genericpubtrans' : 50 , 'boat' :20 , 'funicular' : 20}

def calculate_co2_total(mode, distance, occupancy = None):

    # mapping_modes = { 'walking'  :(0, 1),
    #     'bike' :  (0, 1),
    #     'car': (190,1.5),
    #     'train': (2184, 156),
    #     'taxi': (190,1.5), 
    #     'change' : (0, 1), 
    #     'bus' : (863, 12.7), 
    #     'subway': (193.44, 31), 
    #     'tram': (2184, 156), 
    #     'genericpubtrans': (1080 , 66), 
    #     'boat': (7425.6, 91), 
    #     'funicular': (2184, 156), 
    #     'carsharing': (190,1.5), 
    #       'bikesharing': (0, 1)}

    mapping_modes = { 'walk'  :(0, 1), 
          'cycle' :  (0, 1),
          'car': (190,1.5),
          'train': (2184, 156),
          'taxi': (190,1.5), 
          'change' : (0, 1), 
          'bus' : (863, 12.7), 
          'urbanRail': (193.44, 31), 
          'tram': (2184, 156), 
          'genericpubtrans': (1080 , 66), 
          'boat': (7425.6, 91), 
          'funicular': (2184, 156), 
          'carsharing': (190,1.5), 
          'bikesharing': (0, 1)}

    map_tMode = mapping_modes[mode]


    if occupancy is not None:
        return map_tMode[0]*distance/occupancy

    return map_tMode[0]*distance/map_tMode[1]


def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.    

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    if not isinstance(km, np.ndarray):
        return float(km*1000)

    return km*1000


def get_distance_from_path(data):
    ''' 
    leg level input. (leg_stops, leg_track)

    '''
    if data['leg_track'] is not None:
        temp_path  = data['leg_track']['coordinates']
        new_path = list(zip(temp_path[:-1], temp_path[1:]))
        new_path  = np.array(new_path).reshape(len(temp_path) - 1,4)
        tl = new_path.shape[0]
        new_path = new_path.reshape(tl, 4)
        return float((haversine_np(new_path[:,0], new_path[:,1], new_path[:,2], new_path[:,3]).sum()))

    else: 
        origin_lat, origin_lon = data['leg_stops']['coordinates'][0][0], \
                data['leg_stops']['coordinates'][0][1] 

        dest_lat, dest_lon = data['leg_stops']['coordinates'][1][0], \
            data['leg_stops']['coordinates'][1][1]

        return haversine_np(origin_lon, origin_lat, dest_lon, dest_lat)


def zscore(offers: Mapping, flipped = False) -> Mapping:
    n          = 0
    sum        = 0.0
    sum_square = 0.0

    for o in offers:
        value = offers[o]
        if value is not None:
            n = n + 1
            sum = sum + value
            sum_square = sum_square + value*value

    z_scores = {}
    if n > 0:
        average = sum / n
        std = math.sqrt(sum_square / n - average * average)
        for o in offers:
            value = offers[o]
            if value is not None:
                if std == 0:
                    z_scores[o] = 0
                else:
                    if not flipped:
                        z_scores[o] = (value - average)/std
                    else:
                        z_scores[o] = 1 - (value - average) / std
    return z_scores


def minmaxscore(offers: Mapping, flipped = False) -> Mapping:

    min = sys.float_info.max
    max = sys.float_info.min
    n   = 0
    for o in offers:
        value = offers[o]
        if value is not None:
            n = n + 1
            if value > max:
                max = value
            if value < min:
                min = value

    minmax_scores = {}
    diff = max - min
    if (n > 0):
        for o in offers:
            value = offers[o]
            if value is not None:
                if(diff > 0):
                    if not flipped:
                        minmax_scores[o] = (value-min)/diff
                    else:
                        minmax_scores[o] = 1 - (value-min)/diff
                else:
                    minmax_scores[o] = 0.5
    return minmax_scores

def co2_per_km(data):

    temp_legs = data['triplegs'] #list of legs

    total_dist = 0 
    total_co2_per_km_legs = []
    leg_dist = []
    total_co2 = 0 

    for leg in temp_legs:
        one_leg  = data[leg]
        #take coords...
        # origin_lat, origin_lon = one_leg['leg_stops']['coordinates'][0][0], \
        #     one_leg['leg_stops']['coordinates'][0][1] 
        # dest_lat, dest_lon = one_leg['leg_stops']['coordinates'][1][0], \
        #     one_leg['leg_stops']['coordinates'][1][1]

        # temp_dist = haversine_np(origin_lon, origin_lat, dest_lon, dest_lat)/1000
        temp_dist = get_distance_from_path(one_leg)/1000
        tMode = one_leg['transportation_mode']
        print(tMode, ' : ', temp_dist)
        if one_leg['number_of_persons_sharing_trip'] is not None:

            temp_co2_leg = calculate_co2_total(mode= tMode, distance=temp_dist, occupancy= one_leg['number_of_persons_sharing_trip'])
            print( '----', temp_co2_leg , '----')

        else: 
            temp_co2_leg = calculate_co2_total(mode= tMode, distance=temp_dist)
            print( '----', temp_co2_leg , '----')
    
        total_dist += temp_dist 

        total_co2 += temp_co2_leg 

        total_co2_per_km_legs.append(temp_co2_leg)

        leg_dist.append(temp_dist)
    print('-----------------')
    weight_co2_per_km = np.average(total_co2_per_km_legs, weights = leg_dist )

    return float(total_co2), float(weight_co2_per_km)
    
def transformStringToNum (data): 

    offer_keys = data['output_offer_level']['offer_ids']

    for offer in offer_keys: 

        trip_legs  = data['output_tripleg_level'][offer]['triplegs']

        data['output_offer_level'][offer]['num_interchanges'] = \
            int(data['output_offer_level'][offer]['num_interchanges'])

        for leg in trip_legs:
            data['output_tripleg_level'][offer][leg]['leg_stops'] = \
                json.loads(data['output_tripleg_level'][offer][leg]['leg_stops'])
            try:
                data['output_tripleg_level'][offer][leg]['leg_track'] = \
                    json.loads(data['output_tripleg_level'][offer][leg]['leg_track'])
            except:
                pass
    return data

def collectENVFeatures( data , SCORES = "minmax_scores"):      
     data2 = transformStringToNum(data)
     
     data = data2['output_tripleg_level']
     offer_keys = list(data.keys())

     total_co2_offer, co2_per_km_offer = {},{}
     for one_offer in  offer_keys:
          temp_offer = data[one_offer] 

          total_co2_offer[one_offer] ,  co2_per_km_offer[one_offer] = co2_per_km(temp_offer)


     if SCORES == "minmax_scores":

        total_co2_offer_norm = minmaxscore(total_co2_offer)
        
        co2_per_km_offer_norm = minmaxscore(co2_per_km_offer)

     else:

        total_co2_offer_norm = zscore(total_co2_offer)
        
        co2_per_km_offer_norm = zscore(co2_per_km_offer)

     return {'total_co2_offer' : total_co2_offer, 'co2_per_km_offer' : co2_per_km_offer, 
          'total_co2_offer_norm': total_co2_offer_norm, 'co2_per_km_offer_norm' : co2_per_km_offer_norm}
