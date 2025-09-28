import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# --------------------------------------------------------------------------------------
# FUNCIÓN DE VISUALIZACIÓN DEL MAPA
# --------------------------------------------------------------------------------------
def show_emotion_map_dashboard(df_filtered):
   
    st.header("🗺️ Mapa de Sentimiento de Reseñas en Florida") # <-- CAMBIADO DE st.title a st.header

    # Se verifica si el DataFrame filtrado tiene datos y coordenadas válidas
    if df_filtered.empty or df_filtered['lat'].isnull().all() or df_filtered['lon'].isnull().all():
        st.warning("⚠️ No hay negocios con coordenadas válidas que coincidan con los filtros seleccionados para mostrar en el mapa.")
        return

    st.info(f"Mostrando **{len(df_filtered)}** negocios de detailing en el mapa según los filtros seleccionados.")

    # --- Renderizar el Mapa ---
    render_map_viz(df_filtered)

    # --- Leyenda del Mapa ---
    st.markdown("""
    <div style="padding: 10px; border: 1px solid #ccc; border-radius: 8px; margin-top: 20px;">
        <strong>Leyenda de Emociones (Basada en ML):</strong>
        <ul>
            <li><span style="color: green; font-weight: bold;">■ POSITIVO:</span> Alta satisfacción del cliente (Oportunidad de replicar el éxito).</li>
            <li><span style="color: red; font-weight: bold;">■ NEGATIVO:</span> Baja satisfacción del cliente (Foco rojo de mejora inmediata).</li>
            <li><span style="color: orange; font-weight: bold;">■ NEUTRAL:</span> Reseñas ambiguas o promedio (Potencial de fácil conversión a positivo).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# FUNCIÓN DE CREACIÓN DEL MAPA
# --------------------------------------------------------------------------------------
def render_map_viz(df):

    # Calculamos el centro del mapa dinámicamente basado en los datos filtrados
    # Usamos np.mean para obtener el promedio de latitud y longitud
    center_lat = df['lat'].mean()
    center_lon = df['lon'].mean()
    
    # 1. Definir la vista inicial del mapa
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=7, # Aumentamos el zoom para ver mejor los negocios en Florida
        pitch=40,
    )

    # 2. Definir la capa de Scatterplot
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"], # PyDeck espera [longitude, latitude]
        auto_highlight=True,
        get_fill_color="color",  # Usa la columna 'color' (RGB)
        get_line_color=[0, 0, 0, 100], # Borde de punto semitransparente
        get_radius="review_count / 8", # Radio basado en el volumen de reseñas (ajustado)
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
            "html": "<b>Negocio:</b> {name}<br><b>Rating:</b> {rating} estrellas<br><b>Emoción:</b> {dominant_sentiment}<br><b>Reseñas Totales:</b> {review_count}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
    )

    st.pydeck_chart(r)
