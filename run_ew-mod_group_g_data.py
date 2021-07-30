#%%
import os
from pathlib import Path
from pomato_data.pomato_data import PomatoData

os.chdir("C:\\Users\\cw\\repositories\\PomatoData")

if __name__ == "__main__":  

    settings = {
        "grid_zones": ["DE","NO","SE"],
        "weather_year": 2019,
        "capacity_year": 2020, 
        "co2_price": 55,
        "split_lines": True,
        # "time_horizon": "01.01.2019 - 31.12.2019",
        "time_horizon": "01.01.2019 - 31.12.2019",
        "include_neighbours": False,
        }
    
    if Path(os.path.abspath("")).name != "PomatoData":
        raise FileNotFoundError("Please Execute the script in the repository itself, use os.chdir() to change path")
    else: 
        wdir = Path(os.path.abspath(""))
        
    data = PomatoData(wdir, settings)

# %% EW-MOD Group G Processing
    data.create_basic_ntcs()

    # Remove small plants below a certain threshold 
    threshold = 1
    data.plants[data.plants.g_max > threshold].g_max.sum() / data.plants.g_max.sum()  
    len(data.plants[data.plants.g_max > threshold]) / len(data.plants[data.plants.g_max > 0])
    
    data.plants = data.plants[data.plants.g_max > threshold]
    drop_plants = [p for p in data.availability.columns if p not in data.plants.index]
    data.availability = data.availability.drop(drop_plants, axis=1)
    
    foldername = f"EW-MOD_Group-G_{settings['capacity_year']}_no_nghbrs"
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
    
    plants_2020 = data.plants.copy()
    # # plants_2030 = data.plants.copy()
    t = plants_2020[["fuel", "technology", "zone", "g_max"]].groupby(["fuel", "technology", "zone"]).sum().reset_index().fillna(0)
    t = t.pivot(index="zone", columns=("fuel", "technology"), values="g_max")
    t.plot.bar(stacked=True)
    
    #hydro plants norway
    reservoir_NO = data.plants.loc[(data.plants.zone == 'NO') & (data.plants.fuel == 'hydro')]


# %%
