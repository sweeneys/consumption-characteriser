# Author: Shaun Sweeney 
# Contact: shaunsweeney12@gmail.com
# Initial creation: December 2022

# Purpose: 

# This script defines two classes NeighbourParameters and UnlabelledNeighbourParameters which sets metadata relating to the household. 
# The difference between the classes is whether appliance consumption data for the household is labelled or not. 
# The difference is that if appliances are labeleld, the historic proportion of energy served can be associated directly with the appliance, rather than at the top level for the household. 
# This class is the top level within the hierarchy, and when it is invoked, a number of appliances are associated with it. Requests are then associated with appliances. 


import random
import numpy as np
import marketDesignFunctions as mDF
import pandas as pd


        
def createBaseload(baseload, num_daily_samples): #baseload consumption
    return baseload*np.ones(int(num_daily_samples))

def repeatDailyPattern(daily_pattern, simulation_days): 
    return np.tile(daily_pattern,simulation_days)

class NeighbourParameters:

    def __init__(self, neighbour_id, max_allowed_neighbour_baseload, max_allowed_number_flexible_appliances,
                 num_daily_samples, execution_days):   
        
        #create baseload for neighbour
        self.id=neighbour_id 
        self.neighbour_baseload = random.randint(0, max_allowed_neighbour_baseload)/1000 #convert watts to kw
        daily_baseload = createBaseload(self.neighbour_baseload, num_daily_samples) #note that baseload can represent essential consumption
        self.baseload = repeatDailyPattern(daily_baseload, execution_days)

        #max prices - this should be done at the application level
        self.maxBuyPrice = random.randint(0, 100000000) #max buy price for which willing to buy energy to use with appliance
        self.minSellPrice = random.randint(0, 1) #max sell price for which willing to sell energy from appliance
        
        #what prices do neighbours pay and earn for energy they consume and sell
        self.incurred_buy_price = np.zeros(int(num_daily_samples*execution_days)) #initial value
        self.earned_sell_price = np.zeros(int(num_daily_samples*execution_days)) #initial value
        
        #what is the incurred cost and revenue (price x volume)
        self.incurred_cost = np.zeros(int(num_daily_samples*execution_days)) #initial value
        self.earned_revenue = np.zeros(int(num_daily_samples*execution_days)) #initial value

        self.max_allowed_number_flexible_appliances = random.randint(1, max_allowed_number_flexible_appliances)



class UnlabelledNeighbourParameters:
        
    def __init__(self, neighbour_id, products_list, max_buy_price_feasible, max_buy_price_lower_lim_ratio, set_different_init_buy_prices, high_init_buy_price, set_different_init_fairness, high_init_fairness, set_varying_init_fairness, current_fairness):   
        
        self.id=neighbour_id 
        self.high_init_buy_price = high_init_buy_price
        self.high_init_fairness = high_init_fairness

        #no baseload is specified here as it is assumed that this comes from the provided dataset

        if(set_different_init_buy_prices == True) and (set_different_init_fairness==True):
            init_fairness_values_look_up_df = pd.read_csv('files/neighbour_init_energy_desired_2021_12_17.csv', index_col=0)

            if((high_init_buy_price==True) and (high_init_fairness==True)):
                self.max_buy_price = max_buy_price_feasible
                if(init_fairness_values_look_up_df.index.isin([neighbour_id]).any().any() and not pd.isna(neighbour_id)):
                    neighbour_day_one_energy = init_fairness_values_look_up_df.loc[neighbour_id][0]
                    self.fairness_time_series = [1.0]
                    self.total_historic_energy_delivered= neighbour_day_one_energy 
                    self.total_historic_energy_desired=neighbour_day_one_energy

            elif((high_init_buy_price==False) and (high_init_fairness==False)):
                self.max_buy_price = 1
                if(init_fairness_values_look_up_df.index.isin([neighbour_id]).any().any() and not pd.isna(neighbour_id)):
                    neighbour_day_one_energy = init_fairness_values_look_up_df.loc[neighbour_id][0]
                    self.fairness_time_series = [0]
                    self.total_historic_energy_delivered=0
                    self.total_historic_energy_desired=neighbour_day_one_energy

        else:
            self.max_buy_price = random.randint(int(max_buy_price_feasible*max_buy_price_lower_lim_ratio), max_buy_price_feasible) 
            self.fairness_time_series = [1.0]


        self.min_sell_price = random.randint(0, 1) #max sell price for which willing to sell energy from appliance
        self.product = random.choices(products_list, weights=(10,20), k=1)[0]
        self.productCost = mDF.getProductInfo(self.product).get('product_cost')
        self.productSuccess = mDF.getProductInfo(self.product).get('product_success')


    

        


