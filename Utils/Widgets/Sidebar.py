import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk  

# Helper function to convert DataFrame to CSV for download
# La columna 'color' es para visualización y se elimina para una descarga limpia.
def convert_df_to_csv(df):
    if 'color' in df.columns:
        # Se elimina la columna de color para el archivo de descarga
        df_download = df.drop(columns=['color']) 
    else:
        df_download = df.copy()
    
    # Convierte el DataFrame a una cadena CSV codificada en UTF-8
    return df_download.to_csv(index=False).encode('utf-8')

def create_sidebar_filter(df_data):
    """Crea la barra lateral con opciones de filtrado y el botón de descarga."""
    # --- Sidebar para filtros ---
    st.sidebar.header("Opciones de Filtrado")

    # Filtro 1: Emoción/Sentimiento de la Reseña - Usando toggle buttons
    st.sidebar.markdown("##### Filtrar por Emoción:")
    
    # Usar st.sidebar.columns para alinear los toggle buttons horizontalmente
    col1, col2, col3 = st.sidebar.columns(3)

    # st.toggle devuelve True/False. El valor por defecto es True para mostrar todo al inicio.
    with col1:
        toggle_positivo = st.toggle("Positivo 🟢", value=True, help="Mostrar reseñas con sentimiento Positivo.")
    with col2:
        toggle_neutral = st.toggle("Neutral 🟡", value=True, help="Mostrar reseñas con sentimiento Neutral.")
    with col3:
        toggle_negativo = st.toggle("Negativo 🔴", value=True, help="Mostrar reseñas con sentimiento Negativo.")

    # Recolectar las emociones seleccionadas
    selected_sentiments = []
    if toggle_positivo:
        selected_sentiments.append('Positivo')
    if toggle_negativo:
        selected_sentiments.append('Negativo')
    if toggle_neutral:
        selected_sentiments.append('Neutral')

    if not selected_sentiments:
         st.sidebar.warning("Ninguna emoción seleccionada. El mapa estará vacío.")
        
    # Filtro 2: Calificación de Estrellas
    min_rating = st.sidebar.slider(
        "Calificación Mínima (Estrellas de Yelp):",
        min_value=1.0,
        max_value=5.0,
        value=1.0,
        step=0.5
    )

    # --- Aplicar Filtros ---
    # Aplica el filtro de emoción. Si selected_sentiments está vacío, df_filtered será vacío.
    df_filtered = df_data[df_data['sentiment'].isin(selected_sentiments)]
    
    # Aplica el filtro de rating al resultado.
    df_filtered = df_filtered[df_filtered['rating'] >= min_rating]

    # --- Botón de Descarga ---
    
    # 1. Convertir el DataFrame filtrado a CSV
    csv_data = convert_df_to_csv(df_filtered)
    
    # Separador visual en el sidebar
    st.sidebar.markdown("---") 

    # 2. Agregar el botón de descarga a la barra lateral
    st.sidebar.download_button(
        label="Descargar Datos Filtrados (.csv) ⬇️",
        data=csv_data,
        file_name='shiny_stats_datos_filtrados.csv',
        mime='text/csv',
        help="Descarga la base de datos de negocios con los filtros de la barra lateral aplicados."
    )
    
    return df_filtered