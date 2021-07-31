# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import streamlit

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
import streamlit as st

import numpy as np
import pandas as pd
import plotly.express as px

# IPL = pd.read_csv(r'/Users/shubhamkumar/Downloads/ipl_csv2/all_matches.csv')

# years = IPL['start_date'].str[:4].astype(int).unique().tolist()

st.title('IPL_stats')
st.sidebar.header('Year')
year = list(reversed(range(2008, 2021, 1)))
selected_year = st.sidebar.multiselect('Year', year)


@st.cache
def load_data(year):
    df = pd.read_csv(r'/Users/shubhamkumar/Downloads/ipl_csv2/all_matches.csv')
    df['year'] = df['start_date'].str[:4].astype(int)
    df = df[df['year'].isin(year)]
    return df


# st.dataframe(load_data(selected_year))

df_year = load_data(selected_year)

st.sidebar.header('Team')
team = df_year['batting_team'].unique().tolist()
# all_teams = df_year['batting_team'].unique().tolist()
# team = team.append(all_teams)
selected_team = st.sidebar.multiselect('Team', team, default=team)

df_team = df_year[df_year['batting_team'].isin(selected_team)]
bat = df_team.groupby(['striker', 'match_id']).agg(
    {'ball': 'count', 'runs_off_bat': 'sum'})
bat = bat.reset_index(level=[0, 1])
# bat['striker_copy'] = bat['striker']
bat = bat.groupby(['striker']).agg(
    {'ball': 'sum', 'runs_off_bat': 'sum', 'match_id': 'count'})
bat = bat.rename(columns={'match_id': 'Innings'})
players = df_year['striker'].unique().tolist()
player_dismissals = {}
for i in players:
    player_dismissals.update({i: len(df_year[df_year['player_dismissed'] == i])})
Dismissals = pd.DataFrame([player_dismissals]).T.reset_index().rename(columns={'index': 'striker', 0: 'Dismissals'})
bat = bat.merge(Dismissals, on='striker')
bat['Average'] = round(bat['runs_off_bat'] / bat['Dismissals'], 2)
bat['Strike_Rate'] = round(bat['runs_off_bat'] / bat['ball'] * 100, 2)

Matches = st.sidebar.number_input('Input Minimum No. of Matches', min_value=1, max_value=500, step=1)

st.sidebar.header('Player')
Player = st.sidebar.selectbox('Select Player', players)
st.dataframe(bat[bat['Innings'] >= Matches].sort_values('runs_off_bat', ascending=False))

st.header('By Player (for the chosen years)')
st.dataframe(bat[(bat['striker'] == str(Player))])

st.header('AVG vs STRIKE_RATE')
fig = px.scatter(bat[bat['Innings'] >= Matches], x="Average", y="Strike_Rate", hover_data=['striker']
                 , template='plotly_dark')
fig.add_hline(y=bat[bat['Innings'] >= Matches]['Strike_Rate'].median())
fig.add_vline(x=bat[bat['Innings'] >= Matches]['Average'].median())
st.plotly_chart(fig)
