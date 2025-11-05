import streamlit as st
import pandas as pd
import csv
import time
import math

# ==============================================================
#                   📘 CSV Resource Loader
# ==============================================================
def load_resources(csv_path: str):
    """Loads investment options CSV file."""
    resources = []
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    cagr = float(row.get("CAGR_10Y_%", "")) if row.get("CAGR_10Y_%", "") else None
                except ValueError:
                    cagr = None
                resources.append({
                    "type": row.get("Type", "").strip(),
                    "name": row.get("Name", "").strip(),
                    "cagr_10y": cagr
                })
    except FileNotFoundError:
        st.error("⚠️ CSV file not found. Please check the path.")
    return resources


def get_top_items(resources, category: str, top_n: int = 3):
    """Fetches top N items by CAGR for a given category."""
    cat = category.strip().lower()
    filtered = [r for r in resources if r["type"].lower() == cat]
    filtered.sort(key=lambda x: (x["cagr_10y"] is None, -x["cagr_10y"] if x["cagr_10y"] else 0))
    return filtered[:top_n]

# ==============================================================
#                   💰 Investment Logic
# ==============================================================
def investment_advice(income, expenses, age, risk_level, occupation, knowledge, dependents, debt):
    """AI decides investment allocation based on multiple factors."""
    savings = income - expenses - debt
    if savings <= 0:
        return {"error": "Your savings after expenses and debts are insufficient for investment!"}

    # Base ratio
    if risk_level.lower() == "high":
        ratio = {"Stocks": 0.45, "Mutual Funds": 0.30, "Gold": 0.10, "Insurance": 0.05, "Emergency Fund": 0.10}
    elif risk_level.lower() == "moderate":
        ratio = {"Stocks": 0.30, "Mutual Funds": 0.30, "Gold": 0.10, "Insurance": 0.10, "Emergency Fund": 0.20}
    else:
        ratio = {"Stocks": 0.20, "Mutual Funds": 0.25, "Gold": 0.10, "Insurance": 0.20, "Emergency Fund": 0.25}

    # Adjust for age/dependents/occupation
    if age > 50 or dependents > 3:
        ratio["Stocks"] -= 0.10
        ratio["Insurance"] += 0.05
        ratio["Emergency Fund"] += 0.05
    if occupation.lower() in ["business", "freelancer"]:
        ratio["Emergency Fund"] += 0.05
        ratio["Mutual Funds"] -= 0.05
    if knowledge.lower() == "beginner":
        ratio["Stocks"] -= 0.05
        ratio["Mutual Funds"] += 0.05

    # Normalize and allocate
    total_ratio = sum(ratio.values())
    ratio = {k: v / total_ratio for k, v in ratio.items()}
    allocations = {k: round(v * savings, 2) for k, v in ratio.items()}
    return allocations

# ==============================================================
#               📈 Compounding + Step-Up Growth
# ==============================================================
def compound_with_stepup(principal, rate, years, monthly_addition=0, step_up_rate=0):
    """Future value with monthly compounding and salary step-up (annual growth)."""
    r = rate / 12
    total = principal
    monthly_investment = monthly_addition

    for month in range(int(years * 12)):
        total = total * (1 + r) + monthly_investment
        if (month + 1) % 12 == 0:
            monthly_investment *= (1 + step_up_rate)
    return round(total, 2)


# ==============================================================
#                   🌐 Streamlit App
# ==============================================================
st.set_page_config(page_title="AI Finance Advisor 4.0", layout="centered")

st.title("🤖 AI Finance Advisor 4.0")
st.caption("Powered by real CAGR data and personalized AI-driven insights")

# ✅ Load CSV
csv_path = r"investment_resources_custom.csv"
resources = load_resources(csv_path)
data = pd.read_csv(csv_path)

# --------------------------------------------------------------
# Tabs
# --------------------------------------------------------------
tab1, tab2 = st.tabs(["📊 Personalized Plan", "📈 Stock / Mutual Fund Explorer"])

