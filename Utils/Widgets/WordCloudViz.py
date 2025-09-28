import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

# Importamos las dependencias de NLP para stopwords
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# Diccionario de stopwords comunes en español
SPANISH_STOP_WORDS = [
    'a', 'al', 'algo', 'algunas', 'algunos', 'ante', 'antes', 'como', 'con', 
    'contra', 'cual', 'cuando', 'de', 'del', 'desde', 'donde', 'durante', 
    'e', 'el', 'ella', 'ellas', 'ellos', 'en', 'entre', 'es', 'esa', 'esas', 
    'ese', 'eso', 'esos', 'esta', 'estas', 'este', 'esto', 'estos', 'ha', 
    'hace', 'hacer', 'haces', 'hacemos', 'hacen', 'hacia', 'hasta', 'hay', 
    'la', 'las', 'le', 'les', 'lo', 'los', 'más', 'me', 'mi', 'mis', 'muy', 
    'ni', 'no', 'nos', 'o', 'para', 'pero', 'por', 'porque', 'que', 'se', 
    'si', 'sin', 'sino', 'sobre', 'su', 'sus', 'te', 'tenemos', 'tienes', 
    'todo', 'todos', 'un', 'una', 'unas', 'uno', 'unos', 'y', 'yo', 
    'mi car', 'my car', 'car wash', 'auto detailing', 'auto detail', 
    'auto', 'coche', 'carro', 'camioneta', 'they', 'i'
]

ALL_STOP_WORDS = list(ENGLISH_STOP_WORDS) + SPANISH_STOP_WORDS

@st.cache_data
def generate_word_cloud(text_data, sentiment_color):
    """Genera una Nube de Palabras a partir del texto y devuelve la imagen en bytes."""
    
    # Definir el color de fondo y el color de las palabras basado en el sentimiento
    if sentiment_color == 'Negativo':
        colormap = 'Reds'
        background_color = 'black'
    elif sentiment_color == 'Positivo':
        colormap = 'Greens'
        background_color = 'white'
    else:
        colormap = 'viridis'
        background_color = 'white'
        
    # Crear el objeto WordCloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color=background_color, 
        colormap=colormap, 
        max_words=100,
        stopwords=set(ALL_STOP_WORDS), 
        contour_width=3, 
        contour_color='steelblue'
    )
    
    # Generar la nube de palabras
    wordcloud.generate(text_data)
    
    # Convertir a imagen PNG en memoria
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    return buf

def show_word_cloud_dashboard(df_reviews):
    """
    Muestra el dashboard de la Nube de Palabras con filtros de Emoción.
    """
    st.subheader("☁️ Nube de Palabras por Emoción y Frecuencia")
    st.markdown("Identifica las **palabras clave** más utilizadas en las reseñas filtradas para entender el *porqué* de la emoción.")

    # 1. Widget de Filtro por Emoción
    sentiment_choice = st.selectbox(
        "Seleccionar Sentimiento para el Análisis:",
        ['Negativo', 'Positivo', 'Neutral'],
        index=0,
        help="Filtra las reseñas para ver las palabras clave asociadas a una emoción específica."
    )

    # 2. Filtrar los datos
    df_filtered = df_reviews[df_reviews['sentiment'] == sentiment_choice]

    if df_filtered.empty:
        st.warning(f"No hay reseñas con sentimiento **{sentiment_choice}** con los filtros de negocio aplicados.")
        return

    # 3. Concatenar el texto y generar la nube de palabras
    text_data = " ".join(review for review in df_filtered['text'])
    
    # Si hay texto suficiente, generar la visualización
    if len(text_data) > 100:
        try:
            image_buffer = generate_word_cloud(text_data, sentiment_choice)
            st.image(image_buffer, caption=f'Palabras clave de reseñas {sentiment_choice.lower()}', use_column_width=True)
            
            st.caption(f"Mostrando un total de {len(df_filtered)} reseñas.")
        except Exception as e:
            st.error(f"Error al generar la Nube de Palabras: {e}")
    else:
         st.info("El texto de las reseñas filtradas es demasiado corto para generar una nube de palabras significativa.")
