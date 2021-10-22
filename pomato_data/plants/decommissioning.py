import pandas as pd
import numpy as np
from pathlib import Path

def decom_linear(plants, scenario, settings):
    '''
    Linear decommisioning. No plant site is dropped, except if technology is dropped. Capacity is scaled linearly
    '''
    for z in settings["decommissioning"]["zones"]:
        for f in settings["decommissioning"]["fuels"]:
            cap_old = plants.loc[(plants.fuel==f)&(plants.zone==z),"g_max"].sum() / 1000    # get old capacity in GW
            cap_new = scenario.loc[(scenario.group==f)&(scenario.country==z),"capaConv"].iat[0] # get new capacity in GW
            if cap_new==0.0:    # drop plants if full capacity is decommissioned
                ind_drop = plants.loc[(plants.fuel==f)&(plants.zone==z)].index
                plants.drop(ind_drop, inplace=True)
            else:
                scaling_factor = cap_new/cap_old
                plants.loc[(plants.fuel==f)&(plants.zone==z),"g_max"] = plants.loc[(plants.fuel==f)&(plants.zone==z),"g_max"]*scaling_factor

    return plants

def decommission(plants, scenario, settings):
    if settings["decommissioning"]["method"] == 'linear':
        plants_upated = decom_linear(plants, scenario, settings)

    return plants_upated