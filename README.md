# Feature collector "environmental-fc"
***Version:*** 1.0

***Date:*** 03.06.2021

***Authors:***  [Zisis Maleas](https://github.com/zisismaleas); [Panagiotis Tzenos](https://github.com/ptzenos)

***Address:*** The Hellenic Institute of Transport (HIT), Centre for Research and Technology Hellas (CERTH)

# Description 

The "environmental-fc" feature collector is  a module of the **Ride2Rail Offer Categorizer** responsible for the computation of the determinant factors: ***"total_co2_offer"***, ***"co2_per_km_offer"***, 
, ***"total_co2_offer_norm"***, ***"co2_per_km_offer_norm"***. 

***"total_co2_offer"***, ***"total_co2_offer_norm"*** : The total gCO2 this offer cause.  
***"co2_per_km_offer"*** ,  ***"co2_per_km_offer_norm"***: The total gCO2 this offer cause weighted by the distance of each left. 


Computation can be executed from ***["environmental.py"](https://github.com/Ride2Rail/environmental-fc/blob/main/environmental.py)*** by running the procedure ***extract()*** which is binded under the name ***compute*** with URL using ***[FLASK](https://flask.palletsprojects.com)*** (see example request below).  Computation is composed of three phases (***Phase I:***, ***Phase II:***, and  ***Phase III:***) in the same way the ***(https://github.com/Ride2Rail/tsp-fc)*** use it.

# Configuration

The following values of parameters can be defined in the configuration file ***"environmental.conf"***.

Section ***"running"***:
- ***"verbose"*** - if value __"1"__ is used, then feature collector is run in the verbose mode,
- ***"scores"*** - if  value __"minmax_score"__ is used, the minmax approach is used for normalization of weights, otherwise, the __"z-score"__ approach is used. 

Section ***"cache"***: 
- ***"host"*** - host address where the cache service that should be accessed by ***"environmental-fc"*** feature collector is available
- ***"port"*** - port number where the cache service that should be accessed used by ***"environmental-fc"*** feature collector is available

**Example of the configuration file** ***"environmental.conf"***:
```bash
[service]
name = environmental
type = feature collector
developed_by = Zisis Maleas <https://github.com/zisismaleas> and Panagiotis Tzenos <https://github.com/ptzenos>

[running]
verbose = 1
scores  = minmax_scores

[cache]
host = cache
port = 6379
```

# Usage
### Local development (debug on)

The feature collector "environmental-fc" can be launched from the terminal locally by running the script "environmental.py":

```bash
$ python3 environmental.py
 * Serving Flask app "environmental" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN:
```

The repository contains also configuration files required to launch the feature collector in Docker from the terminal by the command docker-compose up:

```bash
docker-compose up
Starting environmental_fc ... done
Attaching to environmental_fc
active_fc    |  * Serving Flask app "environmental.py" (lazy loading)
active_fc    |  * Environment: development
active_fc    |  * Debug mode: on
active_fc    |  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
active_fc    |  * Restarting with stat
active_fc    |  * Debugger is active!
active_fc    |  * Debugger PIN: 
```

### Example Request
To make a request (i.e. to calculate values of determinant factors assigned to the "environmental-fc" feature collector for a given mobility request defined by a request_id) the command curl can be used:
```bash
$ curl --header 'Content-Type: application/json' \
       --request POST  \
       --data '{"request_id": "123x" }' \
         http://localhost:5005/compute
```
