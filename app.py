import streamlit as st
import pandas as pd
import unicodedata
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# ---------------------- Helper Functions ----------------------

def fix_name(name):
    """Clean player name for proper display"""
    try:
        return unicodedata.normalize('NFKD', name).encode('latin1').decode('utf-8')
    except:
        return name

def convert_value(val):
    """Convert value strings like '€30m' into float (e.g. 30,000,000)"""
    if isinstance(val, str):
        val = val.replace('€', '').replace('m', 'e6').replace('M', 'e6').replace('k', 'e3').strip()
        try:
            return float(eval(val))
        except:
            return None
    return val

# ---------------------- Load & Clean Data ----------------------

@st.cache_data
def load_data():
    """Load player dataset and clean key fields"""
    df = pd.read_excel("data/processed/transfermarkt_players.xlsx")

    if 'Player' in df.columns:
        df.rename(columns={'Player': 'PlayerName'}, inplace=True)

    df['PlayerName'] = df['PlayerName'].apply(fix_name)
    df['MarketValue'] = df['MarketValue'].apply(convert_value)

    # Drop players missing critical fields
    df.dropna(subset=['MarketValue', 'Position', 'Club'], inplace=True)

    return df

df = load_data()

# ---------------------- Train ML Model ----------------------

# Use historical player stats to predict market value
ml_features = ['Age', 'Goals', 'Assists', 'MatchesPlayed', 'YellowCards', 'OwnGoals']
ml_df = df[ml_features + ['MarketValue']].dropna()

# Features (X) and Target (y)
X = ml_df[ml_features]
y = ml_df['MarketValue']

# Train simple regression model
model = LinearRegression()
model.fit(X, y)

# Prepare prediction data for entire dataset
X_all = df[ml_features].fillna(0)  # Fill missing stats with 0 for prediction
df['PredictedValue'] = model.predict(X_all)

# Calculate difference between predicted and actual value
df['ValueGap'] = df['PredictedValue'] - df['MarketValue']

# ---------------------- UI: App Layout ----------------------

st.title("⚽ AI-Based Football Player Recommendation System")

# Tabbed UI for better experience
tab1, tab2, tab3 = st.tabs(["🎯 Recommend Players", "📊 Compare Players", "🎓 Predict Market Value"])

# ---------------------- Tab 1: Recommend ----------------------

with tab1:
    st.header("🎯 Recommend Players Based on Budget and Stats")

    # Budget input
    budget = st.number_input("Enter your total budget (€)", min_value=0.0, value=50_000_000.0)

    # Filters
    positions = st.multiselect("Preferred Positions", options=df['Position'].unique(), default=list(df['Position'].unique()))
    excluded_clubs = st.multiselect("Exclude Clubs", options=df['Club'].unique())

    # Toggle AI Recommendation
    use_ai = st.checkbox("💡 Use AI to Recommend Undervalued Players")

    # Filter by user inputs
    filtered_df = df.copy()
    filtered_df = filtered_df[filtered_df['MarketValue'] <= budget]

    if positions:
        filtered_df = filtered_df[filtered_df['Position'].isin(positions)]
    if excluded_clubs:
        filtered_df = filtered_df[~filtered_df['Club'].isin(excluded_clubs)]

    # If AI mode: Recommend undervalued players
    if use_ai:
        filtered_df = filtered_df[filtered_df['ValueGap'] > 0]  # Players who are predicted to be worth more
        st.info("AI recommending players whose predicted value is higher than actual value. These might be great value picks!")

    # Display result
    st.subheader(f"✅ {len(filtered_df)} Players Found")
    if not filtered_df.empty:
        st.dataframe(
            filtered_df.sort_values(by="ValueGap" if use_ai else "MarketValue", ascending=False)[[
                'PlayerName', 'Age', 'Position', 'Club', 'MarketValue', 'PredictedValue', 'Goals', 'Assists'
            ]].reset_index(drop=True),
            use_container_width=True
        )
    else:
        st.warning("No players match your criteria.")

# ---------------------- Tab 2: Compare ----------------------

with tab2:
    st.header("📊 Compare Player Stats")

    selected_players = st.multiselect("Select players to compare", df['PlayerName'].unique())

    def highlight_max(s):
        is_max = s == s.max()
        return ['background-color: lightgreen' if v else '' for v in is_max]

    if selected_players:
        compare_df = df[df['PlayerName'].isin(selected_players)]
        stats_to_compare = ['Goals', 'Assists', 'MarketValue', 'PredictedValue', 'Age', 'MatchesPlayed']
        display_df = compare_df[['PlayerName'] + stats_to_compare].set_index('PlayerName')
        styled_df = display_df.style.apply(highlight_max, axis=0)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("Select players from the dropdown to compare.")

# ---------------------- Tab 3: Predict ----------------------

with tab3:
    st.header("🎓 Predict Player Market Value (AI Model)")

    # User input for stats
    age = st.number_input("Age", min_value=15, max_value=45, value=25)
    goals = st.number_input("Total Goals", min_value=0, value=10)
    assists = st.number_input("Total Assists", min_value=0, value=5)
    matches = st.number_input("Matches Played", min_value=0, value=30)
    yellow = st.number_input("Yellow Cards", min_value=0, value=2)
    own_goals = st.number_input("Own Goals", min_value=0, value=0)

    # Predict on button click
    if st.button("Predict Market Value"):
        input_data = [[age, goals, assists, matches, yellow, own_goals]]
        predicted_value = model.predict(input_data)[0]
        st.success(f"Estimated Market Value: **€{predicted_value:,.2f}**")
