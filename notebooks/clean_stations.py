# %% [markdown]
# # Cleaning  `Stations.txt`

import pandas as pd
import re

# %%
f = open(r'data/raw/stations.txt', 'r')
stations = f.readlines()
f.close()
data = stations[4:19377]

# %%
pattern = re.compile(r" (\d+) (\d+[A-Z]{0,2}){0,1} +?([\(\)A-Z0-9'\.@\-\/&\[\]\:#" +
                     '"' + r"]+ {1,3})+ {0,}?(\d{4}) +?((\d{4})|(\.\.)) +?(-\d+\.\d+) +?(\d+\.\d+)")

matches = []
for line in data:
    matches.append(pattern.split(line))

num_matches = [len(i) for i in matches]

match_stats = pd.DataFrame({'matches': matches, 'num_matches': num_matches})
match_stats['num_matches'].value_counts()

# %%
no_match = match_stats.loc[match_stats['num_matches'] == 1]
if len(no_match) != 0:
    print(data[nomatch.sample().index[0]])
else:
    print('all matches found')

# %%
