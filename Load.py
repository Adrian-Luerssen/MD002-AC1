import http.server
import socketserver
import os

import matplotlib.pyplot as plt
import sqlite3
import numpy as np
from Transformations import Database

PORT = 8080
ASSETS_DIR = "assets"

class ImageRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override to suppress logging
        return
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            files = os.listdir(ASSETS_DIR)
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

            html = "<html><head><title>Image Gallery</title></head><body>"
            html += "<h1 style='text-align: center;'>Select an Image to View</h1>"
            
            html += """
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f5;
                    margin: 0;
                    padding: 20px;
                }
                .grid-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                    gap: 20px;
                    max-width: 1000px;
                    margin: 0 auto;
                }
                .grid-item {
                    text-align: center;
                }
                .grid-item img {
                    width: 100%;
                    height: 150px;
                    object-fit: cover;
                    border-radius: 8px;
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
                }
                .grid-item h3 {
                    margin-top: 10px;
                    font-size: 16px;
                    color: #333;
                    word-wrap: break-word;
                }
                a {
                    text-decoration: none;
                    color: inherit;
                }
            </style>
            """
            
            html += "<div class='grid-container'>"

            for image in image_files:
                image_path = f"/{ASSETS_DIR}/{image}"
                image_name = os.path.splitext(image)[0]  # Get the filename without extension
                html += f"""
                <div class='grid-item'>
                    <a href='{image_path}'><img src='{image_path}' alt='{image_name}'></a>
                    <h3>{image_name}</h3>
                </div>
                """

            html += "</div></body></html>"

            self.wfile.write(html.encode("utf-8"))
        else:
            super().do_GET()


            
    
    
class WebServer:
    def __init__(self):
        self.database = Database()
        self.httpd = socketserver.TCPServer(("", PORT), ImageRequestHandler)
    def save_chart(self, chart_name:str):
        plt.savefig(f"{ASSETS_DIR}/{chart_name}.png")
        
    def generate_charts(self):
        self.generate_average_age_graph()
        plt.close()
        self.generate_common_city_user_count_graph()
        plt.close()
        self.generate_gender_distribution_graph()
        plt.close()
        self.generate_stacked_generation_distribution_graph()
        plt.close()
        self.generate_timezone_user_count_graph()
        plt.close()
        self.generate_continent_user_count_graph()
        plt.close()
        self.generate_average_age_by_country_graph()
        plt.close()
        self.generate_time_registered_distribution_graph()
        plt.close()
        self.generate_age_at_registration_bar_graph()
        plt.close()
        self.generate_age_at_registration_by_generation_graph()
        plt.close()
        
    

    def generate_average_age_graph(self): 
        results = self.database.load_stat("Average age")
        #print(results)
        
        user_counts = [item[0] for item in results]
        average_ages = [item[1] for item in results]

        plt.figure(figsize=(10, 6))
        plt.plot(user_counts, average_ages, color='blue', marker='o', linestyle='-', label="Average Age Distribution")
        plt.ylim(0, 100)
        
        plt.xlabel("User Count")
        plt.ylabel("Average Age")
        plt.title("Average Age Distribution over User Count")
        plt.legend()
        for i, age in enumerate(average_ages):
            plt.text(user_counts[i], age, f"{age:.2f}", ha='right', va='bottom', fontsize=8, color='black')
            
        self.save_chart("average_age")
        plt.close()

#nuevo grafico a partir de get_common_city

    def generate_common_city_user_count_graph(self):
        # Obtener la ciudad con la mayor cantidad de usuarios
        result = self.database.get_common_city()
        
        # Procesar los datos para el gráfico de barras (solo una ciudad)
        if result:
            city, user_count = result
            cities = [city]
            user_counts = [user_count]
            
            # Crear gráfico de barras
            plt.figure(figsize=(6, 6))  # Ajusta el tamaño del gráfico ya que es solo una barra
            plt.bar(cities, user_counts, color='skyblue')

            plt.xlabel("Ciudad")
            plt.ylabel("Cantidad de Usuarios")
            plt.title("Ciudad con Mayor Cantidad de Usuarios")  # Título en español

            # Guardar el gráfico
            self.save_chart("common_city_user_count")
        else:
            print("No se encontraron datos para generar el gráfico.")       

