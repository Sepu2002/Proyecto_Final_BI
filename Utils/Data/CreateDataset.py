import requests
import pandas as pd
import time

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
API_KEY = "API"  # Reemplaza con tu API Key de Yelp
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
REVIEWS_URL = "https://api.yelp.com/v3/businesses/{id}/reviews"

# Parámetros de búsqueda
TERM = "car detailing"
LOCATION = "Florida"
LIMIT = 50   # NO MODIFICAR
MAX_BUSINESSES = 500  # Ajustar cantidad según consulta

def get_businesses(term, location, limit, max_results):
    """Obtiene negocios de Yelp en páginas de 50 hasta alcanzar max_results"""
    businesses = []
    for offset in range(0, max_results, limit):
        params = {"term": term, "location": location, "limit": limit, "offset": offset}
        response = requests.get(SEARCH_URL, headers=HEADERS, params=params)
        if response.status_code != 200:
            print("Error:", response.json())
            break
        data = response.json().get("businesses", [])
        if not data:
            break
        businesses.extend(data)
        time.sleep(0.5)  # para no sobrecargar la API
    return businesses

def get_reviews(business_id):
    """Obtiene hasta 3 reseñas para un negocio"""
    url = REVIEWS_URL.format(id=business_id)
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return []
    return response.json().get("reviews", [])

businesses_data = get_businesses(TERM, LOCATION, LIMIT, MAX_BUSINESSES)

businesses_list = []
reviews_list = []

for b in businesses_data:
    # Guardar info del negocio
    businesses_list.append({
        "business_id": b["id"],
        "name": b.get("name"),
        "address": " ".join(b["location"].get("display_address", [])),
        "city": b["location"].get("city"),
        "state": b["location"].get("state"),
        "zip_code": b["location"].get("zip_code"),
        "phone": b.get("display_phone"),
        "categories": ", ".join([c["title"] for c in b.get("categories", [])]),
        "rating": b.get("rating"),
        "review_count": b.get("review_count"),
        "price": b.get("price", None),
        "latitude": b["coordinates"].get("latitude"),
        "longitude": b["coordinates"].get("longitude"),
        "url": b.get("url")
    })

    # Guardar reseñas (máx 7, límite de Yelp con versión premium de API)
    reviews = get_reviews(b["id"])
    for r in reviews:
        reviews_list.append({
            "review_id": r["id"],
            "business_id": b["id"],
            "user_id": r["user"]["id"],
            "user_name": r["user"]["name"],
            "rating": r["rating"],
            "text": r["text"],
            "time_created": r["time_created"],
            "url": r["url"]
        })
    time.sleep(0.5)

df_businesses = pd.DataFrame(businesses_list)
df_reviews = pd.DataFrame(reviews_list)    