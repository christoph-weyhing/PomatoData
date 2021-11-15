import pandas as pd

def add_storage(plants, technology, scenario):
    # file_path = str(filepath.joinpath("data_in/plants/input_efficiency_literature_by_fuel_technology.csv"))
    # efficiency_data = pd.read_csv(file_path, header=0, sep=",")
    household_battery = add_household_battery(plants, technology.loc[technology.technology=="battery"].squeeze(), scenario)
    
    return household_battery

# def add_household_battery(plants, technology, battery_g=10000, battery_cap=(9800+560)):
def add_household_battery(plants, technology, scenario):
    for ind, row in scenario.loc[scenario.group == "battery"].iterrows():
        pv_household = plants.loc[(plants["technology"]=="solar rooftop") & (plants["zone"]==row["country"])].copy()
        power_factor = row["capaConv"]/pv_household.g_max.sum()
        capacity_factor = row["capaStSize"]/pv_household.g_max.sum()
    
        household_battery = pv_household.copy().reset_index()
        
        household_battery["g_max"] = household_battery["g_max"]*power_factor
        household_battery["eta"] = technology["eta"]
        household_battery["fuel"] = technology["fuel"]
        household_battery["technology"] = technology["technology"]
        household_battery["index"] = household_battery["node"].str.cat(others=household_battery["fuel"].str.cat(household_battery["technology"], sep='/'), sep='_')
        household_battery.set_index("index")
        household_battery["plant_type"] = technology["plant_type"]
        household_battery["storage_capacity"] = household_battery["g_max"]*capacity_factor
        household_battery["d_max"] = household_battery["g_max"]*power_factor

    return household_battery