# Author: Shaun Sweeney 
# Contact: shaunsweeney12@gmail.com
# Initial creation: June 2023

# Purpose: 
# This script contains helper functions used by the createInputData.py script

import pyarrow.parquet as pq
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import math


def custom_round(x, base):
    return int(base * round(float(x)/base))


def defineRequestDict(start_time, end_time, power):
        
    request_dict={
        "start_time": start_time,
        "end_time": end_time, 
        "power": power
    }

    return request_dict


def characteriseConsumption(dt_start_date, dt_end_date, current_neighbour_consumption, characterisation_parameters):
    convert_watts_to_kw=1e3
    
    current_neighbour_consumption.sort_index(inplace=True, ascending=True)
    current_neighbour_consumption = current_neighbour_consumption.dropna()
    current_neighbour_consumption = current_neighbour_consumption.interpolate()
    current_neighbour_consumption.name= 'consumption'
    current_neighbour_consumption_quantised = current_neighbour_consumption.apply(lambda x: custom_round(x, base=characterisation_parameters.get("quantisation_level")))


    current_neighbour_mode = current_neighbour_consumption_quantised[(current_neighbour_consumption_quantised != 0)].mode()[0]
    datetimeIndex = current_neighbour_consumption_quantised.index

    current_neighbour_consumption_characterised=pd.DataFrame(index = datetimeIndex)
    current_neighbour_consumption_characterised = current_neighbour_consumption_characterised.merge(current_neighbour_consumption_quantised.to_frame(), left_index=True, right_index=True)

    datetimeReindex = pd.date_range(start=dt_start_date, end=dt_end_date, freq='5Min')
    tempdf = current_neighbour_consumption_characterised.copy()
    tempdf = tempdf.tz_localize(None)
    tempdf = tempdf.reindex(datetimeReindex)

    current_neighbour_consumption_characterised = tempdf.copy()
    current_neighbour_consumption_characterised['baseload'] = np.minimum(current_neighbour_mode,current_neighbour_consumption_characterised['consumption'])
    current_neighbour_consumption_characterised['potentially flexible'] = current_neighbour_consumption_characterised['consumption'] - current_neighbour_consumption_characterised['baseload'] 
    current_neighbour_consumption_characterised['threshold'] = current_neighbour_consumption_characterised.groupby((current_neighbour_consumption_characterised['potentially flexible'] < characterisation_parameters.get("power_minimum")).cumsum()).cumcount()
    current_neighbour_consumption_characterised.loc[(current_neighbour_consumption_characterised['threshold'] >= characterisation_parameters.get("threshold_detector")) & (current_neighbour_consumption_characterised['consumption'].isnull()), 'threshold'] = 0 #detect missing data case
    request_thresholds_list = current_neighbour_consumption_characterised.index[current_neighbour_consumption_characterised['threshold']==characterisation_parameters.get("threshold_detector")].to_list()


    total_count = len(request_thresholds_list)
    current_count=0
    current_neighbour_requests_list=[]

    while current_count < total_count:
        #NOTE -> the below is so unreadable as there is some method to get the nearest index if the exact one doesn't exist: https://stackoverflow.com/questions/42264848/pandas-dataframe-how-to-query-the-closest-datetime-index
   
        start_time = current_neighbour_consumption_characterised.index[current_neighbour_consumption_characterised.index.get_indexer([pd.to_datetime(request_thresholds_list[current_count]-characterisation_parameters.get("time_minimum"))], method='nearest')[0]]

        #check if the event continues into the last row of the dataframe
        number_zeroes_after_start_time = len(current_neighbour_consumption_characterised.loc[current_neighbour_consumption_characterised.index > start_time].loc[current_neighbour_consumption_characterised['threshold']==0])
        if number_zeroes_after_start_time !=0:
            end_time = current_neighbour_consumption_characterised.index[current_neighbour_consumption_characterised.index.get_indexer([pd.to_datetime(current_neighbour_consumption_characterised.loc[current_neighbour_consumption_characterised.index > start_time].loc[current_neighbour_consumption_characterised['threshold']==0].iloc[0].name - dt.timedelta(minutes=5))], method='nearest')[0]]
        else:
            end_time = current_neighbour_consumption_characterised.iloc[-1].name

        power = current_neighbour_consumption_characterised['potentially flexible'].loc[start_time: end_time].mode().max()
        if(math.isnan(power)): ## this handles a specific missing data case
            print('power is nan')
            current_count+=1
            continue
        elif(power==0):
            current_count+=1
            continue
        else:
            request_parameters = defineRequestDict(start_time, end_time, power)
            current_neighbour_requests_list.append(request_parameters)
            current_count+=1

    
    current_neighbour_consumption_characterised['assumed flexible'] = 0 #initiate this to 0

    for request_id, request in enumerate(current_neighbour_requests_list):
        current_neighbour_consumption_characterised['assumed flexible'].loc[current_neighbour_requests_list[request_id].get("start_time"): current_neighbour_requests_list[request_id].get("end_time")] += current_neighbour_requests_list[request_id].get("power")

    current_neighbour_consumption_characterised['zeros'] = 0
    current_neighbour_consumption_characterised['essential'] = current_neighbour_consumption_characterised['baseload']
    current_neighbour_consumption_characterised['essential'] += np.maximum(current_neighbour_consumption_characterised['zeros'],current_neighbour_consumption_characterised['potentially flexible'] - current_neighbour_consumption_characterised['assumed flexible'])
    current_neighbour_consumption_characterised['essential'] = current_neighbour_consumption_characterised['essential']/convert_watts_to_kw

    return current_neighbour_consumption_characterised, current_neighbour_requests_list


def plotAndSaveCharacterisationGraphs(path, neighbour_id, total_raw, total_quantised, baseload, potentially_flexible, assumed_flexible, essential):

    ylim_max=np.max(total_quantised)

    fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(8, 8))

    fig.suptitle('Characterising essential and flexible consumption for neighbour {}'.format(neighbour_id))

    # subplot 1: Raw data 
    ax1.set_title('Total (raw)')
    ax1.plot(total_raw, label = 'total raw')
    ax1.legend
    ax1.tick_params(axis="both", rotation=45) 
    ax1.set_ylim([None, ylim_max])

    # subplot 2: Quantised total
    ax2.set_title('Total (quantised)')
    ax2.plot(total_quantised)
    ax2.tick_params(axis="both", rotation=45) 
    ax2.set_ylim([None, ylim_max])

    # subplot 3: Baseload
    ax3.set_title('Baseload')
    ax3.plot(baseload)
    ax3.tick_params(axis="both", rotation=45) 
    ax3.set_ylim([None, ylim_max])

    # subplot 4: Potentially flexible
    ax4.set_title('Potentially flexible')
    ax4.plot(potentially_flexible)
    ax4.tick_params(axis="both", rotation=45) 
    ax3.set_ylim([None, ylim_max])

    # subplot 5: Flexible
    ax5.set_title('Assumed flexible')
    ax5.plot(assumed_flexible)
    ax5.tick_params(axis="both", rotation=45) 
    ax5.set_ylim([None, ylim_max])

    # subplot 5: Flexible
    ax6.set_title('Assumed essential')
    ax6.plot(essential)
    ax6.tick_params(axis="both", rotation=45) 
    ax6.set_ylim([None, ylim_max])

    fig.tight_layout()

    fig.savefig(path+'consumptioncharacterisation_n{}'.format(neighbour_id)+'.png')

