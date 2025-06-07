import streamlit as st
import pandas as pd
import unicodedata

# ----------------- Helper Functions -----------------

def fix_name(name):
    try:
        return unicodedata.normalize('NFKD', name).encode('latin1').decode('utf-8')
    except:
        return name

def convert_value(val):
    if isinstance(val, str):
        val = val.replace('€', '').replace('m', 'e6').replace('k', 'e3')
        try:
            return float(eval(val))
        except:
            return None
    return val

# ----------------- Load Data -----------------

@st.cache_data
def load_data():
    df = pd.read_excel("data/processed/transfermarkt_players.xlsx")

    df.rename(columns={'Player': 'PlayerName'}, inplace=True)
    df['PlayerName'] = df['PlayerName'].apply(fix_name)
    df['MarketValue'] = df['MarketValue'].apply(convert_value)

    df.dropna(subset=['MarketValue', 'Position', 'Club'], inplace=True)

    return df

df = load_data()

# ----------------- User Input -----------------

st.title("Player Recommendation System")

budget = st.number_input("Enter your total budget (€)", min_value=0, value=50000000)

positions = df['Position'].dropna().unique()
selected_positions = st.multiselect("Preferred Positions", positions, default=list(positions))

clubs = df['Club'].dropna().unique()
excluded_club = st.selectbox("Exclude Club", ['None'] + sorted(clubs.tolist()))

# ----------------- Filtering Logic -----------------

filtered_df = df.copy()

# Filter by position
if selected_positions:
    filtered_df = filtered_df[filtered_df['Position'].isin(selected_positions)]

# Filter by club
if excluded_club != 'None':
    filtered_df = filtered_df[filtered_df['Club'] != excluded_club]

# Filter by budget
filtered_df = filtered_df[filtered_df['MarketValue'] <= budget]

# ----------------- Display Results -----------------

st.subheader(f"Recommended Players ({len(filtered_df)} found)")

if not filtered_df.empty:
    st.dataframe(
        filtered_df.sort_values(by="MarketValue", ascending=False)[[
            'PlayerName', 'Age', 'Position', 'Club', 'MarketValue', 'Goals', 'Assists'
        ]].reset_index(drop=True)
    )
else:
    st.warning("No players found matching your criteria.")
