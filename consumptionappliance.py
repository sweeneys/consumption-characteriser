# Author: Shaun Sweeney 
# Contact: shaunsweeney12@gmail.com
# Initial creation: December 2022

# Purpose: 

# This script defines:
# - A class for a spsecific known appliance (ConsumptionAppliance) which consumes electricity from the grid in a regular way. This class is most suited for use with simulating the performance of a consumption appliance between a start date and end date. 
# - A class type for an unknown appliance (UnlabelledConsumptionAppliance) which consumes electricity from the grid. This class is suited for working with consumption data where appliance consumption is unlabelled. 
# - A class for a specific labelled appliance (SimpleConsumptionAppliance) which consumes electricity from the grid. This class has not been developed yet and a future version of the code will include development of this. 

# The script is designed to be used in conjunction with the other scripts provided in the consumption-characteriser repo. 


import random
import request as rq
import numpy as np
import marketDesignFunctions as mDF
import datetime as dt
import pickle
import pandas as pd
import datetime as dt
import os


class ConsumptionAppliance:
    def __init__(self, start_time, end_time, neighbour_id, appliance_id, max_buy_price, msl, max_allowed_appliance_power, max_allowed_appliance_duration, time_series, products_list,first_neighbour):
        self.appliance_id = appliance_id

        num_seconds_day =24*60*60 
        market_resolution = 15*60 #15 minutes in seconds
        market_resolution_dt = dt.timedelta(seconds=market_resolution)
        num_daily_samples = num_seconds_day/market_resolution
        dt_time_series = pd.date_range(start=start_time, end=end_time, freq=market_resolution_dt)

        #create a time series for daily earliest start time
        earliest_daily_start_time = dt_time_series[random.randint(0, num_daily_samples-1)]
        
        #create a time series for latest end time
        latest_daily_end_time = dt_time_series[random.randint(0, num_daily_samples-1)]
        
        #adapt end time in case the request end time = request start time
        if(latest_daily_end_time == earliest_daily_start_time):
            latest_daily_end_time = earliest_daily_start_time - market_resolution_dt 
        
        #create the parameters of the appliance
        self.power_required = random.randint(1, max_allowed_appliance_power)
        self.duration_required = dt.timedelta(hours=random.randint(1, max_allowed_appliance_duration))
        
        #allocate a product to the appliance
        self.product = random.choice(products_list)
        self.productCost = mDF.getProductInfo(self.product).get('product_cost')
        self.productSuccess = mDF.getProductInfo(self.product).get('product_success')

        #store the fairness record for the appliance
        self.fairness_time_series = []
        self.total_historic_energy_delivered=0
        self.total_historic_energy_desired=0
        
        
        requests_to_process_queue=[]

        if(first_neighbour is True):
            try:
                os.remove("files/requests.pickle")
            except OSError:
                pass
            first_neighbour=False
        else:
            requests_to_process_queue = pd.read_pickle('files/requests.pickle')

        current_time = start_time
        iter=0
        while(current_time <= end_time):
            print('neighbour: ' + str(neighbour_id) + ' appliance_id ' + str(appliance_id) +', current time: '+str(current_time))

            request = rq.Request(neighbour_id=neighbour_id, appliance_id=appliance_id,
                                earliest_start_time=earliest_daily_start_time+iter*dt.timedelta(days=1), latest_end_time=latest_daily_end_time+dt.timedelta(days=1),
                                power=self.power_required, duration=self.duration_required, max_buy_price=max_buy_price, 
                                product=self.product)
            
            requests_to_process_queue.append(request)


            earliest_daily_start_time = earliest_daily_start_time + dt.timedelta(seconds=num_seconds_day)
            latest_daily_end_time = latest_daily_end_time + dt.timedelta(seconds=num_seconds_day)
            
            current_time += dt.timedelta(days=1)
            iter+=1


        #store all requests in file so they can be read in later
        with open('files/requests.pickle', 'wb') as handle:
            pickle.dump(requests_to_process_queue, handle, protocol=pickle.HIGHEST_PROTOCOL)


class UnlabelledConsumptionAppliance:
    def __init__(self, appliance_id):
        self.appliance_id = appliance_id

class SimpleConsumptionAppliance:
    def __init__(self, appliance_id):
        self.appliance_id = appliance_id
    
        
        
        