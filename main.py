import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import plotly as plotly
import plotly.express as px
import streamlit as st

Points_URL = "https://www.fantasypros.com/nba/stats/overall.php"

response = requests.get(Points_URL)

soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table')

headers = [th.text.strip() for th in table.find_all('th')]

data = []
for tr in table.find_all('tr')[1:]:
    row = [td.text.strip() for td in tr.find_all('td')]
    data.append(row)

points = pd.DataFrame(data, columns=headers)

numeric_columns = ['PTS', 'FTM', 'REB', 'AST', 'BLK', 'STL', 'FG%', 'FT%', '3PM', 'TO', 'GP', 'MIN', '2PM', 'A/TO',
                   'PF']
points[numeric_columns] = points[numeric_columns].replace({',': ''}, regex=True)

points = points.apply(pd.to_numeric, errors='ignore')

points['Non-FT'] = points['PTS'] - points['FTM']
points['Non-FT%'] = points['Non-FT'] / points['PTS']

points['Non-FT%'] = points['Non-FT%'].fillna(0)

team_pos = points['Player'].str.extract(r'\((.*?)\)')
points['Team'] = team_pos[0].apply(lambda x: x.split()[0])
points['POS'] = team_pos[0].apply(lambda x: x.split()[-1])
points['Player'] = points['Player'].str.split('(').str[0].str.strip()

filtered_points = points[points['Team'] != 'FA']

team_non_ft_avg = filtered_points.groupby('Team')['Non-FT'].mean()
# print(filtered_points)
#
# csv_file_path = "filtered_points_updated.csv"
#
# filtered_points.to_csv(csv_file_path, index=False)

st.title('NBA Deep Dive')

file = "/c/Users/rycor/PycharmProjects/pythonProject8/filtered_points_updated.csv"


@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')


csv = convert_df(filtered_points)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='NBA_Deep_Dive.csv',
    mime='text/csv',
)

team = st.selectbox("Pick A Team", ["BOS", "BKN", "NYK", "PHI", "TOR", "GSW", "LAC", "LAL", "PHO", "SAC", "CHI", "CLE",
                                    "DET", "IND", "MIL", "ATL", "CHA", "MIA", "ORL", "WAS", "DEN", "MIN", "OKC", "POR",
                                    "UTH", "DAL", "HOU", "MEM", "NOR", "SAS"])

team_df = filtered_points[filtered_points['Team'] == team]

st.header(f'{team} Stats')

tab1, tab2 = st.tabs(['PTS', 'Non-FT'])

with tab1:
    fig_pts = px.scatter(team_df, x='FG%', y='PTS')
    st.plotly_chart(fig_pts)

with tab2:
    fig_pts_no_ft = px.scatter(team_df, x='Non-FT%', y='Non-FT')
    st.plotly_chart(fig_pts_no_ft)

with st.sidebar:
    player = st.text_input('Enter A Player:', value='Jayson Tatum')
    st.header(f'Stats of {player}')
    player_df = filtered_points[filtered_points['Player'] == player][['PTS', 'REB', 'AST', 'STL', 'BLK']]

    player_df.columns = ['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks']

    player_df.reset_index(drop=True, inplace=True)
    st.dataframe(player_df)

choice = st.number_input("Pick a Number of Players to show", 1, 100)
top_players = filtered_points.sort_values(by='PTS', ascending=False).head(choice)
st.bar_chart(top_players.set_index('Player')['PTS'])
