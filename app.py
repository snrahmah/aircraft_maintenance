
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("Aircraft Maintenance Dashboard 2024")

# ==========================
# Load Dataset
# ==========================
df = pd.read_csv("maintenance_data.csv")

# ==========================
# Summary KPIs
# ==========================
st.header("Summary KPIs")
total_failures = df['unscheduled_removal'].sum()
total_components = df['component_name'].nunique()
total_downtime = df['downtime_hours'].sum()

mtbur = df.groupby('component_name').apply(
    lambda x: x['hours_since_install'].sum() / max(x['unscheduled_removal'].sum(), 1))
best_component = mtbur.idxmax()
worst_component = mtbur.idxmin()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Failures (2024)", total_failures)
col2.metric("Total Components", total_components)
col3.metric("Total Downtime Hours", round(total_downtime,2))
col4.metric("Best Component (Highest MTBUR)", best_component)
col5.metric("Worst Component (Lowest MTBUR)", worst_component)

# ==========================
# Charts Section
# ==========================
st.header("Charts Section")

col1, col2 = st.columns(2)
with col1:
    # 1. Failure Trend per Month
    df['month'] = pd.to_datetime(df['failure_date']).dt.strftime('%b')
    # order the month
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct','Nov','Dec']
    df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)
    monthly_failure = df.groupby('month')['unscheduled_removal'].sum()
    st.subheader("Failure Trend per Month")
    st.bar_chart(monthly_failure, use_container_width=True)

with col2:
    # 2. Failure Count per ATA Chapter
    failure_per_ata = df.groupby('ata_chapter')['unscheduled_removal'].sum()
    st.subheader("Failure Count per ATA Chapter")
    st.bar_chart(failure_per_ata, use_container_width=True)

# 3. Avg Downtime per Component
avg_downtime = df.groupby('component_name')['downtime_hours'].mean()
st.subheader("Average Downtime Hours per Component")
st.bar_chart(avg_downtime)

# 4. MTBUR per Component
st.subheader("MTBUR per Component")
st.bar_chart(mtbur)

# 5. Pareto Chart – Unscheduled Removal per Component
st.subheader("Pareto Chart – Unscheduled Removal per Component")

# Pareto
pareto = df.groupby('component_name')['unscheduled_removal'].sum().sort_values(ascending=False)
# cumulative percentage
cumulative_percent = pareto.cumsum()/pareto.sum()*100

fig, ax = plt.subplots(figsize=(8,4))
ax.bar(pareto.index, pareto.values)
ax2 = ax.twinx()
ax2.plot(pareto.index, cumulative_percent, color='red', marker='o', ms=5)
ax2.set_ylabel("Cumulative %")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig)

# 6. Reliability Trend per Component
st.subheader("Reliability Trend per Component")
components = st.multiselect("Select Components", df['component_name'].unique(), default=df['component_name'].unique()[:3])
for comp in components:
    trend = df[df['component_name']==comp].groupby('month')['unscheduled_removal'].sum()
    st.line_chart(trend, height=250, use_container_width=True)

# 7. Age vs Failures Scatter
st.subheader("Age Distribution: Removed vs Not Removed")
fig, ax = plt.subplot(figsize=(6,4))
sns.boxplot(x='unscheduled_removal', y='hours_since_install', data=df, ax=ax1, pallete="pastel")
ax.set_xticklabel(["Not Removed", "Removed"])
ax.set_ylabel("Hours Since Install")
ax.set_xlabel("")
st.pyplot(fig)

# 8. Life Distribution Histogram
st.subheader("Life Distribution of Components")
fig, ax = plt.subplots()
ax.hist(df['hours_since_install'], bins=20, color='skyblue', edgecolor='black')
ax.set_xlabel("Hours Since Install")
ax.set_ylabel("Count")
st.pyplot(fig)

# 9. MTBUR vs MTTR Scatter
st.subheader("MTBUR vs MTTR")
avg_downtime_per_comp = df.groupby('component_name')['downtime_hours'].mean()
fig, ax = plt.subplots()
ax.scatter(mtbur, avg_downtime_per_comp)
for i, txt in enumerate(mtbur.index):
    ax.annotate(txt, (mtbur[i], avg_downtime_per_comp[i]))
ax.set_xlabel("MTBUR")
ax.set_ylabel("Average Downtime (MTTR)")
st.pyplot(fig)

# ==========================
# Component Detail Explorer
# ==========================
st.header("Component Detail Explorer")
selected_comp = st.selectbox("Select Component", df['component_name'].unique())
comp_data = df[df['component_name']==selected_comp]
st.write(f"**Total Failures:** {comp_data['unscheduled_removal'].sum()}")
st.write(f"**Total Downtime Hours:** {comp_data['downtime_hours'].sum()}")
comp_mtbur = comp_data['hours_since_install'].sum() / max(comp_data['unscheduled_removal'].sum(),1)
st.write(f"**MTBUR:** {comp_mtbur:.2f}")

# Life Histogram per Component
fig, ax = plt.subplots()
ax.hist(comp_data['hours_since_install'], bins=15, color='lightgreen', edgecolor='black')
ax.set_xlabel("Hours Since Install")
ax.set_ylabel("Count")
st.pyplot(fig)

# Trend per month
monthly_trend = comp_data.groupby('month')['unscheduled_removal'].sum()
st.line_chart(monthly_trend)

st.markdown("""
---
**Note:** This dataset is **synthetic** and is for **learning and demonstration purpose only**.
It does **not represent real aircrat maintenance data**.
""")
