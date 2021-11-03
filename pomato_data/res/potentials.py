
import requests
import pandas as pd
from pathlib import Path

from pomato_data.auxiliary import get_countries_regions_ffe

def get_potentials_ffe():
    country_data, nuts_data = get_countries_regions_ffe()    

    # Download Potentials 
    url = "http://opendata.ffe.de:3000/v_opendata?id_opendata=eq.50"
    result = requests.get(url)
    data = pd.DataFrame.from_dict(result.json()[0]["data"])
    
    data = data[['id_region', 'internal_id_1', 'value']]

    wind = pd.merge(nuts_data, data[data.internal_id_1 == 1],  on="id_region", how="left")
    wind = wind.drop(["id_region", "internal_id_1"], axis=1).fillna(.1) 
    # default has top be non-zero for the capacity regionalisation. 
    
    pv_rooftop = pd.merge(nuts_data, data[data.internal_id_1.isin([75])],  on="id_region", how="left")
    pv_rooftop = pv_rooftop.drop(["id_region", "internal_id_1"], axis=1).fillna(.1)
    pv_rooftop = pv_rooftop.groupby(["name", "name_short", "country"]).sum().reset_index()
    pv_rooftop = pd.merge(pv_rooftop, nuts_data[["name_short", "geometry"]], on="name_short")

    pv_park = pd.merge(nuts_data, data[data.internal_id_1.isin([76])],  on="id_region", how="left")
    pv_park = pv_park.drop(["id_region", "internal_id_1"], axis=1).fillna(.1)
    pv_park = pv_park.groupby(["name", "name_short", "country"]).sum().reset_index()
    pv_park = pd.merge(pv_park, nuts_data[["name_short", "geometry"]], on="name_short")
    
    return wind, pv_rooftop, pv_park

if __name__ == "__main__": 
    import pomato_data
    
    wdir = Path(pomato_data.__path__[0]).parent 
    wind_potentials, pv_rooftop_potentials, pv_park_potentials = get_potentials_ffe()
    wind_potentials.to_csv(wdir.joinpath('data_out/res_potential/wind_potential.csv'))
    pv_rooftop_potentials.to_csv(wdir.joinpath('data_out/res_potential/pv_rooftop_potential.csv'))
    pv_park_potentials.to_csv(wdir.joinpath('data_out/res_potential/pv_park_potential.csv'))
