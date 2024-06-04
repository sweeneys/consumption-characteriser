# Author: Shaun Sweeney 
# Contact: shaunsweeney12@gmail.com
# Initial creation: December 2022

# Purpose: 
# - This script is used to generate consumption data for a set of households by assuming certain parameters about them.
# - The consumption patterns are assumed to be regular/periodic, but it is easily possible to extend the code to take account of other types of consumption pattern or to add noise. 


import random
import numpy as np
import neighbourParameters as nb
import consumptionappliance as conapp
import request as req
import datetime as dt
import pickle
import marketDesignFunctions as mdf


def generateSimulatedConsumption(start_time, end_time, total_simulation_neighbours=10, max_allowed_neighbour_baseload=20, max_allowed_appliance_consumption=7, max_allowed_appliance_production=7,
                                 max_allowed_appliance_duration=5,
                                 max_allowed_number_flexible_appliances=3, products_list=['premium', 'basic']):

    max_allowed_number_flexible_appliances = 3
    neighbour_id = 0
    neighbours_list=[]
    current_neighbour=1
    simulated_bool=True
    num_seconds_day = 24*60*60 
    market_resolution = 30*60 #15 minutes in seconds
    num_daily_samples = num_seconds_day/market_resolution
    simulation_days = (end_time - start_time).days 
    num_simulation_samples = num_daily_samples*simulation_days
    time_series= np.arange(0, market_resolution*num_daily_samples*simulation_days, market_resolution)

    first_neighbour = True
    while current_neighbour < (total_simulation_neighbours+1):
        
        neighbour = []
        #initialise neighbour object
        neighbourParameters = nb.NeighbourParameters(neighbour_id, max_allowed_neighbour_baseload, max_allowed_number_flexible_appliances, 
                                                     num_daily_samples, simulation_days)
        neighbour.append(neighbourParameters)      

        #consumption appliances that will need to be flexible
        appliance_id=1
        while appliance_id <= neighbour[0].max_allowed_number_flexible_appliances:


            consumption_appliance = conapp.ConsumptionAppliance(start_time=start_time, end_time=end_time, neighbour_id=neighbourParameters.id, appliance_id=appliance_id, 
                                                                max_buy_price=neighbourParameters.max_buy_price, msl=neighbourParameters.msl, 
                                                                max_allowed_appliance_power=max_allowed_appliance_consumption, max_allowed_appliance_duration=max_allowed_appliance_duration, 
                                                                time_series=time_series, products_list=products_list, first_neighbour=first_neighbour)

            neighbour.append(consumption_appliance)

            if(neighbour_id==0 and appliance_id==1):
                first_neighbour=False
            appliance_id+=1


        #add completely initialised neighbour to list of neighbours
        neighbours_list.append(neighbour)
        
        neighbour_id+=1
        current_neighbour+=1


    with open('files/neighbours.pickle', 'wb') as handle:
        pickle.dump(neighbours_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
   

##### INITIALISE NEIGHBOURS ##########

if __name__ == '__main__':
    neighbours_list=[]
    total_simulation_neighbours = 10
    max_allowed_neighbour_baseload = 2 #2kW assumed to be max baseload (feasible)
    max_allowed_appliance_production = 7 #7kW assumed max peak of production (feasible for residential solar panels)
    max_allowed_appliance_consumption = 7 #7kW assumed to be max power output of appliance (feasible for EV charger)
    max_allowed_number_flexible_appliances = 3
    max_allowed_appliance_duration = 5
    products_list = mdf.getAvailableProductsList()
    start_time = dt.datetime(2021, 12, 1)
    end_time = dt.datetime(2021, 12, 6)
    execution_times = {"start_time", start_time,
                        "end_time", end_time, }
    

    generateSimulatedConsumption(start_time, end_time, total_simulation_neighbours, max_allowed_neighbour_baseload, 
                                       max_allowed_appliance_consumption, max_allowed_appliance_production, max_allowed_appliance_duration, max_allowed_number_flexible_appliances, products_list)
    
    print('Done')
    




    
    