#nuevo grafico a partir de get_top_gender_distribution_country

    def generate_gender_distribution_graph(self):
        # Obtener datos de distribución de género por país
        results = self.database.get_top_gender_distribution_country()

        # Procesar datos para el gráfico de barras
        from collections import defaultdict
        data_by_country = defaultdict(lambda: {"Male": 0, "Female": 0})

        for country, gender, count in results:
            if gender.title() in [gen.title() for gen in data_by_country[country].keys()]:
                data_by_country[country][gender.title()] = count
        #print(data_by_country)
        countries = list(data_by_country.keys())
        male_counts = [data_by_country[country]["Male"] for country in countries]
        female_counts = [data_by_country[country]["Female"] for country in countries]

        # Crear gráfico de barras agrupado
        plt.figure(figsize=(12, 8))
        bar_width = 0.35
        index = range(len(countries))

        plt.bar(index, male_counts, bar_width, label="Male")
        plt.bar([i + bar_width for i in index], female_counts, bar_width, label="Female")

        plt.xlabel("Country")
        plt.ylabel("User Count")
        plt.title("Gender Distribution by Country")
        plt.xticks([i + bar_width / 2 for i in index], countries, rotation=45)
        plt.legend()

        # Guardar el gráfico
        self.save_chart("gender_distribution")

#nuevo grafico barra aplidad a partir de get_top_generation_distribution_country

    def generate_stacked_generation_distribution_graph(self):
        # Obtener datos de distribución por generación y país
        results = self.database.get_top_generation_distribution_country()

        # Procesar datos para el gráfico de barras apiladas
        from collections import defaultdict
        data_by_country = defaultdict(lambda: {
            "Silent Generation": 0,
            "Baby Boomer": 0,
            "Generation X": 0,
            "Millennials": 0,
            "Generation Z": 0,
            "Generation Alpha": 0
        })

        for country, generation, count in results:
            if generation in data_by_country[country]:
                data_by_country[country][generation] = count

        countries = list(data_by_country.keys())
        silent_counts = [data_by_country[country]["Silent Generation"] for country in countries]
        boomer_counts = [data_by_country[country]["Baby Boomer"] for country in countries]
        gen_x_counts = [data_by_country[country]["Generation X"] for country in countries]
        millennial_counts = [data_by_country[country]["Millennials"] for country in countries]
        gen_z_counts = [data_by_country[country]["Generation Z"] for country in countries]
        alpha_counts = [data_by_country[country]["Generation Alpha"] for country in countries]

        # Crear gráfico de barras apiladas
        plt.figure(figsize=(14, 8))
        plt.bar(countries, silent_counts, label="Silent Generation")
        plt.bar(countries, boomer_counts, bottom=silent_counts, label="Baby Boomer")
        plt.bar(countries, gen_x_counts, bottom=np.array(silent_counts) + np.array(boomer_counts), label="Generation X")
        plt.bar(countries, millennial_counts, bottom=np.array(silent_counts) + np.array(boomer_counts) + np.array(gen_x_counts), label="Millennials")
        plt.bar(countries, gen_z_counts, bottom=np.array(silent_counts) + np.array(boomer_counts) + np.array(gen_x_counts) + np.array(millennial_counts), label="Generation Z")
        plt.bar(countries, alpha_counts, bottom=np.array(silent_counts) + np.array(boomer_counts) + np.array(gen_x_counts) + np.array(millennial_counts) + np.array(gen_z_counts), label="Generation Alpha")

        plt.xlabel("Country")
        plt.ylabel("User Count")
        plt.title("Generation Distribution by Country (Top 10 Countries)")
        plt.xticks(rotation=45)
        plt.legend()

        # Guardar el gráfico
        self.save_chart("stacked_generation_distribution")

#nuevo grafico barra aplidad a partir de get_user_count_by_timezone

    def generate_timezone_user_count_graph(self):
        # Obtener datos de cantidad de usuarios por zona horaria
        results = self.database.get_user_count_by_timezone()

        # Procesar los datos para el gráfico de barras
        timezones = [row[0] for row in results]
        user_counts = [row[1] for row in results]

        # Crear gráfico de barras
        plt.figure(figsize=(12, 8))
        plt.bar(timezones, user_counts, color='skyblue')

        plt.xlabel("Timezone")
        plt.ylabel("User Count")
        plt.title("User Count by Timezone")
        plt.xticks(rotation=45, ha='right')

        # Guardar el gráfico
        self.save_chart("timezone_user_count")

#nuevo grafico barra aplidad a partir de get_top_user_count_by_continent

    def generate_continent_user_count_graph(self):
        # Obtener datos de cantidad de usuarios por continente
        results = self.database.get_top_user_count_by_continent()

        # Procesar los datos para el gráfico de barras
        continents = [row[0] for row in results]
        user_counts = [row[1] for row in results]

        # Crear gráfico de barras
        plt.figure(figsize=(12, 8))
        plt.bar(continents, user_counts, color='skyblue')

        plt.xlabel("Continent")
        plt.ylabel("User Count")
        plt.title("Distribución de Usuarios por Continente")
        plt.xticks(rotation=45, ha='right')

        # Guardar el gráfico
        self.save_chart("continent_user_count")

