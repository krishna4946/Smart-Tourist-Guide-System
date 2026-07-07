import os
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Ye tera existing DB data hai - isko waise hi rehne de
places_db = [
    {"name": "Lingaraj Temple", "image": "https://example.com/lingaraj.jpg", "desc": "Ancient temple"},
    {"name": "Udayagiri Caves", "image": "", "desc": "Historic caves"},
    #... tera baaki data
]

def get_unsplash_image(place_name):
    access_key = os.environ.get('UNSPLASH_KEY')
    if not access_key:
        return None
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": f"{place_name} Bhubaneswar Odisha",
            "client_id": access_key,
            "per_page": 1,
            "orientation": "landscape"
        }
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data['results']:
                return data['results'][0]['urls']['regular']
    except Exception as e:
        print(f"Unsplash error: {e}")
    return None

@app.route('/', methods=['GET', 'POST'])
def home():
    image = None
    place_data = None
    
    if request.method == 'POST':
        search_name = request.form.get('place_name')
      
        for place in places_db:
            if search_name.lower() in place['name'].lower():
                place_data = place
                break
        
        if place_data:
            image = place_data.get('image')
            # Agar DB me image nahi hai to Unsplash se laao
            if not image:
                image = get_unsplash_image(place_data['name'])
    
    return render_template('index.html', image=image, place=place_data)

if __name__ == '__main__':
    app.run(debug=True)