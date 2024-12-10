import pandas as pd
import streamlit as st
import plotly.express as px

# โหลดข้อมูล
@st.cache_data
def load_data():
    # raw GitHub
    df1_url = "https://raw.githubusercontent.com/Siamrat27/Projected_DataSci/main/csv_file/combined_data_2018_2023.csv"
    df2_url = "https://raw.githubusercontent.com/Siamrat27/Projected_DataSci/main/csv_file/final_data_prep_2024.csv"
    prediction_url = "https://raw.githubusercontent.com/Siamrat27/Projected_DataSci/main/csv_file/predictions_output.csv"

    df1 = pd.read_csv(df1_url)
    df2 = pd.read_csv(df2_url)
    prediction_df = pd.read_csv(prediction_url)

    # รวมข้อมูล 2018-2024
    combined_df = pd.concat([df1, df2], ignore_index=True)
    return combined_df, prediction_df

historical_df, prediction_df = load_data()

# แปล column
historical_df['country'] = historical_df['country'].str.strip().str.capitalize()
prediction_df['country'] = prediction_df['country'].str.strip().str.capitalize()

# Sidebar
st.sidebar.title("Settings")
analysis_type = st.sidebar.radio("Select Data Range", ["Historical Data (2018-2024)", "Prediction for 2025"])

if analysis_type == "Historical Data (2018-2024)":
    selected_years = st.sidebar.multiselect(
        "Select Years ",  
        options=sorted(historical_df['year'].unique()), 
        default=sorted(historical_df['year'].unique())  # Default to select all years
    )
    selected_country = st.sidebar.selectbox(
        "Select Country 🌍",
        options=sorted(historical_df['country'].unique())
    )
else:  # Choose Prediction 2025
    selected_country = st.sidebar.selectbox(
        "Select Country 🌍",
        options=sorted(prediction_df['country'].unique())
    )

chart_type = st.sidebar.radio("Choose Chart Type 📊", ["Bar Chart", "Pie Chart", "Heatmap"])

# Main Content
if analysis_type == "Historical Data (2018-2024)":
    st.title(f"Research Analysis for {selected_country} 🗺️")
    # กรองข้อมูล 2018-2024 ตามประเทศและปีที่เลือก
    filtered_data = historical_df[
        (historical_df['country'] == selected_country) &
        (historical_df['year'].isin(selected_years))
    ]

    if not filtered_data.empty:
        # Group ข้อมูลตาม Subject Area และ ปี
        pivot_data = filtered_data.pivot_table(
            index='subject_area_abbrev', 
            columns='year', 
            values='article_amount', 
            aggfunc='sum'
        )

        # Visualization
        if chart_type == "Bar Chart":
            st.subheader("Bar Chart 📶")
            fig = px.bar(
                filtered_data.groupby('subject_area_abbrev')['article_amount']
                .sum()
                .reset_index(),
                x='subject_area_abbrev',
                y='article_amount',
                color='subject_area_abbrev',
                labels={'subject_area_abbrev': 'Subject Area', 'article_amount': 'Article Count'},
                title=f"Top Research Areas in {selected_country} ({', '.join(map(str, selected_years))}) 🔍"
            )
            fig.update_traces(textposition='outside', textfont_size=12)
            st.plotly_chart(fig)

        elif chart_type == "Pie Chart":
            st.subheader("Pie Chart 🥧")
            fig = px.pie(
                filtered_data.groupby('subject_area_abbrev')['article_amount']
                .sum()
                .reset_index(),
                names='subject_area_abbrev',
                values='article_amount',
                title=f"Research Area Distribution in {selected_country} ({', '.join(map(str, selected_years))})",
                hole=0.4
            )
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig)

        elif chart_type == "Heatmap":
            st.subheader("Heatmap 🔥")
            fig = px.imshow(
                pivot_data,
                labels=dict(x="Year", y="Subject Area", color="Article Count"),
                title=f"Heatmap: Article Count by Year and Subject Area for {selected_country}"
            )
            st.plotly_chart(fig)
    else:
        st.warning(f"No data available for {selected_country}.")

elif analysis_type == "Prediction for 2025":
    st.title(f"Prediction for {selected_country} (2025) 🤔")
    # กรองข้อมูลเฉพาะประเทศที่เลือก
    filtered_prediction = prediction_df[prediction_df['country'] == selected_country]

    if not filtered_prediction.empty:
        # Group ข้อมูลตาม Subject Area
        prediction_summary = (
            filtered_prediction.groupby('subject_area_abbrev')['article_amount']
            .sum()
            .reset_index()
            .sort_values('article_amount', ascending=False)
        )

        # Visualization
        if chart_type == "Bar Chart":
            st.subheader("Bar Chart 📶")
            fig = px.bar(
                prediction_summary,
                x='subject_area_abbrev',
                y='article_amount',
                text='article_amount',
                color='subject_area_abbrev',
                labels={'subject_area_abbrev': 'Subject Area', 'article_amount': 'Predicted Article Count'},
                title=f"Predicted Top Research Areas for {selected_country} (2025) 🔍"
            )
            fig.update_traces(textposition='outside', textfont_size=12)
            st.plotly_chart(fig)

        elif chart_type == "Pie Chart":
            st.subheader("Pie Chart 🥧")
            fig = px.pie(
                prediction_summary,
                names='subject_area_abbrev',
                values='article_amount',
                title=f"Predicted Research Area Distribution in {selected_country} (2025)",
                hole=0.4
            )
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig)

        elif chart_type == "Heatmap":
            st.warning(f"No Heatmap available for 2025 Prediction.")

        # Display Probability Details
        st.subheader("Prediction Details with Probability (Raw Data)")
        detailed_df = filtered_prediction[['subject_area_abbrev', 'article_amount', 'prediction', 'probability']].copy()
        detailed_df['probability'] = detailed_df['probability'].apply(lambda x: ', '.join([f"{p:.2%}" for p in eval(x)]))
        st.dataframe(detailed_df)
    else:
        st.warning(f"No prediction data available for {selected_country} in 2025.")