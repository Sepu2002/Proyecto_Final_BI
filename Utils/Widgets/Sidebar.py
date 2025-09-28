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

# Inicializador de estado de la sesión
def _initialize_sentiment_state():
    """Inicializa el estado de la sesión para los filtros de sentimiento."""
    if 'selected_positivo' not in st.session_state:
        st.session_state['selected_positivo'] = True
    if 'selected_neutral' not in st.session_state:
        st.session_state['selected_neutral'] = True
    if 'selected_negativo' not in st.session_state:
        st.session_state['selected_negativo'] = True

# Handler para cambiar el estado al hacer click en el botón
def _toggle_sentiment_state(key):
    """Invierte el estado de la clave de sentimiento en st.session_state."""
    st.session_state[key] = not st.session_state[key]


def create_sidebar_filter(df_data):
    """Crea la barra lateral con opciones de filtrado y el botón de descarga."""
    
    _initialize_sentiment_state()
    
    # --- Sidebar para filtros ---
    st.sidebar.header("Opciones de Filtrado")

    # Filtro 1: Emoción/Sentimiento de la Reseña - Usando botones de selección
    st.sidebar.markdown("##### Filtrar por Emoción:")
    
    col1, col2, col3 = st.sidebar.columns(3)

    # --- INYECCIÓN CSS para estilizar los botones (solución Streamlit Hack) ---
    # Esto es necesario para aplicar colores personalizados a los botones en función de su estado.
    CSS = """
    <style>
        /* Estilo general para los botones de sentimiento en la barra lateral */
        div[data-testid="stSidebar"] div.stButton > button {
            border-radius: 8px;
            font-weight: bold;
            border: 1px solid #ccc;
            padding: 5px 10px;
            width: 100%; /* Para que llenen el ancho de la columna */
            transition: all 0.2s; /* Transición suave al cambiar de estado */
        }
        
        /* === POSITIVO Button Styles === */
        /* Estilo para botón Positivo NO SELECCIONADO (borde verde, texto verde) */
        div[data-testid="stSidebar"] div.stButton > button:has(div > p:contains("Positivo")):not(:has(div > p:contains("(ON)"))) {
            background-color: #F5F5F5; 
            color: #4CAF50; /* Verde */
            border-color: #4CAF50;
        }
        /* Estilo para botón Positivo SELECCIONADO (relleno verde, texto blanco) */
        div[data-testid="stSidebar"] div.stButton > button:has(div > p:contains("Positivo (ON)")) {
            background-color: #4CAF50; 
            color: white;
            border-color: #4CAF50;
        }

        /* === NEUTRAL Button Styles === */
        /* Estilo para botón Neutral NO SELECCIONADO (borde amarillo, texto amarillo/naranja) */
        div[data-testid="stSidebar"] div.stButton > button:has(div > p:contains("Neutral")):not(:has(div > p:contains("(ON)"))) {
            background-color: #F5F5F5; 
            color: #FFC107; /* Amarillo/Naranja */
            border-color: #FFC107;
        }
        /* Estilo para botón Neutral SELECCIONADO (relleno amarillo, texto negro) */
        div[data-testid="stSidebar"] div.stButton > button:has(div > p:contains("Neutral (ON)")) {
            background-color: #FFC107; 
            color: black;
            border-color: #FFC107;
        }

        /* === NEGATIVO Button Styles === */
        /* Estilo para botón Negativo NO SELECCIONADO (borde rojo, texto rojo) */
        div[data-testid="stSidebar"] div.stButton > button:has(div > p:contains("Negativo")):not(:has(div > p:contains("(ON)"))) {
            background-color: #F5F5F5; 
            color: #F44336; /* Rojo */
            border-color: #F44336;
        }
        /* Estilo para botón Negativo SELECCIONADO (relleno rojo, texto blanco) */
        div[data-testid="stSidebar"] div.stButton > button:has(div > p:contains("Negativo (ON)")) {
            background-color: #F44336; 
            color: white;
            border-color: #F44336;
        }
    </style>
    """
    st.markdown(CSS, unsafe_allow_html=True)

    # --- Positivo Button ---
    with col1:
        is_selected = st.session_state['selected_positivo']
        st.button(
            # Se añade (ON) al label para que el CSS pueda identificar el estado seleccionado
            label=f"Positivo {'(ON)' if is_selected else ''}", 
            key="btn_positivo",
            on_click=_toggle_sentiment_state,
            args=['selected_positivo'],
            help="Activar/Desactivar el filtro de sentimiento Positivo."
        )
    
    # --- Neutral Button ---
    with col2:
        is_selected = st.session_state['selected_neutral']
        st.button(
            label=f"Neutral {'(ON)' if is_selected else ''}",
            key="btn_neutral",
            on_click=_toggle_sentiment_state,
            args=['selected_neutral'],
            help="Activar/Desactivar el filtro de sentimiento Neutral."
        )

    # --- Negativo Button ---
    with col3:
        is_selected = st.session_state['selected_negativo']
        st.button(
            label=f"Negativo {'(ON)' if is_selected else ''}",
            key="btn_negativo",
            on_click=_toggle_sentiment_state,
            args=['selected_negativo'],
            help="Activar/Desactivar el filtro de sentimiento Negativo."
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