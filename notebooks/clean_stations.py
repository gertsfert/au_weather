# %% [markdown]
# # Cleaning  `Stations.txt`

import pandas as pd

# %%
f = open(r'data/raw/stations.txt', 'r')
stations = f.readlines()
f.close()
data = stations[4:19377]

# %%
# pull out all the spaces from the column header line to find delimiting index
column_splits = stations[3]
column_spaces = [i for i, char in enumerate(column_splits) if char == ' ']
column_spaces = [0] + column_spaces + \
    [len(column_splits) - 1]  # add start and end

fields = stations[2]
field_names = []

# field names
for i in range(len(column_spaces) - 1):
    field_names.append(fields[column_spaces[i]: column_spaces[i+1]].strip())

# %%
parsed_data = {}
for i, field in enumerate(field_names):
    parsed_data[field] = []
    for row in data:
        parsed_data[field].append(
            row[column_spaces[i]: column_spaces[i+1]].strip())

df = pd.DataFrame(parsed_data)
