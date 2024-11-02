import http.server
import socketserver
import os

PORT = 8080
ASSETS_DIR = "assets"

class ImageRequestHandler(http.server.SimpleHTTPRequestHandler):
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


def run_webserver():
    with socketserver.TCPServer(("", PORT), ImageRequestHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
        
if __name__ == "__main__":
    run_webserver()