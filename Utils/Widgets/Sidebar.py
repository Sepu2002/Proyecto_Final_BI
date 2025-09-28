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

# Inicializador de estado de la sesión (se sigue usando para que los toggles mantengan su estado)
def _initialize_sentiment_state():
    """Inicializa el estado de la sesión para los filtros de sentimiento."""
    if 'selected_positivo' not in st.session_state:
        st.session_state['selected_positivo'] = True
    if 'selected_neutral' not in st.session_state:
        st.session_state['selected_neutral'] = True
    if 'selected_negativo' not in st.session_state:
        st.session_state['selected_negativo'] = True


def create_sidebar_filter(df_data):
    """Crea la barra lateral con opciones de filtrado y el botón de descarga."""
    
    _initialize_sentiment_state()
    
    # --- Sidebar para filtros ---
    st.sidebar.header("Opciones de Filtrado")

    # Filtro 1: Emoción/Sentimiento de la Reseña - Usando toggles verticales
    st.sidebar.markdown("##### Filtrar por Emoción:")
    
    # Usamos st.toggle que se comporta como un botón selector nativo de Streamlit
    # y lo almacenamos en st.session_state para que mantenga su estado.
    
    # Botón Positivo
    st.session_state['selected_positivo'] = st.sidebar.toggle(
        "Positivo 🟢", 
        value=st.session_state['selected_positivo'], 
        key="toggle_positivo",
        help="Mostrar reseñas con sentimiento Positivo (Éxito)."
    )
    
    # Botón Neutral
    st.session_state['selected_neutral'] = st.sidebar.toggle(
        "Neutral 🟡", 
        value=st.session_state['selected_neutral'], 
        key="toggle_neutral",
        help="Mostrar reseñas con sentimiento Neutral (Oportunidad)."
    )

    # Botón Negativo
    st.session_state['selected_negativo'] = st.sidebar.toggle(
        "Negativo 🔴", 
        value=st.session_state['selected_negativo'], 
        key="toggle_negativo",
        help="Mostrar reseñas con sentimiento Negativo (Foco Rojo)."
    )

    # --- Recolectar las emociones seleccionadas para el filtrado ---
    selected_sentiments = []
    if st.session_state['selected_positivo']:
        selected_sentiments.append('Positivo')
    if st.session_state['selected_negativo']:
        selected_sentiments.append('Negativo')
    if st.session_state['selected_neutral']:
        selected_sentiments.append('Neutral')

    if not selected_sentiments:
         st.sidebar.warning("Ninguna emoción seleccionada. El mapa estará vacío.")
        
    # Filtro 2: Calificación de Estrellas
    min_rating = st.sidebar.slider(
        "Calificación Mínima ⭐:",
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
    
    COLOR_MAPPING = {
    'Positivo': [0, 128, 0, 180],    # Verde
    'Negativo': [255, 0, 0, 180],    # Rojo
    'Neutral': [255, 255, 0, 180],   # Amarillo
    }

    # Añadir la columna RGB para PyDeck
    df_filtered['color'] = df_filtered['sentiment'].apply(lambda x: COLOR_MAPPING[x])

    return df_filtered