import pandas as pd
import os
import re
import streamlit as st 
# Importaciones necesarias de scikit-learn para el análisis de sentimientos (ML)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# --- Rutas de los Archivos ---
@st.cache_data
def load_data():
    REVIEWS_FILE = 'Datasets/reviews.csv'
    BUSINESSES_FILE = 'Datasets/businesses.csv'
    
    try:
        # Forzamos 'text' a string para evitar errores en el vectorizador
        df_reviews = pd.read_csv(REVIEWS_FILE, dtype={'text': str}) 
        df_businesses = pd.read_csv(BUSINESSES_FILE)
        return df_reviews, df_businesses
    except FileNotFoundError as e:
        # Se detiene si los archivos esenciales no se encuentran
        st.error(f"❌ Error al cargar archivos. Asegúrate de que '{e.filename}' exista en la carpeta 'Datasets'.")
        return pd.DataFrame(), pd.DataFrame()

# --------------------------------------------------------------------------------------
# FUNCIÓN DE ENTRENAMIENTO Y PREDICCIÓN DE SENTIMIENTO (Machine Learning)
# --------------------------------------------------------------------------------------

@st.cache_data
def train_and_predict_sentiment(df_reviews):
    """
    Entrena un modelo de clasificación de sentimiento y lo aplica a todas las reseñas.
    
    El modelo se entrena usando el rating como verdad fundamental para generar las etiquetas.
    La predicción final se basa únicamente en el texto.
    """
    
    st.info("⚙️ Entrenando modelo de Machine Learning (Logistic Regression) para análisis de sentimiento...")

    df = df_reviews.copy()
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    
    # 1. GENERACIÓN DE ETIQUETAS (Ground Truth basado en Rating)
    # Usamos el rating para crear etiquetas de entrenamiento para el modelo.
    def create_ml_label(rating):
        if rating >= 4.0:
            return 'Positivo'
        elif rating <= 2.0:
            return 'Negativo'
        else: # 3.0
            return 'Neutral'

    df['ml_label'] = df['rating'].apply(create_ml_label)
    
    # Manejar textos nulos o vacíos
    df['text'] = df['text'].fillna('')
    
    # 2. DATOS DE ENTRENAMIENTO
    X = df['text']
    y = df['ml_label']
    
    # 3. CREACIÓN Y ENTRENAMIENTO DEL PIPELINE DE ML
    # TfidfVectorizer: Convierte texto a vectores de características numéricas.
    # LogisticRegression: Modelo clasificador simple y robusto.
    model_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words=None, ngram_range=(1, 2), max_features=2000)),
        ('clf', LogisticRegression(random_state=42, max_iter=200))
    ])

    try:
        model_pipeline.fit(X, y)
        st.success("✔️ Modelo de ML entrenado correctamente.")
        
        # 4. PREDICCIÓN DEL SENTIMIENTO REAL (solo con el texto)
        df['sentiment'] = model_pipeline.predict(df['text'])
    except Exception as e:
        st.error(f"❌ Error durante el entrenamiento del modelo de ML: {e}")
        # En caso de error, volvemos a la clasificación simple por rating
        df['sentiment'] = df['ml_label']
        st.warning("⚠️ Se ha revertido a la clasificación simple por rating debido a un error de ML.")

    # Devolvemos solo las columnas de interés del análisis detallado
    return df[['business_id', 'text', 'sentiment', 'time_created', 'rating']]


