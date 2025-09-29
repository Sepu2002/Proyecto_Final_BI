import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import re
from collections import Counter
from nltk.util import ngrams

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

def generate_ngrams(text, n=1, stopwords=set()):
    """Genera n-gramas a partir de un texto y cuenta su frecuencia."""
    # Limpiar y tokenizar el texto
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filtrar stopwords
    filtered_words = [word for word in words if word not in stopwords and not word.isdigit()]
    
    if n == 1:
        # Para unigramas, el conteo es directo
        return Counter(filtered_words)
    else:
        # Para n-gramas > 1
        n_grams = ngrams(filtered_words, n)
        # Unir las tuplas de n-gramas en cadenas
        gram_strings = [' '.join(grams) for grams in n_grams]
        return Counter(gram_strings)

def show_word_map(df_reviews, selected_sentiment, ngram_n):
    """
    Genera y muestra el WordCloud para el sentimiento y n-grama seleccionados.
    """
    if df_reviews.empty:
        st.warning("No se puede generar el mapa de palabras: el DataFrame de reseñas está vacío.")
        return

    # 1. Filtrar reseñas por el sentimiento seleccionado
    if selected_sentiment == "Todas":
        df_filtered = df_reviews
        title_suffix = "Todas las Reseñas"
    else:
        df_filtered = df_reviews[df_reviews['sentiment'] == selected_sentiment]
        title_suffix = f"Emoción: {selected_sentiment}"

    st.subheader(f"📈 Tendencias de Frases Clave ({title_suffix})")

    if df_filtered.empty:
        st.info(f"No hay reseñas con sentimiento '{selected_sentiment}' para generar el mapa de palabras.")
        return

    # 2. Concatenar todo el texto
    text_combined = " ".join(review for review in df_filtered['text'])

    if not text_combined.strip():
        st.info("El texto filtrado está vacío o solo contiene caracteres de espacio.")
        return

    # 3. Generar n-gramas y sus frecuencias
    ngram_freqs = generate_ngrams(text_combined, n=ngram_n, stopwords=ENGLISH_STOPWORDS)

    if not ngram_freqs:
        st.info(f"No se encontraron {ngram_n}-gramas para mostrar con los filtros aplicados.")
        return
        
    # 4. Crear el objeto WordCloud a partir de las frecuencias
    wordcloud = WordCloud(
        background_color="white",
        width=800,
        height=400,
        colormap='viridis',
        max_words=100
    ).generate_from_frequencies(ngram_freqs)

    # 5. Mostrar la imagen en Streamlit
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)


def word_map_dashboard(df_reviews):
    """
    Componente del dashboard que permite al usuario seleccionar sentimiento y n-grama
    y llama a la función de generación del WordCloud.
    """
    st.markdown("---") 
    st.header("🔍 Análisis de Tendencias por Emoción (Word Map)")
    st.markdown("""
    Selecciona una categoría de emoción y el tamaño del n-grama para visualizar las frases más frecuentes.
    - **1-grama (unigrama):** Palabras individuales.
    - **2-gramas (bigrama):** Pares de palabras.
    - **3-gramas (trigrama):** Tríos de palabras.
    """)
    
    # Dividir en columnas para los selectores
    col1, col2 = st.columns(2)

    with col1:
        # Opciones del selector de sentimiento
        sentiment_options = ["Todas", "Positivo", "Negativo", "Neutral"]
        selected_sentiment = st.selectbox(
            "Filtrar por tipo de Emoción:",
            options=sentiment_options,
            index=0,
            key="wordmap_sentiment_selector"
        )
    
    with col2:
        # Selector de n-grama
        ngram_n = st.slider(
            "Seleccionar tamaño de n-grama:",
            min_value=1,
            max_value=3,
            value=1,
            key="ngram_selector",
            help="1=palabras individuales, 2=pares de palabras, 3=tríos de palabras."
        )

    # Generar y mostrar el WordCloud
    show_word_map(df_reviews, selected_sentiment, ngram_n)
