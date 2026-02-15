import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

if st.button("🎮 Back to the game"):
    st.switch_page("pages/Game.py")

st.switch_page("pages/Game.py")

st.markdown("---")
if st.button("📊 Explore the data yourself", use_container_width=True):
    st.switch_page("pages/Explorer.py")