# --------------------------------------------------------------------------------------
# FUNCIÓN DE CONSOLIDACIÓN DE DATOS (Usa la columna 'sentiment' generada por el ML)
# --------------------------------------------------------------------------------------
def create_business_summary(df_detailed_reviews):
    """
    Genera la tabla de resumen: business_id, num_reviews y los 3 sentimientos.
    """
    
    # Contar el número de reseñas por negocio y sentimiento
    df_sentiment_counts = df_detailed_reviews.groupby(['business_id', 'sentiment']).size().reset_index(name='count')
    
    # Pivoteamos la tabla para que los sentimientos sean columnas
    df_pivot = df_sentiment_counts.pivot_table(
        index='business_id', 
        columns='sentiment', 
        values='count', 
        fill_value=0
    )
    
    # Añadir la columna de número total de reviews
    df_pivot['num_reviews'] = df_pivot.sum(axis=1)
    
    # Reordenar y renombrar las columnas para el formato final
    df_final = df_pivot.reset_index()
    
    # Asegurar que las 3 columnas de sentimiento existan (incluso si están vacías)
    required_sentiment_cols = ['Positivo', 'Negativo', 'Neutral']
    for col in required_sentiment_cols:
        if col not in df_final.columns:
            df_final[col] = 0

    # Seleccionar y reordenar las columnas finales
    df_final = df_final[['business_id', 'num_reviews', 'Positivo', 'Negativo', 'Neutral']]
    df_final.columns = ['business_id', 'num_reviews', 'sentiment_positivo', 'sentiment_negativo', 'sentiment_neutral']
    
    # Calcular el sentimiento dominante para el mapeo
    df_final['dominant_sentiment'] = df_final[['sentiment_positivo', 'sentiment_negativo', 'sentiment_neutral']].idxmax(axis=1).str.replace('sentiment_', '', regex=False)
    
    return df_final


# --------------------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL - Devuelve los DataFrames listos para el dashboard
# --------------------------------------------------------------------------------------
def main():
    st.markdown("## ⚙️ Generación de Base de Datos de Sentimiento (Machine Learning)")
    st.markdown("---")
    
    # 1. Cargar todos los datos
    df_reviews, df_businesses = load_data()
    
    if df_reviews.empty or df_businesses.empty:
        # No se pudo cargar, devolvemos None
        return None, None

    # 2. Aplicar análisis de sentimiento (ML)
    df_detailed_reviews = train_and_predict_sentiment(df_reviews)
    
    # 3. Crear el resumen por negocio 
    df_summary = create_business_summary(df_detailed_reviews)
    st.info(f"Base de datos de sentimiento consolidada para **{len(df_summary)}** negocios.")
    
    # 4. INTEGRACIÓN Y LIMPIEZA DE DATOS (Para Dashboard)
    
    # Seleccionamos columnas relevantes de negocios (incluyendo latitud/longitud)
    df_coords = df_businesses[['business_id', 'name', 'latitude', 'longitude', 'rating', 'review_count']].copy()
    
    # *** CORRECCIÓN CLAVE: Renombrar para PyDeck y asegurar tipo numérico ***
    df_coords.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
    df_coords['lat'] = pd.to_numeric(df_coords['lat'], errors='coerce')
    df_coords['lon'] = pd.to_numeric(df_coords['lon'], errors='coerce')

    # Unimos el resumen de sentimiento con las coordenadas de negocio y el review_count de Yelp
    df_merged = pd.merge(df_summary, df_coords, on='business_id', how='left')

    # *** CORRECCIÓN CLAVE 2: Eliminar filas con coordenadas nulas antes de mapear ***
    df_merged.dropna(subset=['lat', 'lon'], inplace=True)
    
    # Añadir el color para PyDeck (usando el sentimiento dominante)
    COLOR_MAPPING = {
        'Positivo': [0, 128, 0, 180],    # Verde
        'Negativo': [255, 0, 0, 180],    # Rojo
        'Neutral': [255, 255, 0, 180],   # Amarillo
    }
    df_merged['color'] = df_merged['dominant_sentiment'].apply(lambda x: COLOR_MAPPING.get(x, [128, 128, 128, 180]))
    
    # 5. Guardar el resumen de sentimientos
    OUTPUT_FILE = 'business_sentiment.csv'
    OUTPUT_PATH = os.path.join('Datasets', OUTPUT_FILE)

    try:
        # Asegurarse de que solo se guardan las columnas de resumen
        df_summary.to_csv(OUTPUT_PATH, index=False)
        st.success(f"✔️ Base de datos de sentimiento (por negocio) guardada en: **{OUTPUT_PATH}**")
    except Exception as e:
        st.error(f"❌ Error al guardar el archivo: {e}")

    # Devolvemos el dataframe de negocios (fusionado) y los reviews detallados
    return df_merged, df_detailed_reviews


if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Análisis de Sentimiento (ML)", page_icon="📝")
    main()
