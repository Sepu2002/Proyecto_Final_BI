import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk  

def create_sidebar_filter(df_data):
    """Crea la barra lateral con opciones de filtrado."""
    # --- Sidebar para filtros ---
    st.sidebar.header("Opciones de Filtrado")

    # Filtro 1: Emoción/Sentimiento de la Reseña
    selected_sentiments = st.sidebar.multiselect(
        "Filtrar por Emoción:",
        options=['Positivo', 'Negativo', 'Neutral'],
        default=['Positivo', 'Negativo', 'Neutral'],
        help="Selecciona qué tipo de emoción de reseña quieres visualizar."
    )

    # Filtro 2: Calificación de Estrellas
    min_rating = st.sidebar.slider(
        "Calificación Mínima (Estrellas de Yelp):",
        min_value=3.0,
        max_value=5.0,
        value=3.0,
        step=0.5
    )

    # --- Aplicar Filtros ---
    df_filtered = df_data[df_data['sentiment'].isin(selected_sentiments)]
    df_filtered = df_filtered[df_filtered['rating'] >= min_rating]
    return df_filtered