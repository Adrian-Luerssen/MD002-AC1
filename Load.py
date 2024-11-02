import http.server
import socketserver
import os
import matplotlib.pyplot as plt
import sqlite3

PORT = 8080
ASSETS_DIR = "assets"

class ImageRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override to suppress logging
        return
    
    def do_GET(self):
        if self.path == '/':
            # Serve the main page that lists images in the assets directory
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # List all files in the assets directory
            files = os.listdir(ASSETS_DIR)
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

            # Generate HTML content
            html = "<html><head><title>Image Gallery</title></head><body>"
            html += "<h1>Select an image to view</h1>"
            
            # Style for grid layout
            html += """
            <style>
                .grid-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                    gap: 20px;
                    max-width: 1000px;
                    margin: auto;
                }
                .grid-item {
                    text-align: center;
                    font-family: Arial, sans-serif;
                }
                .grid-item img {
                    width: 150px;
                    height: auto;
                    border-radius: 8px;
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
                }
            </style>
            """
            
            html += "<div class='grid-container'>"

            # Add each image as a grid item with title
            for image in image_files:
                image_path = f"/{ASSETS_DIR}/{image}"
                image_name = os.path.splitext(image)[0]  # Get the filename without extension
                html += f"""
                <div class='grid-item'>
                    <a href='{image_path}'><img src='{image_path}'></a>
                    <h3>{image_name}</h3>
                </div>
                """

            html += "</div></body></html>"

            self.wfile.write(html.encode("utf-8"))
        else:
            # Serve image files directly
            super().do_GET()

class Database:
    def __init__(self):
        try:
            self.conn = sqlite3.connect("user_data.db")
            self.cursor = self.conn.cursor()
        except Exception as e:
            print("Error connecting to the database:", e)
            exit(1)
            
    def load_stat(self, stat_name:str):
        self.cursor.execute("SELECT user_count,stat_value FROM stats WHERE stat_name = ?", (stat_name,))
        result = self.cursor.fetchall()
        return [[age[0],float(age[1])] for age in result] if result is not None else None
    
class WebServer:
    def __init__(self):
        self.database = Database()
        self.httpd = socketserver.TCPServer(("", PORT), ImageRequestHandler)
    def save_chart(self, chart_name:str):
        plt.savefig(f"{ASSETS_DIR}/{chart_name}.png")
        
    def generate_charts(self):
        self.generate_average_age_graph()
        
    
    def generate_average_age_graph(self): 
        results = self.database.load_stat("Average age")
        print(results)
        
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