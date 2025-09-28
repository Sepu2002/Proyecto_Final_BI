import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def calculate_ranking_score(df_business_summary, df_detailed_reviews, sentiment_weight=0.6, recency_factor=0.4):
    """
    Calcula un Score de Ranking Combinado basado en Rating Histórico y Sentimiento Reciente Ponderado.
    
    sentiment_weight: Peso del sentimiento (0.0 a 1.0). El rating toma el peso restante.
    recency_factor: Factor para priorizar reseñas recientes (ej. reseñas del último mes valen más).
    """
    
    df = df_business_summary.copy()
    df_reviews = df_detailed_reviews.copy()

    # --- 1. CÁLCULO DEL SCORE DE SENTIMIENTO RECIENTE ---
    
    # A. Filtrar reseñas por "recencia" (último mes o último año para tener volumen)
    # Usaremos el último año para asegurar un volumen mínimo en la simulación
    one_year_ago = datetime.now() - timedelta(days=365)
    
    # Asegurar que 'time_created' sea datetime y que las reseñas tengan 'business_id' y 'sentiment'
    df_reviews['time_created'] = pd.to_datetime(df_reviews['time_created'], errors='coerce')
    df_recent_reviews = df_reviews[df_reviews['time_created'] >= one_year_ago]

    # B. Mapeo de Sentimiento a Score Numérico
    sentiment_to_score = {
        'Positivo': 1.0,
        'Neutral': 0.5,
        'Negativo': 0.0,
    }
    df_recent_reviews['score'] = df_recent_reviews['sentiment'].map(sentiment_to_score)
    
    # C. Ponderar por Recencia (Si queremos darle un extra a las reseñas de los últimos 30 días)
    one_month_ago = datetime.now() - timedelta(days=30)
    df_recent_reviews['recency_boost'] = df_recent_reviews['time_created'].apply(
        lambda x: 1.0 + recency_factor if x >= one_month_ago else 1.0
    )
    df_recent_reviews['weighted_score'] = df_recent_reviews['score'] * df_recent_reviews['recency_boost']

    # D. Agrupar por negocio para obtener el Score Promedio Reciente
    df_recent_score = df_recent_reviews.groupby('business_id').agg(
        avg_sentiment_score=('weighted_score', 'mean'),
        recent_review_count=('business_id', 'count')
    ).reset_index()

    # Fusionar con el resumen de negocios
    df = pd.merge(df, df_recent_score, on='business_id', how='left').fillna(0)
    
    # Normalizar el Score de Sentimiento Reciente (de 0 a 1, si no hay reseñas recientes se usa 0.5 como neutral)
    df['avg_sentiment_score_norm'] = df['avg_sentiment_score'].apply(
        lambda x: (x - 0.0) / (1.0 * (1 + recency_factor) - 0.0) if x > 0 else 0.5
    )
    
    # --- 2. CÁLCULO DEL SCORE DE RATING HISTÓRICO (Base del Ranking) ---
    # Normalización del Rating (de 1.0-5.0 a 0-1)
    MIN_RATING = 1.0
    MAX_RATING = 5.0
    df['rating_norm'] = (df['rating'] - MIN_RATING) / (MAX_RATING - MIN_RATING)
    
    # --- 3. CÁLCULO DEL SCORE COMBINADO (Promedio Ponderado) ---
    df['combined_score'] = (
        (df['rating_norm'] * (1 - sentiment_weight)) + 
        (df['avg_sentiment_score_norm'] * sentiment_weight)
    )
    
    # Ajuste por volumen: penalizar si el número de reseñas es muy bajo (ej. < 10)
    df['volume_penalty'] = df['review_count'].apply(lambda x: 1.0 if x >= 10 else x / 10 if x > 0 else 0.1)
    df['final_combined_score'] = df['combined_score'] * df['volume_penalty']

    # Formatear el score a porcentaje para mejor visualización
    df['ranking_score'] = (df['final_combined_score'] * 100).round(1)
    
    return df

