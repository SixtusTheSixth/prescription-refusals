# imports
import math
import pandas as pd
import os

# load data
spatial = pd.read_csv(os.path.join('data', 'spatial.csv')) # geoid by lat-long
tbl1 = pd.read_csv(os.path.join('data', 'tables', 'table01.csv')) # geoid by sex by age
pharmacies = pd.read_csv(os.path.join('data', 'NC_Pharmacies_MCM.csv')) # pharmacy name by address by lat-long

# select relevant columns
pharmacies = pharmacies[['NAME', 'X', 'Y']] # select name and lat-long
spatial = spatial[['GEOID', 'Longitude', 'Latitude']] # long = x, lat = y so rearrange in (x, y) format
tbl1 = tbl1[['GEOID', 'B01001_030E', 'B01001_031E', 'B01001_032E', 'B01001_033E', 'B01001_034E', 'B01001_035E', 'B01001_036E', 'B01001_037E', 'B01001_038E', 'B01001_039E']]
# geoid by women 15-50 in 10 columns: 15-17, 18-19, 20, 21, 22-24, 25-29, 30-34, 35-39, 40-44, 45-49.

# define lat-long distance
def haversine_dist(long1, lat1, long2, lat2):
    R = 3959 # volumetric radius of the earth in miles
    # return distance between two points along earth's surface in miles
    long1, lat1, long2, lat2 = long1 * math.pi / 180, lat1 * math.pi / 180, long2 * math.pi / 180, lat2 * math.pi / 180
    try:
       return 2 * R * math.asin(math.sqrt(math.sin((lat2 - lat1) / 2) ** 2) + math.cos(lat1) * math.cos(lat2) * (math.sin((long2 - long1) / 2) ** 2))
    except:
        print(long1, lat1, long2, lat2)
        exit()

# find, for each GEOID, the pharmacy closest to it (already have women age data)
# find coords of this geoid, loop through pharmacies and find closest one
# add closest pharmacy name, x, and y to columns
closest_pharmas = []
for row in range(len(tbl1)):
    geo_long = spatial.at[row, 'Longitude']
    geo_lat = spatial.at[row, 'Latitude']
    pharma_dists = pharmacies.apply(lambda x : haversine_dist(x.X, x.Y, geo_long, geo_lat), axis=1)
    minidx = pharma_dists.idxmin()
    closest_pharmas.append([pharmacies.at[minidx, 'NAME']])

closest_pharmas_df = pd.DataFrame(closest_pharmas, index=list(range(len(closest_pharmas))), columns=['PharmaName'])
closest_table = pd.concat([tbl1, closest_pharmas_df], axis=1)

num_women = closest_table.groupby(['PharmaName']).sum()
num_women['TotalWomen'] = num_women.loc[:, 'B01001_030E':'B01001_039E'].sum(axis=1)
# num_women[['B01001_030E']] + num_women[['B01001_031E']] + num_women[['B01001_032E']] + num_women[['B01001_033E']] + \
#     num_women[['B01001_034E']] + num_women[['B01001_035E']] + num_women[['B01001_036E']] + num_women[['B01001_037E']] + num_women[['B01001_038E']] + num_women[['B01001_039E']]

print(num_women.sort_values('TotalWomen', ascending=False))
num_women.to_csv('Women_by_pharmacy.csv')