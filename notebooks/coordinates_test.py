# %% [markdown]
# # Coordinates Test
# Want to test out the capabilities of plotly when using coordinates
# A smattering of visulisations

import pandas as pd
import plotly.express as px

weather = pd.read_csv(r'data/processed/weather.csv')

weather.sample(10)

# %%
basic_stats = (weather
               .groupby(['Location', 'lat', 'lng'])
               .agg({
                    'Temp3pm': 'mean',
                    'Rainfall': 'sum'})
               .reset_index()
               .rename({
                   'Temp3pm': 'Mean Temp 3PM',
                   'Rainfall': 'Sum Rainfall'}, axis=1))

lat_range = [basic_stats['lat'].min(), basic_stats['lat'].max()]
lng_range = [basic_stats['lng'].min(), basic_stats['lng'].max()]

fig = px.scatter_geo(
    basic_stats,
    lat='lat',
    lon='lng',
    color='Mean Temp 3PM',
    size='Sum Rainfall',
    hover_name='Location',
    template='plotly_dark')


fig.update_layout(
    # lonaxis_range=[-54.0, 108.0,],
    # lataxis_range=[114.0, -120.0],
    title='Rainfall and Mean Temperature in Australia',
    geo=dict(
        resolution=50,
        lataxis_range=lat_range,
        lonaxis_range=lng_range,
        projection=dict(scale=0.8)
    ),
)
fig.show()


# %%
