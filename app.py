from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'llavesitasecreta:3'

API_KEY = "0zYsgNsAc070fgtRWyul1pOkENLlfu32g3alFq3a"
API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def buscar_alimento():
    alimentos = request.form.get('alimentos', '').strip()
    if not alimentos:
        flash('Por favor ingresa uno o varios alimentos.', 'error')
        return redirect(url_for('index'))

    lista_alimentos = [a.strip() for a in alimentos.split(',') if a.strip()]
    if len(lista_alimentos) > 5:
        flash('Solo puedes buscar hasta 5 alimentos.', 'error')
        return redirect(url_for('index'))

    resultados = []

    for alimento in lista_alimentos:
        try:
            params = {"query": alimento, "pageSize": 1, "api_key": API_KEY}
            resp = requests.get(API_URL, params=params)

            if resp.status_code == 200:
                data = resp.json()
                if "foods" in data and len(data["foods"]) > 0:
                    food = data["foods"][0]
                    nutrients = {n["nutrientName"]: n["value"] for n in food["foodNutrients"] if "value" in n}

                    resultados.append({
                        "nombre": food["description"].title(),
                        "calorias": nutrients.get("Energy", "No disponible"),
                        "proteinas": nutrients.get("Protein", "No disponible"),
                        "grasas": nutrients.get("Total lipid (fat)", "No disponible"),
                        "carbohidratos": nutrients.get("Carbohydrate, by difference", "No disponible")
                    })
                else:
                    resultados.append({"nombre": alimento.title(), "error": "No encontrado"})
            else:
                resultados.append({"nombre": alimento.title(), "error": "Error en la búsqueda"})
        except requests.exceptions.RequestException:
            resultados.append({"nombre": alimento.title(), "error": "Error de conexión"})

    return render_template('food.html', resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True)