def show_leaderboard(df_filtered_business, df_detailed_reviews):
    """Muestra el leaderboard de las mejores compañías de detailing con formato de podio."""
    
    # 1. Calcular el score y ordenar
    # Asegúrate de que solo se usan los business_id presentes en df_filtered_business para filtrar las reviews
    filtered_business_ids = df_filtered_business['business_id'].unique()
    df_reviews_for_ranking = df_detailed_reviews[df_detailed_reviews['business_id'].isin(filtered_business_ids)]
    
    df_ranked = calculate_ranking_score(df_filtered_business.copy(), df_reviews_for_ranking, sentiment_weight=0.6) 
    df_ranked = df_ranked.sort_values(by='ranking_score', ascending=False).reset_index(drop=True)
    df_ranked['Rank'] = df_ranked.index + 1
    
    st.subheader("🏆 Ranking Activo de Competidores (BI Score)")
    st.markdown("""
        Este ranking utiliza un **Score de BI Ponderado** (Sentiment Reciente 60% | Rating Histórico 40%) 
        para reflejar el pulso actual del mercado, no solo el desempeño pasado. 
        Esto te ayuda a identificar a los competidores que están fallando *ahora* (oportunidad) o triunfando *ahora* (benchmarking).
    """)
    
    if df_ranked.empty:
        st.warning("No hay datos disponibles para mostrar el Leaderboard con los filtros aplicados.")
        return

    # 2. Separar Top 3 y el resto
    df_top3 = df_ranked.head(3)
    df_rest = df_ranked.iloc[3:]

    # 3. Mostrar el Podio (Top 3)
    # Usar 3 columnas: 2do lugar | 1er lugar | 3er lugar
    col2, col1, col3 = st.columns([1, 1.2, 1])

    # Función auxiliar para renderizar cada posición
    def render_podium_item(col, rank, df_podium, title, color_hex, emoji, height):
        if rank <= len(df_podium):
            item = df_podium.iloc[rank - 1]
            name = item['name']
            score = item['ranking_score']
            rating = item['rating']
            
            # Formatear el texto de la empresa según el ranking
            if rank == 1:
                name_style = f"<h3 style='color: white; margin-top: 5px; font-size: 1.5rem;'>{name}</h3>"
            else:
                 name_style = f"<h3 style='color: white; margin-top: 5px; font-size: 1.3rem;'>{name}</h3>"
                 
            
            # Diseño de la tarjeta con HTML/CSS para el podio
            col.markdown(f"""
            <div style="
                background-color: {color_hex}; 
                border-radius: 10px; 
                padding: 15px; 
                margin-bottom: 10px;
                text-align: center;
                box-shadow: 3px 3px 15px rgba(0,0,0,0.3);
                height: {height};
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                border: 3px solid white;
            ">
                <h2 style="color: white; margin-bottom: 0px;">{emoji} {title}</h2>
                {name_style}
                <p style="color: white; font-size: 1.5rem; font-weight: bold; margin: 5px 0;">BI Score: {score}%</p>
                <p style="color: white; margin: 0;">Rating Histórico: {rating} ⭐</p>
            </div>
            """, unsafe_allow_html=True)
        else:
             # Cajón vacío para mantener la estructura si hay menos de 3 resultados
             col.markdown(f"""
            <div style="
                background-color: #f0f2f6; 
                border-radius: 10px; 
                padding: 15px; 
                margin-bottom: 10px;
                text-align: center;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                height: {height};
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <p style="color: #808080; font-weight: bold; margin: 0;">{title} Lugar Vacío</p>
            </div>
            """, unsafe_allow_html=True)


    # Renderizar 2do lugar (col2)
    render_podium_item(
        col=col2, 
        rank=2, 
        df_podium=df_top3, 
        title="2º PLATA", 
        color_hex="#A8A8A8", # Plata
        emoji="🥈", 
        height="300px"
    )
    
    # Renderizar 1er lugar (col1 - más alto y central)
    render_podium_item(
        col=col1, 
        rank=1, 
        df_podium=df_top3, 
        title="1º ORO", 
        color_hex="#FFD700", # Dorado
        emoji="🥇", 
        height="300px"
    )

    # Renderizar 3er lugar (col3)
    render_podium_item(
        col=col3, 
        rank=3, 
        df_podium=df_top3, 
        title="3º BRONCE", 
        color_hex="#CD7F32", # Bronce
        emoji="🥉", 
        height="300px"
    )

    st.markdown("---")
    
    # 4. Mostrar el resto del ranking (del 4º lugar en adelante)
    if not df_rest.empty:
        st.subheader("Ranking Completo (Top 4 en adelante)")
        
        # Filtramos la tabla para mostrar solo columnas relevantes y el score
        df_display_rest = df_rest[['Rank', 'name', 'rating', 'dominant_sentiment', 'review_count', 'ranking_score']]
        df_display_rest.columns = ['Rank', 'Compañía', 'Rating Histórico', 'Sentimiento Dominante', 'Total Reseñas', 'BI Score (%)']
        
        st.dataframe(
            df_display_rest,
            height=300,
            use_container_width=True,
            hide_index=True,
            column_config={
                "BI Score (%)": st.column_config.ProgressColumn(
                    "BI Score (%)",
                    help="Score Combinado (Sentimiento Reciente + Rating Histórico)",
                    format="%f",
                    min_value=0,
                    max_value=100,
                )
            }
        )
    else:
        if len(df_ranked) > 0:
            st.info("Solo hay 3 o menos negocios disponibles con los filtros aplicados para mostrar el ranking extendido.")
