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
        min_value=1.0,
        max_value=5.0,
        value=1.0,
        step=0.5
    )

    # --- Aplicar Filtros ---
    df_filtered = df_data[df_data['sentiment'].isin(selected_sentiments)]
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