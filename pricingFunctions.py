
# Author: Shaun Sweeney 
# Contact: shaunsweeney12@gmail.com
# Initial creation: December 2022

# Purpose: 

# This script is designed to enable users to specify parameters relating to pricing functions i.e. how much someone pays for their flexible consumption. 
# Currently this  contains a linear pricing function but this can easily be extended to other desired pricing functions. 

def linearPricingFunction():
    buy_price_slope=-2.65
    sell_price_slope=-2.65
    buy_price_y_intercept=265
    sell_price_y_intercept=0 

    pricing_function = dict({'buy_price_slope': buy_price_slope,
                        'sell_price_slope': sell_price_slope,
                        'buy_price_y_intercept':buy_price_y_intercept,
                        'sell_price_y_intercept':sell_price_y_intercept})
    

    return pricing_function