# ==============================================================
# TAB 1: Personalized Plan
# ==============================================================
with tab1:
    st.header("📊 Build Your Personalized Investment Plan")

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("🎂 Age", 18, 100, 30)
        income = st.number_input("💰 Monthly income (₹)", min_value=1000.0, value=50000.0)
        expenses = st.number_input("💸 Monthly expenses (₹)", min_value=0.0, value=25000.0)
        debt = st.number_input("💳 Monthly EMI / Debt (₹)", min_value=0.0, value=5000.0)
        dependents = st.number_input("👨‍👩‍👧 Number of dependents", 0, 10, 1)
    with col2:
        occupation = st.selectbox("💼 Occupation", ["Job", "Business", "Freelancer", "Student"])
        knowledge = st.selectbox("🧠 Financial knowledge", ["Beginner", "Intermediate", "Expert"])
        risk_level = st.select_slider("⚖️ Risk tolerance", ["Low", "Moderate", "High"])
        step_up = st.slider("📈 Expected annual salary growth (%)", 0, 20, 5) / 100
        years = st.slider("⏳ Investment duration (years)", 1, 40, 15)

    goal = st.text_input("🎯 Your main goal (e.g., Retirement, Education, Wealth Growth)")
    goal_amount = st.number_input("💰 Target goal amount (₹)", min_value=0.0, value=1000000.0)
    existing_savings = st.number_input("🏦 Existing savings (₹)", min_value=0.0, value=100000.0)

    if st.button("🚀 Generate My Investment Plan"):
        with st.spinner("Analyzing your financial profile..."):
            time.sleep(1.5)

        plan = investment_advice(income, expenses, age, risk_level, occupation, knowledge, dependents, debt)
        if "error" in plan:
            st.error(plan["error"])
        else:
            total_savings = income - expenses - debt
            st.success(f"✅ Monthly investable savings: ₹{total_savings:,.2f}")

            st.subheader("📊 Recommended Portfolio Allocation")
            st.bar_chart(pd.DataFrame(plan.values(), index=plan.keys(), columns=["Amount (₹)"]))

            returns_rate = {"Stocks": 0.15, "Mutual Funds": 0.13, "Gold": 0.09, "Insurance": 0.05, "Emergency Fund": 0.03}
            total_future_value = 0

            st.subheader("📈 Projected Future Value (with salary growth)")
            for k, monthly_amt in plan.items():
                fv = compound_with_stepup(0, returns_rate[k], years, monthly_amt, step_up)
                total_future_value += fv
                st.write(f"• {k}: ₹{fv:,.2f} after {years} years")

            st.success(f"💰 Total Projected Wealth: ₹{total_future_value:,.2f}")

            st.info("💡 AI Insights:\n- Keep 6 months of expenses as Emergency Fund.\n- Review portfolio annually.\n- Stay invested long-term!")

            st.subheader("🔝 Top Investment Suggestions (by CAGR)")
            for category in plan.keys():
                cat_map = {"Stocks": "Stock", "Mutual Funds": "Mutual Fund", "Gold": "Gold", "Insurance": "Insurance", "Emergency Fund": "Other"}
                top_items = get_top_items(resources, cat_map[category])
                if top_items:
                    st.markdown(f"**{category}**")
                    for i, item in enumerate(top_items, 1):
                        st.write(f"{i}. {item['name']} — CAGR: {item['cagr_10y']}%")
                else:
                    st.write(f"No data for {category}")

# ==============================================================
# TAB 2: Stock / Mutual Fund Explorer
# ==============================================================
with tab2:
    st.header("📈 Explore Stocks and Mutual Funds")

    category = st.selectbox("Choose investment type", ["Stock", "Mutual Fund"])
    filtered = data[data["Type"] == category]

    st.dataframe(filtered[["Name", "CAGR_10Y_%"]].sort_values("CAGR_10Y_%", ascending=False).reset_index(drop=True))

    selected = st.selectbox(f"Select a {category}", filtered["Name"].unique())
    amount = st.number_input("💵 Investment amount (₹)", min_value=1000.0, value=10000.0)
    years = st.slider("⏳ Investment period (years)", 1, 40, 10)

    if st.button("📊 Calculate Growth"):
        rate = filtered[filtered["Name"] == selected]["CAGR_10Y_%"].values[0]
        final_value = amount * ((1 + rate / 100) ** years)
        profit = final_value - amount

        st.success(f"✅ {selected} — CAGR: {rate}%")
        st.metric("Future Value", f"₹{final_value:,.2f}", delta=f"₹{profit:,.2f} Profit")

        st.progress(min(final_value / (amount * 3), 1.0))
