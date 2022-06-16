#%%
import os
import numpy as np
from pathlib import Path
from pomato_data.pomato_data import PomatoData
import pandas as pd

from pomato_data.res import capacities

#%%

settings = {
    "grid_zones": ["DE"],
    "future": True,     # create future scenario or data set for present
    "weather_year": 2019,
    "scenario": '2022_energy_charts',    # name of the csv file in folder data_out/extension containing overall installed power data
    "year": 2022,   # target year of data set
    # "decommissioning": {"method":"linear",
    #                     "fuels":["lignite", "hard coal", "uran", "gas", "oil"],
    #                     "zones":["DE"]},
    "co2_price": 75,
    "split_lines": True,
    "time_horizon": "01.01.2019 - 01.01.2020", 
    }

if Path(os.path.abspath("")).name != "PomatoData":
    raise FileNotFoundError("Please Execute the script in the repository itself, use os.chdir() to change path")
else: 
    wdir = Path(os.path.abspath(""))

# %%       
data = PomatoData(wdir, settings)

# # %% Data tests
# stor = data.storage_level.pivot(index="timestep", columns="plant", values="storage_level")

# %% 
# t_start = settings["time_horizon"].split(" - ")[0]
# t_end = settings["time_horizon"].split(" - ")[1]
# timesteps = pd.date_range(t_start, t_end, freq='168H').values
# timesteps[1:] = timesteps[1:] - pd.Timedelta(value=1, unit="hours")

# # %%
# year = 2019
# storage_level = pd.read_csv(data.wdir.joinpath(f'data_out/hydro/storage_level_{year}.csv'), index_col=0)
# storage_level = storage_level.reset_index(drop=True)
# start = pd.to_datetime(storage_level["utc_timestamp"].iloc[1])
# storage_level.utc_timestamp = pd.to_datetime(storage_level.utc_timestamp).astype('datetime64[ns]') + pd.Timedelta(value=23, unit="hours")
# storage_level.loc[1,"utc_timestamp"] = start

# # %%
# plants = data.plants
# demand = data.demand_el
# t_start = data.settings["time_horizon"].split(" - ")[0]
# t_end = data.settings["time_horizon"].split(" - ")[1]
# timesteps = pd.date_range(t_start, t_end, freq='168H').tolist()
# timesteps[1:] = [t - pd.Timedelta(value=1, unit="hours") for t in timesteps[1:]]
# timesteps.append(pd.Timestamp(t_end) - pd.Timedelta(value=1, unit="hours"))
# timestep_index = demand.loc[demand.utc_timestamp.isin(timesteps), "utc_timestamp"]

# # %% 

# storage_level_battery = pd.DataFrame()
# for ind, p in plants.loc[plants.technology=="solar battery"].iterrows():
#     tmp_level = pd.DataFrame(index=timestep_index.index)
#     tmp_level["plant"] = ind
#     tmp_level["storage_level"] = 0
#     storage_level_battery = pd.concat([storage_level_battery, tmp_level])

# %% DE Processing
data.add_dcline("nDK", "nSE", 2000)

# Remove small plants below a certain threshold 
threshold = 5
data.plants[data.plants.g_max > threshold].g_max.sum() / data.plants.g_max.sum()  
len(data.plants[data.plants.g_max > threshold]) / len(data.plants[data.plants.g_max > 0])

data.plants = data.plants[data.plants.g_max > threshold]
drop_plants = [p for p in data.availability.columns if p not in data.plants.index]
data.availability = data.availability.drop(drop_plants, axis=1)
    
#%% Save data set
foldername = f"DE_gas200euros_{settings['year']}"
data.save_to_csv(foldername)

#%% Data checks
# data.plants[data.plants.technology=="solar battery"].storage_capacity.sum() 

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

# %% Workbench NTCs
import itertools
commercial_exchange=True
# from physical cross border flows
year = data.settings["weather_year"]
if commercial_exchange:
    exchange = pd.read_csv(data.wdir.joinpath(f'data_out/exchange/commercial_exchange_{year}.csv'), index_col=0)
else:
    exchange = pd.read_csv(data.wdir.joinpath(f'data_out/exchange/physical_crossborder_flow_{year}.csv'), index_col=0)

exchange.utc_timestep = pd.to_datetime(exchange.utc_timestep).astype('datetime64[ns]')
ntc = pd.DataFrame(index=pd.MultiIndex.from_tuples([(f,t) for (f,t) in itertools.permutations(list(data.zones.index), 2)]))

# %%
max_flow = exchange.groupby(["from_zone", "to_zone"]).quantile(0.85).reset_index()
ntc["ntc"] = 0
# %%
for (f,t) in ntc.index:
    ntc.loc[(f,t), "ntc"] = max_flow.loc[(max_flow.from_zone == f) & (max_flow.to_zone == t), "value"].max()

# %%        
ntc = ntc.reset_index().fillna(0)
ntc.columns = ["zone_i", "zone_j", "ntc"]
# %% 
# Set NTC to zero if no physical connection exists. 
for (f,t) in zip(ntc.zone_i, ntc.zone_j):
    lines, dclines = [], []
    lines += list(data.lines.index[(data.lines.node_i.isin(data.nodes.index[data.nodes.zone == f]))&(data.lines.node_j.isin(data.nodes.index[data.nodes.zone == t])) ])
    lines += list(data.lines.index[(data.lines.node_i.isin(data.nodes.index[data.nodes.zone == t]))&(data.lines.node_j.isin(data.nodes.index[data.nodes.zone == f]))])
    dclines += list(data.dclines.index[(data.dclines.node_i.isin(data.nodes.index[data.nodes.zone == f]))&(data.dclines.node_j.isin(data.nodes.index[data.nodes.zone == t])) ])
    dclines += list(data.dclines.index[(data.dclines.node_i.isin(data.nodes.index[data.nodes.zone == t]))&(data.dclines.node_j.isin(data.nodes.index[data.nodes.zone == f]))])

    ntc_values = ntc.loc[(ntc.zone_i == f) & (ntc.zone_j == t), "ntc"].sum()
    if len(lines) == 0 and len(dclines) == 0:
        ntc.loc[(ntc.zone_i == f) & (ntc.zone_j == t), "ntc"] = 0
    elif ntc_values < data.dclines.loc[dclines, "capacity"].sum():  #all(self.ntc.loc[(self.ntc.zone_i == f) & (self.ntc.zone_j == t), "ntc"] == 0):
        ntc.loc[(ntc.zone_i == f) & (ntc.zone_j == t), "ntc"] = data.dclines.loc[dclines, "capacity"].sum()

# %%
