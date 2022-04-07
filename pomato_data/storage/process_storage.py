import pandas as pd
import numpy as np
from pandas._libs.tslibs.timedeltas import Timedelta

def add_storage(plants, technology, scenario):
    # file_path = str(filepath.joinpath("data_in/plants/input_efficiency_literature_by_fuel_technology.csv"))
    # efficiency_data = pd.read_csv(file_path, header=0, sep=",")
    solar_battery = add_solar_battery(plants, technology.loc[technology.technology=="solar battery"].squeeze(), scenario)
    
    return solar_battery

# def add_household_battery(plants, technology, battery_g=10000, battery_cap=(9800+560)):
def add_solar_battery(plants, technology, scenario):
    solar_battery = pd.DataFrame()
    for ind, row in scenario.loc[scenario.group == "solar battery"].iterrows():
        pv_household = plants.loc[(plants["technology"]=="solar rooftop") & (plants["zone"]==row["country"])].copy()
        # scale from GW/GWh to MW/MWh
        power_factor = row["capaConv"]*1000/pv_household.g_max.sum()
        capacity_factor = row["capaStSize"]*1000/pv_household.g_max.sum()
    
        solar_battery_tmp = pv_household.copy().reset_index()
        
        solar_battery_tmp["storage_capacity"] = solar_battery_tmp["g_max"]*capacity_factor
        solar_battery_tmp["g_max"] = solar_battery_tmp["g_max"]*power_factor
        solar_battery_tmp["d_max"] = solar_battery_tmp["g_max"]
        solar_battery_tmp["eta"] = technology["eta"]
        solar_battery_tmp["fuel"] = technology["fuel"]
        solar_battery_tmp["technology"] = technology["technology"]
        solar_battery_tmp["index"] = solar_battery_tmp["node"].str.cat(others=solar_battery_tmp["fuel"].str.cat(solar_battery_tmp["technology"], sep='/'), sep='_')
        solar_battery_tmp.set_index("index", inplace=True)
        solar_battery_tmp["plant_type"] = technology["plant_type"]
        
        solar_battery = pd.concat([solar_battery, solar_battery_tmp])
        
    return solar_battery

def process_battery_storage_level(t_start, t_end, demand, plants):
    # timesteps = pd.date_range(t_start, t_end, freq='168H')
    timesteps = pd.date_range(t_start, t_end, freq='168H').tolist()
    # timesteps[1:] = [t - pd.Timedelta(value=1, unit="hours") for t in timesteps[1:]]
    if pd.Timestamp(t_end) != timesteps[-1]:
        timesteps.append(pd.Timestamp(t_end) - pd.Timedelta(value=1, unit="hours"))
    timestep_index = demand.loc[demand.utc_timestamp.isin(timesteps), "utc_timestamp"]
    
    storage_level_battery = pd.DataFrame()
    for ind, p in plants.loc[plants.technology=="solar battery"].iterrows():
        tmp_level = pd.DataFrame(index=timestep_index.index)
        tmp_level["plant"] = ind
        tmp_level["storage_level"] = 0
        storage_level_battery = pd.concat([storage_level_battery, tmp_level])
        
    return storage_level_battery.reset_index()
        
# t_start = data.time_horizon["start"]
# t_end = data.time_horizon["end"]
# demand = data.demand_el
# plants = data.plants

