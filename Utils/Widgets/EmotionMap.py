import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk




# --------------------------------------------------------------------------------------
# FUNCIÓN DE VISUALIZACIÓN DEL MAPA
# --------------------------------------------------------------------------------------
def render_map_viz(df):
    """Renderiza la visualización del mapa de Florida con puntos coloreados por emoción."""

    # 1. Definir la vista inicial del mapa (centrado en Florida)
    view_state = pdk.ViewState(
        latitude=28.5,
        longitude=-81.5,
        zoom=6,
        pitch=40,
    )

    # 2. Definir la capa de Scatterplot
    # Usa la columna 'color' que creamos en el dataframe
    # Usa el conteo de reseñas para el radio del punto
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"],
        auto_highlight=True,
        get_fill_color="color",  # Usa la columna 'color' (RGB) para el color de relleno
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
        # *** CORRECCIÓN: Se eliminó el map_style que requería Mapbox token ***
        tooltip={
            "html": "<b>Negocio:</b> {name}<br><b>Rating:</b> {rating} estrellas<br><b>Emoción:</b> {sentiment}<br><b>Reseñas:</b> {review_count}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
    )

    st.pydeck_chart(r)



def show_emotion_map_dashboard(df_data):
    # --------------------------------------------------------------------------------------
    # CUERPO PRINCIPAL DEL DASHBOARD
    # --------------------------------------------------------------------------------------
    st.title("🗺️ Visualización 1: Mapa de Sentimiento de Reseñas en Florida")
    st.markdown("---")

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

    st.info(f"Mostrando {len(df_filtered)} negocios de detailing en el mapa según los filtros seleccionados.")

    # --- Renderizar el Mapa ---
    render_map_viz(df_filtered)

    # --- Leyenda del Mapa ---
    st.markdown("""
    <div style="padding: 10px; border: 1px solid #ccc; border-radius: 8px; margin-top: 20px;">
        <strong>Leyenda de Emociones:</strong>
        <ul>
            <li><span style="color: green; font-weight: bold;">■ POSITIVO:</span> Alta satisfacción del cliente (Oportunidad para aprender y replicar el éxito).</li>
            <li><span style="color: red; font-weight: bold;">■ NEGATIVO:</span> Baja satisfacción del cliente (Área de oportunidad inmediata / Focos rojos).</li>
            <li><span style="color: orange; font-weight: bold;">■ NEUTRAL:</span> Reseñas ambiguas o promedio (Potencial para mejorar fácilmente).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
