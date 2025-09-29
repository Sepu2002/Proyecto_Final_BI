# **Shiny Stats: Business Intelligence para el Detailing Automotriz en Florida**

**Shiny Stats** es un proyecto de inteligencia de negocios que analiza el mercado de *detailing* automotriz en Florida. A través de un dashboard interactivo desarrollado en Streamlit, la herramienta permite visualizar y analizar datos extraídos de reseñas de Yelp para obtener una ventaja competitiva, identificar oportunidades de mercado y mejorar la toma de decisiones.

**Dashboard Interactivo:** [Florida Auto Detailing Dashboard](https://florida-auto-detailing.streamlit.app)

## **El Problema y la Oportunidad**

El sector del *detailing* automotriz en Florida es altamente competitivo y la calidad del servicio puede ser inconsistente. Los clientes basan sus decisiones en la reputación, el precio y las reseñas en línea. La principal oportunidad radica en la falta de un servicio personalizado que analice a fondo los comentarios de los clientes para identificar patrones de quejas y áreas de mejora.

## **Nuestra Solución: "Shiny Stats"**

**Shiny Stats** es una propuesta de negocio que utiliza un enfoque basado en datos (Business Intelligence) para optimizar cada aspecto de la operación. La clave es el uso de **análisis de sentimientos y minería de texto** en las reseñas de los clientes para convertir las quejas de la competencia en oportunidades de crecimiento.

## **📊 Características del Dashboard**

El dashboard es la herramienta central para la toma de decisiones y contiene los siguientes módulos:

* **Análisis de Sentimiento:** Un gráfico de barras que muestra el porcentaje de reseñas **positivas, negativas y neutrales** por región o competidor. Permite identificar qué negocios generan las mejores y peores experiencias.  
* **Palabras Clave:** Una nube de palabras (*word cloud*) que resalta los términos más frecuentes en las reseñas negativas, revelando las quejas más comunes como "tiempo de espera", "manchas", "rayones" o "precio".  
* **Mapa de Calor:** Un mapa interactivo de Florida que muestra la densidad de reseñas negativas por área, ayudando a identificar zonas con alta insatisfacción y potencial de mercado.  
* **Tendencias Temporales:** Un gráfico de líneas que muestra la evolución de las calificaciones a lo largo del tiempo, permitiendo detectar si la reputación de un competidor está mejorando o empeorando.  
* **Análisis de la Competencia:** Una tabla comparativa de competidores basada en sus calificaciones, número de reseñas y las principales quejas identificadas.

## **🛠️ Fuentes de Datos y Tecnología**

### **Fuentes de Datos**

* **Fuente Primaria:** [Yelp Fusion API](https://www.yelp.com/fusion) para extraer reseñas de negocios de *detailing* automotriz en Florida.  
* **Fuentes Secundarias:**  
  * Google Maps API  
  * Datos demográficos de la Oficina del Censo de EE. UU.  
  * Precios de mercado de sitios como Edmunds o Kelley Blue Book.

### **Stack Tecnológico**

* **Lenguaje:** Python  
* **Librerías Principales:** Streamlit, Pandas, Plotly, NLTK, WordCloud.  
* **Plataforma de Despliegue:** Streamlit Community Cloud.

## **🚀 Propuesta de Valor**

Al analizar los datos con este dashboard, se puede:

1. **Mejorar el Servicio:** Abordar directamente las quejas más comunes identificadas.  
2. **Personalizar Ofertas:** Crear paquetes de servicios dirigidos a resolver problemas específicos.  
3. **Optimizar la Estrategia de Precios:** Correlacionar la satisfacción del cliente con los precios para encontrar el punto óptimo.  
4. **Identificar Nuevos Mercados:** Usar el mapa de calor para encontrar áreas con alta demanda pero baja satisfacción.
