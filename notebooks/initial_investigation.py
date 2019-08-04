# %% [markdown]
# # Initial investigation of dataset

# %% imports and reading data
import pandas as pd
import plotly.express as px

au_weather = pd.read_csv(r'data//raw//weatherAus.csv')
au_weather['Date'] = pd.to_datetime(au_weather['Date'])
au_weather['Month'] = pd.to_datetime(
    au_weather['Date'].apply(lambda x: f'01-{x.month_name()}-{x.year}'))
au_weather['Month Name'] = au_weather['Date'].dt.month_name()

# %% [markdown]
# # What does the dataset look like?
# ## Basics
au_weather.head(10)

# %%
print(au_weather.shape)

# %% [markdown]
# ## Columns
for f in list(au_weather):
    print(f)

# %% [markdown]
# ## How many measurements per location?

num_measures = au_weather.groupby('Location')['Date'].count(
).reset_index().rename({'Date': 'num_measures'}, axis=1)
fig = px.histogram(num_measures, x='num_measures',
                   template='plotly_dark', color='Location')
fig.show()

# %%
au_weather['Location'].describe()

# %% [markdown]
# ## 9AM Temperature for each location
temp_9am = au_weather.groupby('Date')['Temp9am'].mean().reset_index()
fig = px.line(temp_9am, x='Date', y='Temp9am', template='plotly_dark')
fig.show()

# %% [markdown]
# ## Rainfall by Location and month name
area_month_rain = au_weather.groupby(['Month Name', 'Location'])[
    'Rainfall'].sum().reset_index()
fig = px.bar(area_month_rain, x='Location', y='Rainfall',
             color='Month Name', template="plotly_dark")
fig.show()


# %%
