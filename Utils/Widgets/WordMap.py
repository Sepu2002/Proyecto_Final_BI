import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import io

# Definición de Stopwords en inglés
# Combinamos las STOPWORDS estándar con términos comunes en el contexto de detailing/reseñas
ENGLISH_STOPWORDS = set(STOPWORDS) | {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 
    'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 
    'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 
    'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 
    'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 
    'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 
    'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 
    'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 
    'again', 'further', 'then', 'once', 'here', 'there', 'when', 
    'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 
    'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 
    'can', 'will', 'just', 'don', 'should', 'now',
    
    # Palabras específicas del contexto de detailing que probablemente no aportan valor
    'car', 'vehicle', 'auto', 'truck', 'my car', 'service', 'time', 
    'place', 'shop', 'job', 'they', 'get', 'got', 'day', 'work', 
    'did', 'was', 'were', 'really', 'much', 'so', 'had', 'looks',
    'new', 'definitely', 'like', 'would', 'also', 'back', 'detailing', 'detail', 'great', 'good', 'amazing'
}

def load_reviews_data():
    """Carga y limpia el dataset de reseñas con sentimiento."""
    try:
        # Usamos el dataset reviews_con_sentimiento.csv como lo solicitaste
        df = pd.read_csv('Datasets/reviews_con_sentimiento.csv')
        
        # Estandarizar la columna 'sentiment'
        df['sentiment'] = df['sentiment'].str.title()
        
        # Asegurar que la columna de texto exista y sea una cadena
        df['text'] = df['text'].astype(str)
        return df
    except FileNotFoundError:
        st.error("Error: El archivo 'reviews_con_sentimiento.csv' no se encontró. Asegúrate de que esté en la carpeta 'Datasets'.")
        return pd.DataFrame()

def show_word_map(df_reviews, selected_sentiment):
    """
    Genera y muestra el WordCloud para el sentimiento seleccionado.
    """
    if df_reviews.empty:
        st.warning("No se puede generar el mapa de palabras: el DataFrame de reseñas está vacío.")
        return

    # 1. Filtrar reseñas por el sentimiento seleccionado
    if selected_sentiment == "Todas":
        df_filtered = df_reviews
        title_suffix = "Todas las Reseñas"
    else:
        # Nota: La columna 'sentiment' se estandariza a Title case en load_reviews_data
        df_filtered = df_reviews[df_reviews['sentiment'] == selected_sentiment]
        title_suffix = f"Emoción: {selected_sentiment}"

    st.subheader(f"📈 Tendencias de Palabras Clave ({title_suffix})")

    if df_filtered.empty:
        st.info(f"No hay reseñas con sentimiento '{selected_sentiment}' para generar el mapa de palabras.")
        return

    # 2. Concatenar todo el texto
    text_combined = " ".join(review for review in df_filtered['text'])

    if not text_combined.strip():
        st.info("El texto filtrado está vacío o solo contiene caracteres de espacio.")
        return

    # 3. Crear el objeto WordCloud
    wordcloud = WordCloud(
        stopwords=ENGLISH_STOPWORDS, # AHORA USAMOS LAS STOPWORDS EN INGLÉS
        background_color="white",
        width=800,
        height=400,
        colormap='viridis',  # Un mapa de color atractivo
        max_words=100
    ).generate(text_combined)

    # 4. Mostrar la imagen en Streamlit
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)


def word_map_dashboard(df_reviews):
    """
    Componente del dashboard que permite al usuario seleccionar el sentimiento
    y llama a la función de generación del WordCloud.
    """
    st.markdown("---") 
    st.header("🔍 Análisis de Tendencias por Emoción (Word Map)")
    st.markdown("Selecciona una categoría de emoción para visualizar las palabras más frecuentes en las reseñas correspondientes. Esto ayuda a entender las quejas y elogios específicos.")
    
    # Opciones del selector
    sentiment_options = ["Todas", "Positivo", "Negativo", "Neutral"]
    
    # Selector de sentimiento
    selected_sentiment = st.selectbox(
        "Filtrar el mapa de palabras por tipo de Emoción:",
        options=sentiment_options,
        index=0,
        key="wordmap_sentiment_selector"
    )

    # Generar y mostrar el WordCloud
    show_word_map(df_reviews, selected_sentiment)
