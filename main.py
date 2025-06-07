import streamlit as st
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('data/processed/transfermarkt_players.xlsx')
    # Clean MarketValue: remove € and M, convert to float million
    def parse_value(val):
        if isinstance(val, str):
            val = val.replace('€', '').replace('m', '').replace('M', '').strip()
            try:
                return float(val)
            except:
                return 0.0
        elif isinstance(val, (int, float)):
            return float(val)
        return 0.0
    df['MarketValue'] = df['MarketValue'].apply(parse_value)
    return df

df = load_data()

# Preprocess for ML
ml_df = df[['Age', 'Goals', 'Assists', 'MatchesPlayed', 'YellowCards', 'OwnGoals', 'MarketValue']].dropna()

X = ml_df[['Age', 'Goals', 'Assists', 'MatchesPlayed', 'YellowCards', 'OwnGoals']]
y = ml_df['MarketValue']

model = LinearRegression()
model.fit(X, y)


st.title("Transfermarkt Player Recommendation & Comparison")

tab1, tab2 = st.tabs(["🎯 Recommend Players", "📊 Compare Players"])

with tab1:
    st.header("Player Recommendation")

    budget = st.number_input("Enter your Budget (in million €)", min_value=0.0, value=50.0, step=0.1)
    exclude_clubs = st.multiselect("Exclude Clubs", options=df['Club'].unique())
    positions = st.multiselect("Preferred Positions", options=df['Position'].unique())

    # Filter players by budget
    filtered_df = df[df['MarketValue'] <= budget]

    # Exclude clubs
    if exclude_clubs:
        filtered_df = filtered_df[~filtered_df['Club'].isin(exclude_clubs)]

    # Filter by positions
    if positions:
        filtered_df = filtered_df[filtered_df['Position'].isin(positions)]

    st.write(f"Players matching criteria: {len(filtered_df)}")

    if not filtered_df.empty:
        # Show top 20 by MarketValue descending
        result = filtered_df.sort_values(by='MarketValue', ascending=False).head(20)
        st.dataframe(result[['Player', 'Position', 'Age', 'Club', 'MarketValue', 'Goals', 'Assists', 'MatchesPlayed', 'YellowCards']], use_container_width=True)
    else:
        st.write("No players found matching the criteria.")

with tab2:
    st.header("Compare Players")

    selected_players = st.multiselect("Select players to compare", df['Player'].unique())

    def highlight_max(s):
        is_max = s == s.max()
        return ['background-color: lightgreen' if v else '' for v in is_max]

    if selected_players:
        compare_df = df[df['Player'].isin(selected_players)]
        stats_to_compare = ['Goals', 'Assists', 'MarketValue', 'Age', 'MatchesPlayed']
        display_df = compare_df[['Player'] + stats_to_compare].set_index('Player')
        styled_df = display_df.style.apply(highlight_max, axis=0)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.write("Select players from the dropdown above to compare.")

tab1, tab2, tab3 = st.tabs(["🎯 Recommend", "📊 Compare", "🎓 Predict Market Value"])

# Prediction Tab
with tab3:
    st.header("Predict Player's Market Value using AI")

    age = st.number_input("Age", min_value=15, max_value=45, value=25)
    goals = st.number_input("Total Goals", min_value=0, value=10)
    assists = st.number_input("Total Assists", min_value=0, value=5)
    matches = st.number_input("Matches Played", min_value=0, value=30)
    yellow = st.number_input("Yellow Cards", min_value=0, value=2)
    own_goals = st.number_input("Own Goals", min_value=0, value=0)

    if st.button("Predict Market Value"):
        features = [[age, goals, assists, matches, yellow, own_goals]]
        predicted_value = model.predict(features)[0]
        st.success(f"Estimated Market Value: **€{predicted_value:.2f} million**")
