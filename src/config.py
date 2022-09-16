'''
Useful configuration variables for the update / dashboard.
'''
from pathlib import Path
import pandas as pd


# data path
config_path = Path(__file__).parent
root_path = config_path/".."/"data"  # fill in the root data path
data_root = root_path
db_path = data_root/"weather.db"

# airport info path
airport_csv_path = data_root/"airports.csv"
df_airports = pd.read_csv(airport_csv_path)
airports = list(df_airports.T.to_dict().values())

# hour of day to pull (0 = midnight)
pull_hour = 0
