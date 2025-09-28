import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import os

# Importar las funciones de procesamiento de datos y visualización
from Utils.Data.sentiment_analysis import main as run_sentiment_analysis
from Utils.Widgets.EmotionMap import show_emotion_map_dashboard
from Utils.Widgets.Sidebar import create_sidebar_filter
from Utils.Widgets.WordCloudViz import show_word_cloud_dashboard
from Utils.Widgets.Leaderboard import show_leaderboard

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

# ----------------------------------------------------
# FASE DE CARGA Y PROCESAMIENTO DE DATOS (ML)
# ----------------------------------------------------
# La función run_sentiment_analysis devuelve el DataFrame de negocios fusionado 
# (para mapa/ranking) y el DataFrame detallado de reseñas (para la nube de palabras).
df_merged, df_detailed_reviews = run_sentiment_analysis()

# Si los datos no se cargaron correctamente, salimos
if df_merged is None or df_detailed_reviews is None:
    st.error("No se pudieron cargar o procesar los datos para el dashboard.")
    st.stop()


# ----------------------------------------------------
# FASE DE FILTRADO
# ----------------------------------------------------
# Filtramos los datos de negocios (df_merged) para el mapa y el leaderboard
df_filtered = create_sidebar_filter(df_merged)
# Creamos una columna temporal de Business IDs para filtrar las reseñas
filtered_business_ids = df_filtered['business_id'].unique()
# Filtramos las reseñas detalladas según la selección del negocio
df_detailed_reviews_filtered = df_detailed_reviews[
    df_detailed_reviews['business_id'].isin(filtered_business_ids)
]


# ----------------------------------------------------
# FASE DE VISUALIZACIÓN
# ----------------------------------------------------

# FILA 1: Mapa y Nube de Palabras
col_mapa, col_nube = st.columns([1, 1])

with col_mapa:
    # Visualización 1: Mapa de Emoción
    show_emotion_map_dashboard(df_filtered)

with col_nube:
    # Visualización 2: Nube de Palabras
    # Pasamos las reseñas filtradas
    show_word_cloud_dashboard(df_detailed_reviews_filtered)

st.markdown("---") 

# FILA 2: Ranking Activo
# Visualización 3: Ranking de Competidores
# Pasamos los datos filtrados para que el ranking refleje solo la selección actual
show_leaderboard(df_filtered)
