
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt

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

total_unsc_removal = df['unscheduled_removal'].sum()
total_components = df['component_name'].nunique()
total_downtime = df['downtime_hours'].sum()

# MTBUR
mtbur = df.groupby('component_name').apply(
    lambda x: x['hours_since_install'].sum() / max(x['unscheduled_removal'].sum(), 1))

# Best and worst component
best_idx = mtbur.idxmax()
worst_idx = mtbur.idxmin()


col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Unscheduled Removal (2024)", total_unsc_removal)
col2.metric("Total Components", total_components)
col3.metric("Total Downtime Hours", round(total_downtime,2))
col4.metric("Best Component (Highest MTBUR)", best_idx)
col5.metric("Worst Component (Lowest MTBUR)", worst_idx)

# ==========================
# Charts Section
# ==========================
st.header("Charts Section")

col1, col2 = st.columns(2)
with col1:
# 1. Unschedulued Removal per Month
    df['month'] = pd.to_datetime(df['failure_date']).dt.strftime('%b')
    # order the month
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct','Nov','Dec']
    df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)
    monthly_failure = df.groupby('month')['unscheduled_removal'].sum().reset_index()
   
    st.subheader("Unschedulued Removal per Month")
    
    fig1 = px.bar(
        monthly_failure,
        x="month",
        y="unscheduled_removal",
        labels={"unscheduled_removal": "Unscheduled Removal Count", "month": "Month"},
        color_discrete_sequence=["navy"],
        height=400 
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
# 2. Failure Count per ATA Chapter
    df['ata_chapter'] = df['ata_chapter'].astype(str)
    failure_per_ata = df.groupby('ata_chapter')['unscheduled_removal'].sum().reset_index()

    st.subheader("Unschedulued Removal per ATA")
    chart = alt.Chart(failure_per_ata).mark_bar(color="navy").encode(
        x=alt.X('ata_chapter:N', title = 'ATA', axis = alt.Axis(labelAngle=0)),
        y=alt.Y('unscheduled_removal:Q', title='Unscheduled Removal Count')).properties(height=400)
    st.altair_chart(chart)

# 3. Pareto Chart – Unscheduled Removal per Component
st.subheader("Pareto Chart – Unscheduled Removal per Component")

# Pareto
pareto = df.groupby('component_name')['unscheduled_removal'].sum().sort_values(ascending=False)
# cumulative percentage
cumulative_percent = pareto.cumsum()/pareto.sum()*100

fig = go.Figure()

# bar chart
fig.add_trace(
    go.Bar(
        x = pareto.index,
        y = pareto.values,
        name="Unschedule Removal",
        yaxis = "y1",
        marker_color = "navy"
    )
)

# line chart for cumulative (%)
fig.add_trace(
    go.Scatter(
        x = pareto.index,
        y = cumulative_percent,
        name = "Cumulative %",
        mode="lines+markers",
        yaxis="y2",
        line = dict(width=2),
        marker_color = "gold"
    )
)

# layout
fig.update_layout(
    xaxis = dict(title = "Component"),
    
    yaxis = dict(
    title = "Failure Count",
    side = "left"
    ),
    
    yaxis2 = dict(
    title = "Cumulative %",
    overlaying = "y",
    side = "right",
    range = [0,110]
    ),
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# 4. Avg Downtime per Component (MTTR)
avg_downtime = df.groupby('component_name')['downtime_hours'].mean()
avg_downtime = avg_downtime.sort_values(ascending=False)

st.subheader("Mean Time To Repair (MTTR)")
fig = px.bar(
    x = avg_downtime.index,
    y = avg_downtime.values,
    labels = {"x":"Component", "y": "Downtime Hours"},
    color_discrete_sequence = ["navy"]
)
st.plotly_chart(fig, use_container_width = True)

# 5. MTBUR per Component
mtbur1 = mtbur.sort_values(ascending=False)
st.subheader("MTBUR per Component")
fig = px.bar(
    x = mtbur.index,
    y = mtbur.values,
    labels = {"x": "Component", "y":"MTBUR"},
    color_discrete_sequence = ["navy"]
)
st.plotly_chart(fig)


# 6. MTBUR vs MTTR Scatter
st.subheader("MTBUR vs MTTR")
mttr = df.groupby('component_name')['downtime_hours'].mean()

scatter_df = pd.DataFrame({
    "component_name": mtbur.index,
    "MTBUR": mtbur.values,
    "MTTR": mttr.values
})

fig = px.scatter(
    scatter_df,
    x="MTBUR",
    y="MTTR",
    text="component_name",
    labels={"MTBUR": "MTBUR", "MTTR": "MTTR"},
    color_discrete_sequence=["navy"]
)

# component_name in scatter
fig.update_traces(marker = dict(size=12), textposition='top center')

st.plotly_chart(fig, use_container_width=True)



# 7. Reliability Trend per Component
st.subheader("Reliability Trend per Component")
components = st.multiselect("Select Components", df['component_name'].unique(), default=df['component_name'].unique()[:1])
for comp in components:
    trend = df[df["component_name"]==comp].groupby("month")["unscheduled_removal"].sum()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x = trend.index,
            y = trend.values,
            mode = "lines",
            marker_color = "navy",
            line = dict(width=2)
        )
    )
    fig.update_layout(
        xaxis = dict(title = "Month"),
        yaxis = dict(title = "Unscheduled Removal", side = "left"),
        height = 300
    )
    st.plotly_chart(fig, use_container_width=True)


