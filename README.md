---
header-includes:
  - \usepackage{algorithm2e}
---

# Algorithm 1
Just a sample algorithmn
\begin{algorithm}[H]
\DontPrintSemicolon
\SetAlgoLined
\KwResult{Write here the result}
\SetKwInOut{Input}{Input}\SetKwInOut{Output}{Output}
\Input{Write here the input}
\Output{Write here the output}
\BlankLine
\While{While condition}{
    instructions\;
    \eIf{condition}{
        instructions1\;
        instructions2\;
    }{
        instructions3\;
    }
}
\caption{While loop with If/Else condition}
\end{algorithm} 

# REPO DESCRIPTION / OBJECTIVE 

- The purpose of this repo is to take a dataset of electricity consumption and characterise the consumption as either essential or flexible based on a heuristic. The qualitative objectives of the characteriser are:

    (i) baseload consumption should be considered essential

    (ii) short spikes e.g. kettles should not be considered flexible and

    (iii) all other consumption larger in magnitude than $P_{threshold}$ for a duration $T_{threshold}$ should be considered flexible.

- The outputs of the characteriser are inputs for use in the online market described here [https://github.com/sweeneys/fair-flexible-energy-market]

- Further details on the market design are provided in [Link to paper to be proviedd]

  

# SCRIPT DESCRIPTIONS 

- createInputData.py: Main execution script in which to set configuration parameters

- createInputDataFunctions.py: Contains helper functions used by createInputData.py

- neighbourParameters.py: Class which defines metadata at the household level e.g. willingess to pay

- consumptionappliance.py: Class which defines metadata at the appliance level (different classes for datasets which either have appliance consumption labelled or unlabelled)

- request.py: Class for a request for consumption by flexible appliances

- marketDesignFunctions.py: Class which contains parameters relating to the market design in which the characterised consumption is intended to be used (these parameters can also be manually set but setting them in consideration to the specific market design ensures there is consistency with the market design in which the outputs are to be used).

- pricingFunctions.py: Defines the buy and sell pricing function for energy which may be useful in setting the willingness to pay parameters for each household.

- generateSimulatedConsumption.py: This is an alternative executable to createInputData.py for the case where the user does not have their own consumption dataset to characterise and they instead wish to generate some (simulated) consumption data.  
  
  

# INSTRUCTIONS 

1. Add the dataset you wish to characterise to the datasets/ folder, an example input dataset format is provided in exampleInputFile folder.

  
2. Within createInputData.py, set configuration parameters:

- Filepath to the dataset: there should be a separate consumption file for each household and the name should be formatted as 'consumptionOnly_N{}'

- power_minimum: Minimum amount of power in kW desired to consider consumption as flexible (note this is after subtracting the baseload consumption - which is identified by the characteriser).

- time_minimum: Minimum duration in minutes to consider consumption as flexible.

- quantisation_level: Consumption will be quantised to a common base

- flexibility_levels = [0,1,2,3,6,9,12,24]: these correspond with the assumed flexibility to associate with each household. A different set of requests is generated for each level given in the list (0 assumes 0 hours of flexibility, 3 assumes 3 hours of flexibility etc.).



*Note*: There are a number of other non-essential config options (high_init_buy_price, high_init_fairness, init_fairness) which are possible to set which change other configuration options relating to the inputs which may be interesting for running different types of experiment. By default, the willingness to pay (or max buy price) is set to be a random value over the interval from [0.5*BP_Max and BP_Max] where BP_Max is the maximum possible system price pricingFunctions.py.


3. Run the createInputData.py in a Python terminal
  
  

# OUTPUTS 

1. CSV file for each household containing consumption characterised as: consumption, baseload, potentially flexible, threshold, assumed flexible and essential. Note that the essential consumption is in kW while the other values are in Watts (no good reason for this, easy to change the other values to kW also).

2. neighbours{timestamp}.pickle: Contains metadata for each household (i.e. neighbourParameters.py and consumptionappliance.py) for all households.

3. requests{flexlevel}flexleve{timestamp}.pickle: Contains specific request objects for all households in one file, each request has parameters specified as in request.py.

4. (Optional) Figures: .png figures can be generated showing the characterised consumption as 6 x subplots to provide a visual sense check of how the characteriser has characterised the consumption.


Note that files 2 & 3 are linked together in the marketplace via neighbour ID. These are linked to file 1 using the neighbour ID included in the CSV filename.


# LICENSE
IP is owned by Shaun Sweeney and Imperial College London. This codebase is open-access can be freely used for experimentation or for other projects to be built on it. All work developed based on this should correctly acknowledge and cite the original author. 


# CONTACT
Contact shaunsweeney12@gmail.com


# ACKNOWLEDGMENTS
This work was developed as part of PhD research at Dyson School of Design Engineering, Imperial College London. 



 
