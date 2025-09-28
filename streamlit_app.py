import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

from Utils.Data.GenMockData import generate_mock_data
from Utils.Widgets.EmotionMap import render_map_viz
from Utils.Widgets.EmotionMap import show_emotion_map_dashboard
from Utils.Widgets.Sidebar import create_sidebar_filter

# --- Configuración de la Página de Streamlit ---
st.set_page_config(layout="wide", page_title="Shiny Stats: Dashboard de BI Automotriz", page_icon="🚗")


# Cargar los datos simulados
df_data = generate_mock_data()

df_filtered = create_sidebar_filter(df_data)

# Mostrar el dashboard del mapa de emociones
show_emotion_map_dashboard(df_filtered)