# 8. Age vs Removal
st.subheader("Age Distribution: Removed vs Not Removed")
fig = px.box(
    df,
    x="unscheduled_removal",
    y="hours_since_install",
    color="unscheduled_removal",
    labels={
        "unscheduled_removal": "",
        "hours_since_install": "Hours Since Install"},
    category_orders = {'unscheduled_removal':[0, 1]},
)

# change name for 0 and 1 to not removed and removed
fig.update_xaxes(
    tickvals=[0, 1],
    ticktext = ["Not Removed", "Removed"]
)
st.plotly_chart(fig, use_container_width=True)



# ==========================
# Component Detail Explorer
# ==========================

st.header("Component Detail Explorer")

selected_comp = st.selectbox("Select Component", df['component_name'].unique())
comp_data = df[df['component_name']==selected_comp]

st.write(f"**Total Unscheduled Removal:** {comp_data['unscheduled_removal'].sum()}")
st.write(f"**Total Downtime Hours:** {comp_data['downtime_hours'].sum()}")
comp_mtbur = comp_data['hours_since_install'].sum() / max(comp_data['unscheduled_removal'].sum(),1)
st.write(f"**MTBUR:** {comp_mtbur:.2f}")

# Life Histogram per Component
fig= px.histogram(
    comp_data,
    x = "hours_since_install", 
    nbins = 15,
    labels = {"hours_since_install": "Hours Since Install"},
    title = "Life Distribution"
)
fig.update_traces(marker_color="navy", marker_line_width=1, marker_line_color="white")
fig.update_layout(
    xaxis = dict(showgrid= True),
    yaxis = dict(showgrid= True),
    bargap = 0.02
)
st.plotly_chart(fig, use_container_width=True)

# Trend per month
monthly_trend = comp_data.groupby('month')['unscheduled_removal'].sum()
fig = px.line(
    x = monthly_trend.index,
    y = monthly_trend.values,
    labels ={"x":"Month", "y": "Unscheduled Removal Count"},
    color_discrete_sequence=["navy"],
    height = 300,
    title = "Unscheduled Removal Trend"
)
st.plotly_chart(fig, use_container_width = True)

st.markdown("""
**Note:** This dataset is **synthetic** and is for **learning and demonstration purpose only**.
It does **not represent real aircrat maintenance data**.
""")
