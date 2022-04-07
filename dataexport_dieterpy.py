# %%
import os
import numpy as np
from pathlib import Path
from pomato_data.pomato_data import PomatoData
import pandas as pd
import geopandas as gpd
import shapely
import requests

from pomato_data.res import capacities
from pomato_data.auxiliary import get_countries_regions_ffe

# %% PV availability
url = "http://opendata.ffe.de:3000/v_opendata?id_opendata=eq.3"
result = requests.get(url)
data = pd.DataFrame.from_dict(result.json()[0]["data"])

data = data[['id_region', 'region', 'values']]

country_data, nuts_data = get_countries_regions_ffe()
# de_nuts_data = nuts_data.loc[nuts_data.country=="DE"].copy()

pv_availability_raw = pd.merge(nuts_data, data,  on="id_region", how="left")
pv_availability_raw = pv_availability_raw[['id_region', 'name_short', 'values']]
pv_availability = pd.concat([pd.DataFrame({r.name_short:r["values"]}) if type(r["values"]) is list else pd.DataFrame({r.name_short:[0.1]*8784})
                            for ind, r in pv_availability_raw.iterrows()], axis=1)
pv_ava = pv_availability.sum(axis=0)

# %% PV rooftop potential (energy)
url = "http://opendata.ffe.de:3000/v_opendata?id_opendata=eq.50"
result = requests.get(url)
data = pd.DataFrame.from_dict(result.json()[0]["data"])

data = data[['id_region', 'internal_id_1', 'value']]

pv_rooftop = pd.merge(nuts_data, data[data.internal_id_1.isin([75])],  on="id_region", how="left")
pv_rooftop = pv_rooftop.drop(["id_region", "internal_id_1"], axis=1).fillna(.1)
pv_rooftop = pv_rooftop.groupby(["name", "name_short", "country"]).sum().reset_index()
pv_rooftop = pd.merge(pv_rooftop, nuts_data[["name_short", "geometry"]], on="name_short")

# %% PV rooftop potential (power)
pv_potential = pv_rooftop.copy()
pv_potential["value"] = pv_potential["value"].div(pv_ava[pv_rooftop["name_short"].values].values)
pvp = pd.DataFrame(pv_potential.drop(columns=["geometry"]))

# %% NUTS to nodes
zone = "DE"
nodes_orig = pd.read_csv(r"C:\Users\cw\repositories\PomatoData\data_out\nodes\nodes.csv")
capacity_nuts = pv_potential.set_index("name_short", drop=True)[["value"]].copy()
# GW to MW
capacity_nuts["value"] = capacity_nuts["value"]*1000 
capacity_nuts = capacity_nuts.rename(columns={"value":"pv_rooftop"})

nodes_orig = nodes_orig[nodes_orig["info"] != "joint"].copy()
country_data, nuts_data = get_countries_regions_ffe()    


nuts_data = gpd.GeoDataFrame(nuts_data[nuts_data.country == zone]).set_crs("EPSG:4326")

geometry = [shapely.geometry.Point(xy) for xy in zip(nodes_orig.lon, nodes_orig.lat)]
condition = [n.within(country_data.loc[zone, "geometry"]) for n in geometry]
nodes = gpd.GeoDataFrame(nodes_orig, crs="EPSG:4326", geometry=geometry).loc[condition].set_index("index", drop=True)

capacity_nodes = nodes[['voltage', 'name', 'zone', "info", "lat", "lon"]].copy()
nuts_to_nodes = gpd.sjoin(nodes, nuts_data, how='left', op='within')

nuts_to_nodes["weighting"] = 1
nuts_multiple_nodes = nuts_to_nodes[["name_short", "weighting"]].groupby('name_short').count()
nuts_multiple_nodes["sum_weight"] = nuts_to_nodes[["name_short", "weighting"]].groupby('name_short').sum()

for tech in capacity_nuts.columns:
    capacity_nodes[tech] = (capacity_nuts.loc[nuts_to_nodes.name_short, tech]/nuts_multiple_nodes.loc[nuts_to_nodes.name_short, "sum_weight"]).values

node_in_nuts = gpd.sjoin(nuts_data, nodes, how='left', op='contains')
nuts_no_node = node_in_nuts[node_in_nuts["index_right"].isna()]

nuts_centroids = nuts_data.centroid # .to_crs("epsg:4326")
nuts_no_node = nuts_centroids.loc[nuts_no_node.index] #.to_crs('epsg:2953')

# Find the closest node to the region's centroid and map them
dist = []
for j in range(len(nodes)):
    dist.append(nuts_no_node.distance(nodes.geometry.iloc[j]))
dist = pd.DataFrame(dist)
    
nuts_no_node_map = pd.DataFrame(dist.idxmin(), columns=['node_index'])
nuts_no_node_map["node"] = nodes.iloc[nuts_no_node_map.node_index].index
nuts_no_node_map = nuts_no_node_map.join(pd.DataFrame(nuts_data['name_short']))
nuts_no_node_map = nuts_no_node_map.reset_index()
nuts_no_node_map.rename(columns={'index': 'nuts_index'}, inplace=True)

# Add those regions to the nodal load patterns
for i in nuts_no_node_map.index:
    for tech in capacity_nuts.columns:
        capacity_nodes.loc[nuts_no_node_map['node'].loc[i], tech] += capacity_nuts.loc[nuts_no_node_map['name_short'].loc[i], tech]

tmp_plants = capacity_nodes[["zone", 'name', "lat", "lon", tech]].reset_index().rename(columns={"pv_rooftop": "g_pot", "index": "node"})
tmp_plants["index"] = tmp_plants.node.astype(str) + "_" + tech
tmp_plants = tmp_plants.set_index("index")

# %% Solar battery potential
pv_rooftop_potential = tmp_plants.copy().set_index("node", drop=True)["g_pot"]
p_max_pv = 0.01     # MW/household
pv_rooftop_households = (pv_rooftop_potential/p_max_pv).rename("households").round(0)
market_share = 1
solar_battery_households = (pv_rooftop_households*market_share).round(0)
inverter_sizing = 0.7
solar_battery_power_potential = (solar_battery_households*p_max_pv*inverter_sizing).rename("g_pot")
capacity_power_ratio = 3    # MWh/MW
solar_battery_capacity_potential = (solar_battery_power_potential*capacity_power_ratio).rename("storage_capacity")

# %% Store data
outdir = Path(r"C:\Users\cw\repositories\PomatoData\modezeen_data\20220221")
pv_rooftop_potential.to_csv(outdir.joinpath("pv_rooftop_potential.csv"))
solar_battery_households.to_csv(outdir.joinpath("solar_battery_households.csv"))
solar_battery_power_potential.to_csv(outdir.joinpath("solar_battery_power_potential.csv"))
solar_battery_capacity_potential.to_csv(outdir.joinpath("solar_battery_capacity_potential.csv"))

# %%
