import streamlit as st
import joblib
import pandas as pd

model = joblib.load("notebook/fraud_model.pkl")

st.title("AI FraudShield")
st.subheader("Credit Card Fraud Detection System")

uploaded_file = st.file_uploader(
    "Upload Transaction CSV",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    if "Class" in df.columns:
        df = df.drop("Class", axis=1)

    # Save clean features for prediction
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

    fraud_df = df[df["Prediction"] == "Fraud"]
    st.subheader("🚨 Suspicious Transactions")

    st.dataframe(fraud_df)

    frauds = (df["Prediction"] == "Fraud").sum()

    st.metric(
        "Fraud Transactions Detected",
        frauds
    )

    fraud_percent = (frauds / len(df)) * 100

    st.metric(
        "Fraud Percentage",
        f"{fraud_percent:.2f}%"
    )

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

    csv = df.to_csv(index=False)

    st.download_button(
        "Download Results",
        csv,
        "fraud_analysis.csv",
        "text/csv"
    )