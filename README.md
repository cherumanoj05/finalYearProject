# ⚽ ScoutSmart – AI-Based Football Player Recommendation System

This project uses machine learning to analyze football player statistics and recommend the most valuable players based on your budget and preferences.

### 🚀 Features:
- 🎯 **AI-Powered Recommendations** – Suggests undervalued players by comparing predicted vs actual market value.
- 📊 **Compare Players** – Compare performance and value of multiple players visually.
- 🎓 **Market Value Prediction** – Predict any player’s estimated market value using stats like age, goals, assists, etc.
- 📂 Based on real-world data from Transfermarkt.

### 💡 Technology Used:
- Python
- Streamlit (Frontend)
- Pandas & Scikit-learn (ML)
- Linear Regression for market value prediction

### 📌 How It Works:
- Player stats are fed into a trained regression model to predict market value.
- Players whose predicted value > actual value are marked as "undervalued".
- The system recommends these players as high-potential targets under your budget.

### 📁 Dataset:
- Sourced from Transfermarkt, preprocessed in `data/processed/transfermarkt_players.xlsx`

### 🎓 Ideal For:
- Football clubs, analysts, or scouts who want to spot good transfer market opportunities using AI.
- Final year students building real-world AI projects.

---

Give it a ⭐ if you like it!
