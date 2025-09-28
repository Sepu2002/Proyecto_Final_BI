import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# --------------------------------------------------------------------------------------
# FUNCIÓN DE VISUALIZACIÓN DEL MAPA
# --------------------------------------------------------------------------------------
def show_emotion_map_dashboard(df_filtered):
   
    st.subheader("🗺️ Mapa de Sentimiento de Reseñas en Florida")

    # Filtramos los datos que tengan coordenadas válidas
    df_valid = df_filtered.dropna(subset=['latitude', 'longitude'])

    st.info(f"Mostrando **{len(df_valid)}** negocios de detailing en el mapa (de {len(df_filtered)} filtrados).")

    # --- Renderizar el Mapa ---
    if not df_valid.empty:
        render_map_viz(df_valid)
    else:
        st.warning("No hay negocios con coordenadas válidas para mostrar en el mapa.")

    # --- Leyenda del Mapa ---
    st.markdown("""
    <div style="padding: 10px; border: 1px solid #ccc; border-radius: 8px; margin-top: 20px;">
        <strong>Leyenda de Emociones (Sentimiento Dominante):</strong>
        <ul>
            <li><span style="color: green; font-weight: bold;">■ POSITIVO:</span> Sentimiento general positivo en las reseñas.</li>
            <li><span style="color: red; font-weight: bold;">■ NEGATIVO:</span> Sentimiento general negativo en las reseñas (Foco Rojo).</li>
            <li><span style="color: orange; font-weight: bold;">■ NEUTRAL:</span> Sentimiento mixto o falta de predominancia (Oportunidad).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# FUNCIÓN DE CREACIÓN DEL MAPA
# --------------------------------------------------------------------------------------
def render_map_viz(df):

    # Calcular el centro del mapa dinámicamente
    avg_lat = df['latitude'].mean()
    avg_lon = df['longitude'].mean()

    # 1. Definir la vista inicial del mapa (centrado en los datos)
    view_state = pdk.ViewState(
        latitude=avg_lat,
        longitude=avg_lon,
        zoom=7,  # Un poco más de zoom para Florida
        pitch=40,
    )

    # 2. Definir la capa de Scatterplot
    # Usa la columna 'color' y el 'review_count' del negocio
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["longitude", "latitude"], # Asegurar el orden lon, lat
        auto_highlight=True,
        get_fill_color="color",  # Usa la columna 'color' (RGB)
        get_line_color=[0, 0, 0],
        get_radius="review_count / 10", # Radio basado en el volumen de reseñas
        radius_scale=2,
        radius_min_pixels=5,
        radius_max_pixels=100,
        pickable=True, # Hace los puntos interactivos
    )

    # 3. Crear el deck con el tooltip
    r = pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>Negocio:</b> {name}<br><b>Rating Histórico:</b> {rating} estrellas<br><b>Sentimiento Dominante:</b> {dominant_sentiment}<br><b>Reseñas Totales:</b> {review_count}",
            "style": {"backgroundColor": "#1E90FF", "color": "white"}
        }
    )

    st.pydeck_chart(r)
