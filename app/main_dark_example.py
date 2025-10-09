"""
Example main.py for Report 9 with Dark Mode
This demonstrates how to enable dark mode in your report
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration variables that the ConfigManager will detect
template_iesb = True  # Enable MIV template
dark_mode = True      # Enable dark mode for Report 9

def main():
    st.title("Report 9 - Dark Mode Example")
    
    # Create some sample data
    data = {
        'Category': ['A', 'B', 'C', 'D', 'E'],
        'Values': [23, 45, 56, 78, 32],
        'Secondary': [12, 34, 45, 23, 67]
    }
    df = pd.DataFrame(data)
    
    # Display data
    st.subheader("Sample Data")
    st.dataframe(df)
    
    # Create a chart that works well with dark mode
    fig = px.bar(df, x='Category', y='Values', 
                 title='Sample Bar Chart',
                 color_discrete_sequence=['#D13F42'])  # MIV Red
    
    # Update chart for dark mode compatibility
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#FAFAFA'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Sidebar content
    st.sidebar.header("Report Controls")
    st.sidebar.info("This report is running in dark mode!")
    
    # Some metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Values", sum(df['Values']))
    with col2:
        st.metric("Average", round(df['Values'].mean(), 2))
    with col3:
        st.metric("Max Value", max(df['Values']))

if __name__ == "__main__":
    main()
