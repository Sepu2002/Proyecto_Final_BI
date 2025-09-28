import streamlit as st
import pandas as pd

def calculate_ranking_score(df, sentiment_weight=0.5):
    """
    Calcula un score de ranking combinando el rating de estrellas y el sentimiento.

    La fórmula usa un promedio ponderado donde el rating de estrellas (desempeño histórico) 
    y el score de sentimiento (desempeño reciente) están normalizados a una escala de 0 a 1.
    """
    
    # 1. Mapeo de Sentimiento a Score Numérico (0 a 1)
    sentiment_to_score = {
        'Positivo': 1.0,
        'Neutral': 0.5,
        'Negativo': 0.0,
    }
    df['sentiment_score'] = df['sentiment'].map(sentiment_to_score)
    
    # 2. Normalización del Rating (de 1.0-5.0 a 0-1)
    MIN_RATING = 1.0
    MAX_RATING = 5.0
    df['rating_norm'] = (df['rating'] - MIN_RATING) / (MAX_RATING - MIN_RATING)
    
    # 3. Cálculo del Score Combinado (Promedio Ponderado 50/50)
    # W_rating = 1 - sentiment_weight (0.5), W_sentiment = sentiment_weight (0.5)
    df['combined_score'] = (
        (df['rating_norm'] * (1 - sentiment_weight)) + 
        (df['sentiment_score'] * sentiment_weight)
    )
    
    # Formatear el score a porcentaje para mejor visualización
    df['ranking_score'] = (df['combined_score'] * 100).round(1)
    
    return df

def show_leaderboard(df_data):
    """Muestra el leaderboard de las mejores compañías de detailing."""

    # 1. Calcular el score y ordenar
    # Se usa una copia de los datos filtrados para evitar SettingWithCopyWarning
    df_ranked = calculate_ranking_score(df_data.copy(), sentiment_weight=0.5) 
    df_ranked = df_ranked.sort_values(by='ranking_score', ascending=False).reset_index(drop=True)
    df_ranked['Rank'] = df_ranked.index + 1
    
    # 2. Seleccionar columnas a mostrar
    df_display = df_ranked[['Rank', 'name', 'rating', 'sentiment', 'review_count', 'ranking_score']]
    df_display.columns = ['Rank', 'Compañía', 'Rating (Estrellas)', 'Emoción Reciente', 'Total Reseñas', 'Score Combinado (%)']
    
    # 3. Mostrar el leaderboard en Streamlit
    st.subheader("🏆 Leaderboard de Desempeño Combinado")
    st.markdown("Este ranking combina el **Rating de Estrellas** (desempeño histórico) y el **Score de Emoción** (desempeño reciente), ponderados al 50/50, para dar una visión holística de la calidad del servicio.")
    
    # Usar st.dataframe para un look más limpio y completo
    st.dataframe(
        df_display,
        height=400,
        use_container_width=True,
        hide_index=True,
    )