import streamlit as st
import joblib
import pandas as pd

model = joblib.load("notebook/fraud_model.pkl")

st.title("🛡️ AI FraudShield")

st.markdown("""
### Explainable Credit Card Fraud Detection Dashboard

Upload transaction data and identify suspicious transactions using Machine Learning.
""")
st.subheader("Credit Card Fraud Detection System")

uploaded_file = st.file_uploader(
    "Upload Transaction CSV",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    if "Class" in df.columns:
        df = df.drop("Class", axis=1)

    X = df.copy()

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)

    df["Prediction"] = pd.Series(predictions).map({
        0: "Normal",
        1: "Fraud"
    })

    df["Fraud Probability"] = (
    probabilities[:,1] * 100
    ).round(2)

#risk levels of various frauds

    def risk_level(p):

     if p > 80:
        return "High"

     elif p > 40:
        return "Medium"

     else:
        return "Low"
     
    df["Risk Level"] = (
    df["Fraud Probability"]
    .apply(risk_level)
    )

    def highlight_risk(row):

      if row["Risk Level"] == "High":
        return [
            "background-color: #ffcccc; color: black;"
        ] * len(row)

      elif row["Risk Level"] == "Medium":
        return [
            "background-color: #fff2cc; color: black;"
        ] * len(row)

      elif row["Risk Level"] == "Low":
        return [
            "background-color: #d4edda; color: black;"
        ] * len(row)
 
      return [""] * len(row)

#result of all frauds detected

    fraud_df = df[df["Prediction"] == "Fraud"]
    st.subheader("🚨 Suspicious Transactions")
    st.info(
    "Transactions are color coded by risk level."
     )
    fraud_df = fraud_df.sort_values(
    by="Fraud Probability",
    ascending=False
    )
    st.dataframe(
    fraud_df.style.apply(
        highlight_risk,
        axis=1
    ),
    use_container_width=True
)
#fraud counts

    frauds = (df["Prediction"] == "Fraud").sum()

#fraud percentage

    fraud_percent = (frauds / len(df)) * 100

    col1, col2 = st.columns(2)

    with col1:
     st.metric(
        "🚨 Fraud Transactions",
        frauds
    )

    with col2:
     st.metric(
        "📊 Fraud %",
        f"{fraud_percent:.2f}%"
    )
     
    st.subheader("📈 Risk Distribution")

    risk_counts = (
    df["Risk Level"]
    .value_counts()
    .reset_index()
)

    risk_counts.columns = [
    "Risk Level",
    "Count"
]

    import plotly.express as px


# Donut Chart
    fig = px.pie(
    risk_counts,
    names="Risk Level",
    values="Count",
    hole=0.55,
    title="📊 Risk Distribution",
    color="Risk Level",
    color_discrete_map={
        "Low": "#28a745",      # Green
        "Medium": "#ffc107",   # Yellow
        "High": "#dc3545"      # Red
    }
)

# Show labels and percentages
    fig.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
)

# Total transactions
    total_transactions = len(df)

# Layout improvements
    fig.update_layout(
    title_x=0.35,
    legend_title="Risk Level",
    font=dict(size=14),
    annotations=[
        dict(
            text=f"<b>{total_transactions}</b><br>Transactions",
            x=0.5,
            y=0.5,
            font_size=20,
            showarrow=False
        )
    ]
)

# Display chart
    st.plotly_chart(
    fig,
    use_container_width=True
)
    low_count = (df["Risk Level"] == "Low").sum()
    medium_count = (df["Risk Level"] == "Medium").sum()
    high_count = (df["Risk Level"] == "High").sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("🟢 Low", low_count)
    col2.metric("🟡 Medium", medium_count)
    col3.metric("🔴 High", high_count)
  
#downloadable file

    csv = df.to_csv(index=False)

    st.download_button(
        "Download Results",
        csv,
        "fraud_analysis.csv",
        "text/csv"
    )
    st.success(
    f"""
    Analysis Complete!

    Transactions Analyzed: {len(df)}
    Fraud Transactions Detected: {frauds}
    """
)

#conclusions

    if fraud_percent < 1:
       st.success("✅ Transaction batch appears healthy")

    elif fraud_percent < 5:
      st.warning("⚠️ Elevated fraud activity detected")

    else:
      st.error("🚨 High fraud activity detected")

#sidebar
    st.sidebar.title("🛡️ AI FraudShield")

    st.sidebar.markdown("""
### Model Information

**Algorithm:** Random Forest

**Features:** 30

**Explainability:** SHAP

**Framework:** Streamlit
""")

    st.sidebar.markdown("---")

    st.sidebar.success("System Ready")

    st.caption(
    "AI FraudShield | Random Forest + Explainable AI | Built by Aayushi Sud"
)