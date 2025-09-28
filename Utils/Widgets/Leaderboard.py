import streamlit as st
import pandas as pd

def calculate_ranking_score(df, sentiment_weight=0.5):
    """
    Calcula un score de ranking combinando el rating de estrellas y el sentimiento.
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
    df['combined_score'] = (
        (df['rating_norm'] * (1 - sentiment_weight)) + 
        (df['sentiment_score'] * sentiment_weight)
    )
    
    # Formatear el score a porcentaje para mejor visualización
    df['ranking_score'] = (df['combined_score'] * 100).round(1)
    
    return df

def show_leaderboard(df_data):
    """Muestra el leaderboard de las mejores compañías de detailing con formato de podio."""

    # 1. Calcular el score y ordenar
    df_ranked = calculate_ranking_score(df_data.copy(), sentiment_weight=0.5) 
    df_ranked = df_ranked.sort_values(by='ranking_score', ascending=False).reset_index(drop=True)
    df_ranked['Rank'] = df_ranked.index + 1
    
    st.subheader("🏆 Leaderboard de Desempeño Combinado")
    st.markdown("Este ranking combina el **Rating de Estrellas** (desempeño histórico) y el **Score de Emoción** (desempeño reciente), ponderados al 50/50, para dar una visión holística de la calidad del servicio.")
    
    # 2. Separar Top 3 y el resto
    df_top3 = df_ranked.head(3)
    df_rest = df_ranked.iloc[3:]

    # 3. Mostrar el Podio (Top 3)
    if not df_top3.empty:
        
        # Usar 3 columnas: 2do lugar | 1er lugar | 3er lugar
        col2, col1, col3 = st.columns([1, 1.2, 1])

        # Función auxiliar para renderizar cada posición
        def render_podium_item(col, rank, df_podium, title, color_hex, emoji, height):
            if rank <= len(df_podium):
                item = df_podium.iloc[rank - 1]
                name = item['name']
                score = item['ranking_score']
                rating = item['rating']
                sentiment = item['sentiment']
                
                # Diseño de la tarjeta con HTML/CSS para el podio
                col.markdown(f"""
                <div style="
                    background-color: {color_hex}; 
                    border-radius: 10px; 
                    padding: 15px; 
                    margin-bottom: 10px;
                    text-align: center;
                    box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
                    height: {height};
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                ">
                    <h2 style="color: white; margin-bottom: 0px;">{emoji} {title}</h2>
                    <h3 style="color: white; margin-top: 5px; font-size: 1.3rem;">{name}</h3>
                    <p style="color: white; font-size: 1.2rem; font-weight: bold;">Score: {score}%</p>
                    <p style="color: white; margin: 0;">Rating: {rating} ⭐ | {sentiment}</p>
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
            color_hex="#A9A9A9", # Gris oscuro/Plata
            emoji="🥈", 
            height="200px"
        )
        
        # Renderizar 1er lugar (col1 - más alto y central)
        render_podium_item(
            col=col1, 
            rank=1, 
            df_podium=df_top3, 
            title="1º ORO", 
            color_hex="#FFD700", # Dorado
            emoji="🥇", 
            height="250px"
        )

        # Renderizar 3er lugar (col3)
        render_podium_item(
            col=col3, 
            rank=3, 
            df_podium=df_top3, 
            title="3º BRONCE", 
            color_hex="#CD7F32", # Bronce/Marrón
            emoji="🥉", 
            height="150px"
        )
    else:
        st.warning("No hay datos disponibles para mostrar el Leaderboard con los filtros aplicados.")


    st.markdown("---")
    
    # 4. Mostrar el resto del ranking (del 4º lugar en adelante)
    if not df_rest.empty:
        st.subheader("Ranking Completo (Top 4 en adelante)")
        
        df_display_rest = df_rest[['Rank', 'name', 'rating', 'sentiment', 'review_count', 'ranking_score']]
        df_display_rest.columns = ['Rank', 'Compañía', 'Rating (Estrellas)', 'Emoción Reciente', 'Total Reseñas', 'Score Combinado (%)']
        
        st.dataframe(
            df_display_rest,
            height=300,
            use_container_width=True,
            hide_index=True,
        )