#nuevo grafico barra aplidad a partir de get_top_average_age_by_country

    def generate_average_age_by_country_graph(self):
        # Obtener datos de edad promedio por país
        results = self.database.get_top_average_age_by_country()

        # Procesar los datos para el gráfico de barras
        countries = [row[0] for row in results]
        average_ages = [row[1] for row in results]

        # Crear gráfico de barras
        plt.figure(figsize=(12, 8))
        plt.bar(countries, average_ages, color='skyblue')

        plt.xlabel("País")
        plt.ylabel("Edad Promedio")
        plt.title("Edad Promedio por País")  # Título en español
        plt.xticks(rotation=45, ha='right')

        # Guardar el gráfico
        self.save_chart("average_age_by_country")
       
#nuevo grafico barra aplidad a partir de get_time_registered_distribution

    def generate_time_registered_distribution_graph(self):
        # Obtener datos de distribución de tiempo desde el registro
        results = self.database.get_time_registered_distribution()

        # Procesar los datos para el gráfico de barras
        years_since_registration = [row[0] for row in results]
        user_counts = [row[1] for row in results]

        # Crear gráfico de barras
        plt.figure(figsize=(12, 8))
        plt.bar(years_since_registration, user_counts, color='skyblue')

        plt.xlabel("Años de Registro")
        plt.ylabel("Cantidad de Usuarios")
        plt.title("Tiempo Total Registrado")  # Título en español
        plt.xticks(rotation=45, ha='right')

        # Guardar el gráfico
        self.save_chart("time_registered_distribution")

#nuevo grafico barra aplidad a partir de get_age_at_registration_distribution

    def generate_age_at_registration_bar_graph(self):
        # Obtener datos de edad al momento del registro
        results = self.database.get_age_at_registration_distribution()

        # Procesar los datos para el gráfico de barras
        ages_at_registration = [row[0] for row in results]
        user_counts = [row[1] for row in results]

        # Crear gráfico de barras
        plt.figure(figsize=(12, 8))
        plt.bar(ages_at_registration, user_counts, color='skyblue')

        plt.xlabel("Edad al Momento del Registro")
        plt.ylabel("Cantidad de Usuarios")
        plt.title("Distribución de Usuarios según Edad al Momento del Registro")  # Título en español
        plt.xticks(rotation=45, ha='right')

        # Guardar el gráfico
        self.save_chart("age_at_registration_bar")

#nuevo grafico barra aplidad a partir de get_age_at_registration_by_generation

    def generate_age_at_registration_by_generation_graph(self):
        # Obtener datos de edad al momento del registro por generación
        results = self.database.get_age_at_registration_by_generation()

        # Procesar los datos para el gráfico de barras agrupado
        generations = [row[0] for row in results]
        min_ages = [row[1] for row in results]
        max_ages = [row[2] for row in results]
        avg_ages = [row[3] for row in results]
        median_ages = [row[4] for row in results]

        # Configurar el gráfico de barras agrupado
        plt.figure(figsize=(14, 8))
        bar_width = 0.2
        index = range(len(generations))

        plt.bar(index, min_ages, bar_width, label="Edad Mínima")
        plt.bar([i + bar_width for i in index], max_ages, bar_width, label="Edad Máxima")
        plt.bar([i + 2 * bar_width for i in index], avg_ages, bar_width, label="Edad Promedio")
        plt.bar([i + 3 * bar_width for i in index], median_ages, bar_width, label="Edad Mediana")

        plt.xlabel("Generación")
        plt.ylabel("Edad")
        plt.title("Edad al Momento del Registro por Generación")
        plt.xticks([i + 1.5 * bar_width for i in index], generations, rotation=45)
        plt.legend()

        # Guardar el gráfico
        self.save_chart("age_at_registration_by_generation")

    def empty_assets_dir(self):
        for file in os.listdir(ASSETS_DIR):
            os.remove(os.path.join(ASSETS_DIR, file))
            
    
    def run_webserver(self):
        #print("serving at port", PORT)
        self.httpd.serve_forever()
        
    def stop_webserver(self):
        self.httpd.shutdown()

def Load():
    webserver = WebServer()
    webserver.empty_assets_dir()
    webserver.generate_charts()
    webserver.run_webserver()

if __name__ == "__main__":
    Load()