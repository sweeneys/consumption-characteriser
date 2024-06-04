# Author: Shaun Sweeney 
# Contact: shaunsweeney12@gmail.com
# Initial creation: June 2023

# Purpose: 
# This script is the executable for chracterising consumption as essential or flexible based on a known consumption dataset. The link to the file should be provided. 
# Some attributes relating to the consumption need to be assumed or modelled, such as their willingness to pay and how much of their consumption has been served in the past (i.e. their fairness score).
# Default values are provided for these, but it may also be of interest to test different initial conditions for these which can be turned off and on using the parameters (set_different_init_buy_prices, set_different_init_fairness)


import pandas as pd
import datetime as dt
import createInputDataFunctions as cIDF
import numpy as np
import matplotlib.pyplot as plt
import os
import request as rq
import neighbourParameters as nb
import consumptionappliance as conapp
import marketDesignFunctions as mdf
import pickle
import time
import random
import pricingFunctions
from datetime import datetime, timedelta



num_files=101 #101


dt_start_date = dt.datetime(2021, 11, 8)
dt_end_date = dt.datetime(2022, 11, 8)

# variables for inputs
num_neighbours = 101 #101
current_neighbour = 0
neighbours_consumption = []
neighbours_consumption_quantised=[]
neighbours_consumption_characterised=[]
neighbours_list=[]
neighbour_requests_list=[]

#flexibility scenarios - for each value provided below, a different request file will be generated
flexibility_levels = [0,1,2,3,6,9,12,24] #hours


#characterisation details
quantisation_level = 250 #quantise the data to 250W level incremenets
time_minimum = dt.timedelta(minutes=30)
sampling_period = 5*60 #our data is in 5 minute intervals
threshold_detector = time_minimum.seconds/sampling_period
power_minimum = 1000 #watts
convert_watts_to_kw=1e3

characterisation_parameters = {"quantisation_level":quantisation_level,
 "threshold_detector":threshold_detector,
 "power_minimum":power_minimum,
 "time_minimum":time_minimum}


set_different_init_buy_prices=True
set_different_init_fairness = True


def getMaxBuyPrice(pricing_function_parameters):
    pricing_function_parameters = pricingFunctions.linearPricingFunction() #We may wish to have different pricing functions in future
    max_buy_price = pricing_function_parameters.get("buy_price_y_intercept")

    return max_buy_price

def roundTime(dt, delta):
    return dt + (datetime.min - dt) % delta


def extract(lst):
    return [item[0] for item in lst]


#if graphs are being created
create_characterisation_graphs=False
if(create_characterisation_graphs):
    plot_start_date = '2022-01-04'
    plot_end_date = '2022-01-07'
    path = 'characterisation/'+plot_start_date + '-'+ plot_end_date + '/'
    if not os.path.exists(path):
        os.makedirs(path)



#Read in the data
while(current_neighbour < num_neighbours):
    filepath = 'Consumption only/consumptionOnly_N{}'.format(current_neighbour)+'.csv'
    print('neighbour file: ' + str(current_neighbour)+' read in')
    current_neighbour_consumption = pd.read_csv(filepath, index_col=0, parse_dates=True).squeeze("columns")
    neighbours_consumption.append(current_neighbour_consumption)

    current_neighbour+=1


#choose appropriate parameter values for pricing
pricing_function_parameters = pricingFunctions.linearPricingFunction() #We may wish to have different pricing functions in future
max_buy_price_feasible = 1000000
# getMaxBuyPrice(pricing_function_parameters)
max_buy_price_lower_lim_ratio=0.5


first_iter = True
high_init_buy_price=True
high_init_fairness = False
init_fairness = 0
current_fairness = init_fairness
fairness_difference=1.0/num_neighbours  
first_fairness_iter = True


