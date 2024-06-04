# Author: Shaun Sweeney 
# Contact: shaunsweeney12@gmail.com
# Initial creation: December 2022

# Purpose: 

# This script defines a class (Request) which encapsulates a desire to consume energy between a specific start time and end time. 
# The request enables some window (or time flexibility) to be defined. Some attributes have values set on creation and others are set whasen the request is being processed.
# The script is designed to be used in conjunction with the other scripts provided in the consumption-characteriser repo. 


class Request:
    def __init__(self, neighbour_id, appliance_id, earliest_start_time, latest_end_time, power, duration, max_buy_price, product):
        num_seconds_hour=60*60
        self.id=""+str(neighbour_id) + str(appliance_id) + str(earliest_start_time)
        self.neighbour_id=neighbour_id
        self.appliance_id=appliance_id
        self.earliest_start_time = earliest_start_time
        self.latest_end_time = latest_end_time
        self.power = power
        self.duration = duration
        self.max_buy_price = max_buy_price
        self.product = product
        self.fairness = 1 
        self.total_energy_delivered = 0
        self.total_energy_desired = self.power*self.duration.seconds/num_seconds_hour
        self.iter = 0 #store which iteration the request is on for updating fairness metric
        self.accepted=False
        self.accepted_start_time=None
        self.accepted_end_time=None
        self.queue_position=None
        self.cost=None
        self.temp_prob_success=None #we will use this as part of normalising probability of success of each request
        self.try_to_satisfy_request=None
        self.ever_tried_to_satisfy_request = False 
        self.feasible_to_satisfy_request_this_iter = None
        self.updated_energy_desired = False #we will use this to ensure that if the same request is rejected multiple times that it does not affect fairness multiple times
        