#%%
import os
from pathlib import Path
from pomato_data.pomato_data import PomatoData
import pandas as pd

#%%

if __name__ == "__main__":  

    settings = {
        "grid_zones": ["DE"],
        "future": True,     # create future scenario or data set for present
        "weather_year": 2019,
        # "capacity_year": 2030,
        "scenario": 'NEP_C_2030_ext_anymod',    # name of the csv file in folder data_out/extension containing overall installed power data
        "year": 2030,   # target year of data set
        "decommissioning": {"method":"linear",
                            "fuels":["lignite", "hard coal", "uran", "gas", "oil"],
                            "zones":["DE"]},
        "co2_price": 60,
        "split_lines": True,
        "time_horizon": "01.01.2019 - 31.12.2019",
        }
    
    if Path(os.path.abspath("")).name != "PomatoData":
        raise FileNotFoundError("Please Execute the script in the repository itself, use os.chdir() to change path")
    else: 
        wdir = Path(os.path.abspath(""))
        
    data = PomatoData(wdir, settings)

    # # %% DE Processing
    # data.add_dcline("nDK", "nSE", 2000)
    # data.create_basic_ntcs()

    # # Remove small plants below a certain threshold 
    # threshold = 1
    # data.plants[data.plants.g_max > threshold].g_max.sum() / data.plants.g_max.sum()  
    # len(data.plants[data.plants.g_max > threshold]) / len(data.plants[data.plants.g_max > 0])
    
    # data.plants = data.plants[data.plants.g_max > threshold]
    # drop_plants = [p for p in data.availability.columns if p not in data.plants.index]
    # data.availability = data.availability.drop(drop_plants, axis=1)
    
    
    # if settings["year"] == 2030:
    #     # Decommissioning (manual)

    #     condition_lignite = data.plants.fuel == "lignite"
    #     condition_coal = data.plants.fuel == "hard coal"
    #     condition_nuclear = data.plants.fuel == "uran"
    #     condition_gas= data.plants.fuel == "gas"
    #     condition_de = data.plants.zone == "DE"
    #     data.plants = data.plants.loc[~(condition_lignite & condition_de)]
    #     data.plants = data.plants.loc[~(condition_nuclear & condition_de)]
    #     data.plants.loc[(condition_gas & condition_de), "g_max"] *= 1.5
        
    #     data.plants.loc[(condition_nuclear|condition_coal|condition_lignite), "g_max"] *= 0.7
    
#%% Save data set
    foldername = f"DE_{settings['year']}"
    data.save_to_csv(foldername)
    
#%% Testing 
    # # availability = data.availability
    # demand = data.demand_el
    
    # dclines = data.dclines
    # lines = data.lines
    # nodes = data.nodes
    # plants = data.plants
    # zones = data.zones
    # ntc = data.ntc
    # technology = data.technology
    
    # plants_2020 = data.plants.copy()
    # # plants_2030 = data.plants.copy()
    # t = plants_2020[["fuel", "technology", "zone", "g_max"]].groupby(["fuel", "technology", "zone"]).sum().reset_index().fillna(0)
    # t = t.pivot(index="zone", columns=("fuel", "technology"), values="g_max")
    # t.plot.bar(stacked=True)


# %%
relative_path = 'data_out/extension/' + data.settings["scenario"] + '.csv'
scenario = pd.read_csv(data.wdir.joinpath(relative_path))
f= "lignite"
z = "DE"
print(scenario.loc[(scenario.group==f)&(scenario.country==z),"capaConv"].iat[0])
# %%