for flexibility_level in flexibility_levels:
    print('flex level:' + str(flexibility_level))
    requests_to_process_queue=[]


    #Characterise the data (plot if necessary) and save it offline so it can be read in later
    for current_neighbour_id, current_neighbour_consumption in enumerate(neighbours_consumption):
        print('current_neighbour_id: '+str(current_neighbour_id))


        if((set_different_init_buy_prices == True) and (set_different_init_fairness==True)):
            if(high_init_buy_price==True):
                high_init_buy_price=False
                high_init_fairness=False
            elif(high_init_fairness==False):
                high_init_fairness=True
                high_init_buy_price=True



        if(first_iter==True):

            current_neighbour_consumption_characterised, current_neighbour_requests_list = cIDF.characteriseConsumption(dt_start_date, dt_end_date, current_neighbour_consumption,characterisation_parameters)

            neighbour_id = current_neighbour_id
            neighbour=[]

            products_list = mdf.getAvailableProductsList()

    
            #initial conditions for initial different fairness
            neighbourParameters = nb.UnlabelledNeighbourParameters(neighbour_id, products_list, max_buy_price_feasible, max_buy_price_lower_lim_ratio, set_different_init_buy_prices, high_init_buy_price, set_different_init_fairness, high_init_fairness, set_varying_init_fairness, current_fairness)
            neighbour.append(neighbourParameters)  

            #create csvs
            path='characterised/'
            current_neighbour_consumption_characterised.to_csv(path+'csvs/consumptioncharacterisation_n{}'.format(neighbour_id)+'.csv')

            neighbour_requests_list.append(current_neighbour_requests_list)

        if(create_characterisation_graphs):
            total_raw =  current_neighbour_consumption[plot_start_date: plot_end_date]
            total_quantised = current_neighbour_consumption_characterised['consumption'][plot_start_date: plot_end_date]
            baseload = current_neighbour_consumption_characterised['baseload'][plot_start_date: plot_end_date]
            potentially_flexible = current_neighbour_consumption_characterised['potentially flexible'][plot_start_date: plot_end_date]     
            assumed_flexible = current_neighbour_consumption_characterised['assumed flexible'][plot_start_date: plot_end_date]                                                    
            essential = current_neighbour_consumption_characterised['essential'][plot_start_date: plot_end_date]
            #create plots
            cIDF.plotAndSaveCharacterisationGraphs(path, neighbour_id, total_raw, total_quantised, baseload, potentially_flexible, assumed_flexible, essential)


        for request_to_process_id, request_to_process in enumerate(neighbour_requests_list[current_neighbour_id]):

            # we differentiate for the first iteration, because neighbour parameters only needs to be generated once per household, whereas the request file should be generated once for each flex level specified.
            if(first_iter!=True):
                neighbour_id = current_neighbour_id
                neighbour_parameters_only = extract(neighbours_list)
                current_neighbour_parameters = next((x for x in neighbour_parameters_only if x.id == neighbour_id), None)
     
   
            #generate time constraints for request with assumed flexibility level
            market_parameters = mdf.getDefaultMarketDesignParameters()
            earliest_start_time = roundTime(request_to_process.get("start_time") - dt.timedelta(hours=0.5*flexibility_level), market_parameters.get("market_resolution"))
            latest_end_time = roundTime(request_to_process.get("end_time") + dt.timedelta(hours=0.5*flexibility_level), market_parameters.get("market_resolution"))

            #need to calculate some parameters relating to the request
            duration_required = (request_to_process.get("end_time") - request_to_process.get("start_time")).round(freq=market_parameters.get("market_resolution"))
            
            #we do not want any requests longer than the length of a market window 
            if(duration_required >= market_parameters.get("market_window_length")): 
               duration_required = market_parameters.get("market_window_length") - market_parameters.get("market_resolution")
               print(duration_required)

            #edge case depending on rounding
            if((earliest_start_time + duration_required) > latest_end_time):
                latest_end_time = earliest_start_time + duration_required

            
            power_required = request_to_process.get("power")/convert_watts_to_kw

            ###
            appliance_id = request_to_process_id #we have unlabelled appliance data - so we assume each request belongs to an independent appliance
            consumption_appliance = conapp.UnlabelledConsumptionAppliance(appliance_id)
            neighbour.append(consumption_appliance)

   


            if(first_iter==True):
                request = rq.Request(neighbour_id=current_neighbour_id, appliance_id=appliance_id,
                    earliest_start_time=earliest_start_time, latest_end_time=latest_end_time,
                    power=power_required, duration=duration_required, max_buy_price=neighbour[0].max_buy_price, 
                    product=neighbour[0].product)

            else:
                request = rq.Request(neighbour_id=current_neighbour_id, appliance_id=appliance_id,
                    earliest_start_time=earliest_start_time, latest_end_time=latest_end_time,
                    power=power_required, duration=duration_required, max_buy_price=current_neighbour_parameters.max_buy_price, 
                    product=current_neighbour_parameters.product)

            
            requests_to_process_queue.append(request)

        
        neighbours_list.append(neighbour)    


    if(first_iter==True):        
        with open('files/eighbours'+str(int(time.time()))+'.pickle', 'wb') as handle:
            print('dumping a file')
            pickle.dump(neighbours_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
        

    with open('files/requests{}flexlevel'.format(flexibility_level)+str(int(time.time()))+'.pickle', 'wb') as handle:
        pickle.dump(requests_to_process_queue, handle, protocol=pickle.HIGHEST_PROTOCOL)

    first_iter = False










