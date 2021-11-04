#%%
import os
from pathlib import Path
from pomato_data.pomato_data import PomatoData
import pandas as pd

from pomato_data.res import capacities

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

# %% DE Processing
    data.add_dcline("nDK", "nSE", 2000)

    # Remove small plants below a certain threshold 
    threshold = 1
    data.plants[data.plants.g_max > threshold].g_max.sum() / data.plants.g_max.sum()  
    len(data.plants[data.plants.g_max > threshold]) / len(data.plants[data.plants.g_max > 0])
    
    data.plants = data.plants[data.plants.g_max > threshold]
    drop_plants = [p for p in data.availability.columns if p not in data.plants.index]
    data.availability = data.availability.drop(drop_plants, axis=1)
    
    
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
# wdir = Path(os.path.abspath(""))
# from pomato_data.res import get_potentials_ffe

# wind_potentials, pv_rooftop_potentials, pv_park_potentials = get_potentials_ffe()
# wind_potentials.to_csv(wdir.joinpath('data_out/res_potential/wind_potential.csv'))
# # pv_potentials.to_csv(wdir.joinpath('data_out/res_potential/pv_potential.csv'))
# pv_rooftop_potentials.to_csv(wdir.joinpath('data_out/res_potential/pv_rooftop_potential.csv'))
# pv_park_potentials.to_csv(wdir.joinpath('data_out/res_potential/pv_park_potential.csv'))

# %% Testbench pv technologies
from pomato_data.res.capacities import read_in_res_potentials, load_installed_res_capacities
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

rooftop_share = 0.7
potentials = read_in_res_potentials(wdir, res_technologies = ["solar rooftop", "solar park", "wind onshore"])
installed_capacities = load_installed_res_capacities(wdir, settings["scenario"])
capacities = potentials.copy()
potential_keys = list(potentials.keys()) 
countries = [c for c in capacities[potential_keys[0]].country.unique() if c in installed_capacities.index]

for k in potential_keys:
    capacities[k]["relative_potential"] = 1 
    capacities[k]["capacity"] = 0

for c in countries:
    for k in potential_keys:
        if 'solar' in installed_capacities.loc[c, "capaConv"].index.to_list():
            installed_capacities.loc[(c, 'solar rooftop'), "capaConv"] = installed_capacities.loc[(c, 'solar'), "capaConv"]*rooftop_share
            installed_capacities.loc[(c, 'solar park'), "capaConv"] = installed_capacities.loc[(c, 'solar'), "capaConv"]*(1-rooftop_share)
        capacities[k].loc[capacities[k].country == c, "relative_potential"] = potentials[k].loc[potentials[k].country == c, "value"]/potentials[k].loc[potentials[k].country == c, "value"].sum()   
        if c in installed_capacities.xs(k, level=1).index:
            capacities[k].loc[capacities[k].country == c, "capacity"] = capacities[k].loc[capacities[k].country == c, "relative_potential"]*installed_capacities.loc[(c, k), "capaConv"]*1000
        else:
            capacities[k].loc[capacities[k].country == c, "capacity"] = 0
    # 
    # wind_capacities.loc[wind_capacities.country == c, "relative_potential"] = wind_potentials.loc[wind_potentials.country == c, "value"]/wind_potentials.loc[wind_potentials.country == c, "value"].sum()
    # if c in installed_capacities.xs("wind onshore", level=1).index:
    #     wind_capacities.loc[wind_capacities.country == c, "capacity"] = wind_capacities.loc[wind_capacities.country == c, "relative_potential"]*installed_capacities.loc[(c, "wind onshore"), "capaConv"]*1000
    # else:
    #     wind_capacities.loc[wind_capacities.country == c, "capacity"] = 0
    
    # pv_capacities.loc[pv_capacities.country == c, "relative_potential"] = pv_potentials.loc[pv_potentials.country == c, "value"]/pv_potentials.loc[pv_potentials.country == c, "value"].sum()
    # if c in installed_capacities.xs("solar", level=1).index:
    #     pv_capacities.loc[pv_capacities.country == c, "capacity"] = pv_capacities.loc[pv_capacities.country == c, "relative_potential"]*installed_capacities.loc[(c, "solar"), "capaConv"]*1000
    # else:
    #     pv_capacities.loc[pv_capacities.country == c, "capacity"] = 0

# %%
technology = pd.read_csv(wdir.joinpath("data_out/technology/technology.csv"), index_col=0)
# %%
t = 'solar rooftop'
technology.loc[technology["technology"] == t,"fuel"].iat[0] + "/" + t
# %%
