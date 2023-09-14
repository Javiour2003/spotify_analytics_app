import plotly.express as px
import streamlit as st

def feature_plot(features,theta):
    fig = px.line_polar(features,r=(features.values).reshape(-1),
                        theta=theta,
                        line_close=True,
                        template="plotly_dark",
                        color_discrete_sequence=['green'],
                        title='Feature Plot',
                        width=750, height=600)
    # Display the radar chart
    st.plotly_chart(fig)
        
    