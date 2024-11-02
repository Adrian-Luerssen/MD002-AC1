from Extraction import *
from Transformations import *
from Load import *
import threading

def main():
    webserver = WebServer()
    webserver.empty_assets_dir()
    try:
        webserver.generate_charts()
    except Exception as e:
        print("Error generating charts:", e)
        
    t1 = threading.Thread(target=webserver.run_webserver)
    t1.start()
    while(True):
        print("""---- MD002-AC1 MENU ----
                1. ETL
                2. Reset DB
                3. Exit
                """)
        option = input("Enter your option: ")
        if option == '1':
            num_users = int(input("Enter the number of users to extract: "))
            extraction(num_users)
            transformation()
            webserver.empty_assets_dir()
            webserver.generate_charts()
        elif option == '2':
            reset_db()
            webserver.empty_assets_dir()
        elif option == '3':
            webserver.stop_webserver()  # Signal the web server to stop
            break
        else:
            printf("Invalid option. Please try again.")
        pass
    # Wait for the web server thread to finish
    t1.join()
    webserver.empty_assets_dir()
    print("Web server stopped. Exiting program.")
    
if __name__ == "__main__":
    main()