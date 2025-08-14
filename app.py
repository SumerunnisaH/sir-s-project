import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Movement Lab - Student Fitness Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ML_school_testing_clean.csv")
    # Add derived metrics
    df['BMI_Category'] = pd.cut(df['BMI'], bins=[0, 18.5, 25, 30, 100],
                                labels=['Underweight', 'Normal', 'Overweight', 'Obese'])
    return df

df = load_data()

# -----------------------------
# Sidebar - Branding & Filters
# -----------------------------
st.sidebar.image("https://via.placeholder.com/150/0047AB/FFFFFF?text=Movement+Lab", width=120)
st.sidebar.title("Movement Lab")
st.sidebar.markdown("### Student Fitness Analytics")

st.sidebar.markdown("---")
st.sidebar.header("Filters")

# Dropdown: Select one or more students
student_names = df['Name'].tolist()
selected_students = st.sidebar.multiselect(
    "Select Students",
    options=student_names,
    default=student_names
)

# Dropdown: BMI Category Filter
bmi_options = ['All'] + df['BMI_Category'].dropna().unique().tolist()
selected_bmi = st.sidebar.selectbox("Filter by BMI Category", options=bmi_options)

# Apply Filters
filtered_df = df[df['Name'].isin(selected_students)]
if selected_bmi != 'All':
    filtered_df = filtered_df[filtered_df['BMI_Category'] == selected_bmi]

# -----------------------------
# Main Title
# -----------------------------
st.title("📊 Movement Lab Fitness Dashboard")
st.markdown("### Empowering young athletes with data-driven insights")

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏋️ Strength & Flexibility", "📏 Javelin Performance", "📋 Data Explorer"])

# -----------------------------
# Tab 1: Overview
# -----------------------------
with tab1:
    st.header("Student Fitness Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Students", len(filtered_df))
    with col2:
        avg_bmi = filtered_df['BMI'].mean()
        st.metric("Avg BMI", f"{avg_bmi:.1f}")
    with col3:
        avg_grip = filtered_df['Rel_Grip_perKg'].mean()
        st.metric("Avg Relative Grip", f"{avg_grip:.2f}")
    with col4:
        max_squat = filtered_df['LB_Squat_1min_reps'].max()
        st.metric("Max Squat (reps)", int(max_squat))

    # BMI Distribution
    fig_bmi = px.histogram(filtered_df, x='BMI', nbins=10, title="BMI Distribution",
                           color_discrete_sequence=['#0047AB'])
    fig_bmi.update_layout(xaxis_title="BMI", yaxis_title="Count")
    st.plotly_chart(fig_bmi, use_container_width=True)

# -----------------------------
# Tab 2: Strength & Flexibility
# -----------------------------
with tab2:
    st.header("Strength and Flexibility Analysis")

    # Add Relative Strength
    filtered_df = filtered_df.copy()
    filtered_df['Rel_Strength_perKg'] = filtered_df['UB_Strength_kg'] / filtered_df['Weight_kg']

    # Sort by Name for cleaner plotting
    filtered_df = filtered_df.sort_values('Name')

    # Plot 1: Flexibility
    fig_flex = px.bar(
        filtered_df,
        x='Name',
        y='Flexibility_cm',
        title="Flexibility (cm)",
        labels={'Flexibility_cm': 'Flexibility (cm)'},
        color='Flexibility_cm',
        color_continuous_scale='Blues',
        text='Flexibility_cm'
    )
    fig_flex.update_traces(texttemplate='%{text:.1f} cm', textposition='outside')
    fig_flex.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',
                           yaxis={'showticklabels': True},
                           xaxis_tickangle=45)
    st.plotly_chart(fig_flex, use_container_width=True)

    # Plot 2: Absolute Upper Body Strength
    fig_abs = px_bar = px.bar(
        filtered_df,
        x='Name',
        y='UB_Strength_kg',
        title="Absolute Upper Body Strength (kg)",
        labels={'UB_Strength_kg': 'Strength (kg)'},
        color='UB_Strength_kg',
        color_continuous_scale='Reds',
        text='UB_Strength_kg'
    )
    fig_abs.update_traces(texttemplate='%{text:.1f} kg', textposition='outside')
    fig_abs.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',
                          xaxis_tickangle=45)
    st.plotly_chart(fig_abs, use_container_width=True)

    # Plot 3: Relative Strength (Strength per kg body weight)
    fig_rel = px.bar(
        filtered_df,
        x='Name',
        y='Rel_Strength_perKg',
        title="Relative Strength (UB Strength / BMI)",
        labels={'Rel_Strength_perKg': 'Relative Strength (kg/kg)'},
        color='Rel_Strength_perKg',
        color_continuous_scale='Greens',
        text='Rel_Strength_perKg'
    )
    fig_rel.update_traces(texttemplate='%{text:.3f}', textposition='outside')
    fig_rel.update_layout(
        yaxis_tickformat='.3f',
        xaxis_tickangle=45
    )
    st.plotly_chart(fig_rel, use_container_width=True)

    # Optional: Data table
    st.subheader("Detailed Metrics")
    display_cols = ['Name', 'Flexibility_cm', 'UB_Strength_kg', 'Weight_kg', 'Rel_Strength_perKg']
    st.dataframe(
        filtered_df[display_cols].round(3).style.format({
            'Rel_Strength_perKg': '{:.3f}',
            'UB_Strength_kg': '{:.1f}',
            'Flexibility_cm': '{:.1f}',
            'Weight_kg': '{:.1f}'
        }),
        use_container_width=True)
# -----------------------------
# Tab 3: Medicine Ball Overhead Throw
# -----------------------------
with tab3:
    st.header("Medicine Ball Overhead Throw Performance")

    # Best vs Mean throw
    fig_mb = go.Figure()
    fig_mb.add_trace(go.Scatter(
        x=filtered_df['MB_OH_Best_m'],
        y=filtered_df['Name'],
        mode='markers',
        name='Best Throw',
        marker=dict(size=10, color='blue')
    ))
    fig_mb.add_trace(go.Scatter(
        x=filtered_df['MB_OH_Mean_m'],
        y=filtered_df['Name'],
        mode='markers',
        name='Mean Throw',
        marker=dict(size=10, color='lightblue')
    ))
    fig_mb.update_layout(
        title="Best vs Mean Overhead Throw (m)",
        xaxis_title="Distance (m)",
        yaxis_title="Student",
        yaxis={'categoryorder':'total ascending'},
        height=max(400, len(filtered_df) * 30)
    )
    st.plotly_chart(fig_mb, use_container_width=True)

    # Trials count
    fig_trials = px.pie(filtered_df, names='MB_OH_Trials', title="Number of Trials Conducted",
                        hole=0.4, color_discrete_sequence=['#0047AB', '#6CA6CD'])
    st.plotly_chart(fig_trials, use_container_width=True)

# -----------------------------
# Tab 4: Data Explorer
# -----------------------------
with tab4:
    st.header("Raw Data Explorer")
    st.dataframe(filtered_df.style.format({
        'Height_cm': '{:.1f}',
        'Weight_kg': '{:.1f}',
        'BMI': '{:.2f}',
        'Rel_Grip_perKg': '{:.3f}'
    }), use_container_width=True)


    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(filtered_df)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name='movement_lab_filtered_data.csv',
        mime='text/csv',
    )

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")

st.markdown("🔍 *Movement Lab — Fitness Intelligence for Young Athletes* | Data last updated: Aug 2025")
