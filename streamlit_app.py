import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

from Utils.Data.GenMockData import generate_mock_data
from Utils.Widgets.EmotionMap import render_map_viz
from Utils.Widgets.EmotionMap import show_emotion_map_dashboard
from Utils.Widgets.Sidebar import create_sidebar_filter
from Utils.Widgets.Leaderboard import show_leaderboard
from Utils.Widgets.WordMap import load_reviews_data # Importar la nueva función de carga
from Utils.Widgets.WordMap import update_word_map_with_filters # Nueva función para usar filtros de sidebar

# --- Configuración de la Página de Streamlit ---
st.set_page_config(layout="wide", page_title="Shiny Stats: Dashboard de BI Automotriz", page_icon="🚗")

# --- ENCABEZADO PRINCIPAL ---
st.title("✨ Shiny Stats: Dashboard de Inteligencia de Negocios Automotriz 🚗")
st.markdown("""
    **Transformando el Detailing en Florida con Data Science.**
    Análisis de sentimientos en reseñas de Yelp para **identificar quejas**, 
    optimizar la experiencia del cliente y obtener una ventaja competitiva.
""")
st.markdown("---") 
# ---------------------------

# Cargar los datos de negocios (para Mapa y Leaderboard)
df_data_businesses = pd.read_csv('Datasets/businesses_con_sentimiento.csv') 

# Cargar los datos de reseñas (para WordMap)
# Nota: Este DataFrame contiene TODAS las reseñas y no está filtrado.
df_data_reviews = load_reviews_data()


# 1. Sidebar y Filtrado para el Mapa
# La barra lateral filtra 'df_data_businesses' (negocios)
df_filtered_businesses = create_sidebar_filter(df_data_businesses)

# 2. Mostrar el dashboard del mapa de emociones (usa df_filtered_businesses)
show_emotion_map_dashboard(df_filtered_businesses)

# 3. Word Map de Tendencias (utiliza los negocios filtrados por la sidebar)
update_word_map_with_filters(df_filtered_businesses, df_data_reviews)

# 4. Leaderboard de Ranking (usa df_filtered_businesses)
st.markdown("---") # Separador para mejor visualización
show_leaderboard(df_filtered_businesses)