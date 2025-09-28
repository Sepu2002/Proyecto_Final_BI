import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# --- Variables Globales ---
# Definición del diccionario de colores para pydeck
COLOR_MAPPING = {
    'Positivo': [0, 128, 0, 180],    # Verde
    'Negativo': [255, 0, 0, 180],    # Rojo
    'Neutral': [255, 255, 0, 180],   # Amarillo
}

# --------------------------------------------------------------------------------------
# FUNCIÓN DE GENERACIÓN DE DATOS SIMULADOS (Mock Data)
# Nota: En una aplicación real, esta función se reemplazaría por la lectura de tus datos
# de Yelp, Google Maps y la aplicación de tu modelo de NLP.
# --------------------------------------------------------------------------------------
def generate_mock_data(num_businesses=100):
    """Genera datos simulados para negocios de detailing en Florida."""
    np.random.seed(42)

    # Coordenadas aproximadas para simular ubicaciones en Florida (alrededor de Orlando, Tampa, Miami)
    latitudes = np.random.uniform(25.7, 30.5, num_businesses)
    longitudes = np.random.uniform(-82.8, -80.1, num_businesses)

    # Datos de Sentimiento y Calificación
    sentiments = np.random.choice(['Positivo', 'Negativo', 'Neutral'], num_businesses, p=[0.55, 0.25, 0.20])
    ratings = np.random.choice([3.0, 3.5, 4.0, 4.5, 5.0], num_businesses, p=[0.05, 0.1, 0.35, 0.3, 0.2])

    data = pd.DataFrame({
        'name': [f'Detailing Pro {i}' for i in range(num_businesses)],
        'lat': latitudes,
        'lon': longitudes,
        'sentiment': sentiments,
        'rating': ratings,
        'review_count': np.random.randint(10, 500, num_businesses)
    })
    
    # Añadir la columna RGB para PyDeck
    data['color'] = data['sentiment'].apply(lambda x: COLOR_MAPPING[x])
    
    return data