from datetime import datetime
import requests
import sqlite3
# Set root path of API
api_root = 'https://randomuser.me/'

def get_users(num_users: int = 10):
    try:
        # Make a GET request to the API endpoint using requests.get()
        response = requests.get(api_root + 'api/?results=' + str(num_users),
                                headers={'Accept': 'application/json'})

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            posts = response.json()
            return posts["results"]
        else:
            print('Error:', response.status_code)
            return None
    except Exception as e:
        print('Error:', e)
        return None


# Crear un a clase para guardar los usuarios y los lugares
class User:
    # un constructor para el objecto de usuario
    def __init__(self, user_id: str, first_name: str, last_name: str, gender: str, email: str, phone: str, dob: datetime, age: int , datetime, date_of_registration: datetime, profile_picture: str):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.email = email
        self.phone = phone
        self.dob = dob
        self.age = age #nico le agrego la edad
        self.date_of_registration = date_of_registration
        self.profile_picture = profile_picture

    # un método de clase para crear un objeto de usuario desde un objeto JSON
    @classmethod
    def from_json(cls, data: str):
        return cls(
            user_id=data["login"]["uuid"],
            first_name=data["name"]["first"],
            last_name=data["name"]["last"],
            gender=data["gender"],
            email=data["email"],
            phone=data["phone"],
            dob=datetime.strptime(data["dob"]["date"], "%Y-%m-%dT%H:%M:%S.%fZ"), # transformar la fecha de nacimiento a un objeto de fecha
            age=data["dob"]["age"],  # Nueva línea para extraer la edad
            date_of_registration=datetime.strptime(data["registered"]["date"], "%Y-%m-%dT%H:%M:%S.%fZ"), # transformar la fecha de registro a un objeto de fecha
            profile_picture=data["picture"]["large"]
        )

    def print_user(self):
        print(f"User ID: {self.user_id}")
        print(f"First Name: {self.first_name}")
        print(f"Last Name: {self.last_name}")
        print(f"Email: {self.email}")
        print(f"Phone: {self.phone}")
        print(f"Date of Birth: {self.dob}")
        print(f"age: {self.age}") # Nueva línea para extraer la edad
        print(f"Date of Registration: {self.date_of_registration}")
        print(f"Profile Picture: {self.profile_picture}")
        return self

    def insert_user(self):
        db = Database() # Crear una instancia de la clase Database
        db.insert_user(self) # Llamar al método insert_user() de la clase Database
        db.close()


class Location:
    # un constructor para el objecto de lugar
    def __init__(self, user_id: str, city: str, coordinates: list[float], country: str, postcode: int, state: str, street_name: str, street_number: int, timezone: str):
        self.user_id = user_id
        self.city = city
        self.coordinates = coordinates
        self.country = country
        self.postcode = postcode
        self.state = state
        self.street_name = street_name
        self.street_number = street_number
        self.timezone = timezone

    # un método de clase para crear un objeto de lugar desde un objeto JSON
    @classmethod
    def from_json(cls, data):
        return cls(
            user_id=data["login"]["uuid"],
            city=data["location"]["city"],
            coordinates=[data["location"]["coordinates"]["latitude"], data["location"]["coordinates"]["longitude"]], # guardar las coordenadas en una lista
            country=data["location"]["country"],
            postcode=data["location"]["postcode"],
            state=data["location"]["state"],
            street_name=data["location"]["street"]["name"],
            street_number=data["location"]["street"]["number"],
            timezone=data["location"]["timezone"]["description"]
        )

    def insert_location(self):
        db = Database() # Crear una instancia de la clase Database
        db.insert_location(self) # Llamar al método insert_location() de la clase Database
        db.close()

    def print_location(self):
        print(f"City: {self.city}")
        print(f"Coordinates: {self.coordinates}")
        print(f"Country: {self.country}")
        print(f"Postcode: {self.postcode}")
        print(f"State: {self.state}")
        print(f"Street Name: {self.street_name}")
        print(f"Street Number: {self.street_number}")
        print(f"Timezone: {self.timezone}")
        return self


def decode_json(json_data):
    # Crear un objeto de usuario y un objeto de lugar desde un objeto JSON
    user = User.from_json(json_data)
    location = Location.from_json(json_data)
    return user, location


class Database:
    def __init__(self):
        try:
            # Connect to SQLite database
            self.conn = sqlite3.connect("user_data.db")
            self.cursor = self.conn.cursor()
            self.create_table()
        except Exception as e:
            print('Error connecting to DB', e)
            exit(1)

    def create_table(self):
        # crear una tabla de usuarios y una tabla de lugares si no existen
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                gender TEXT,
                email TEXT,
                phone TEXT,
                dob DATE,
                date_of_registration DATE,
                profile_picture TEXT
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS locations (
                user_id TEXT PRIMARY KEY,
                city TEXT,
                coordinates TEXT,
                country TEXT,
                postcode TEXT,
                state TEXT,
                street_name TEXT,
                street_number INTEGER,
                timezone TEXT
            )
            """
        )
        self.conn.commit()

    def drop_tables(self):
        # drop all tables
        self.cursor.execute("select 'drop table ' || name || ';' from sqlite_master where type = 'table';")
        results = self.cursor.fetchall()
        for result in results:
            
            if ("sqlite_sequence" not in result[0]):
                print(result[0])
                self.cursor.execute(result[0])
        self.conn.commit()
    def insert_user(self, user):
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO users (user_id, first_name, last_name, gender, email, phone, dob, date_of_registration, profile_picture)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user.user_id, user.first_name, user.last_name, user.gender, user.email, user.phone, user.dob, user.date_of_registration, user.profile_picture)
        )
        self.conn.commit()

    def insert_location(self, location):
        # Convert coordinates list to a JSON string
        coordinates_json = location.coordinates[0]+ "," + location.coordinates[1]
        self.cursor.execute(
            """
            INSERT INTO locations (user_id, city, coordinates, country, postcode, state, street_name, street_number, timezone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (location.user_id, location.city, coordinates_json, location.country, location.postcode, location.state, location.street_name, location.street_number, location.timezone)
        )
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
 

def reset_db():
    Database().drop_tables()        
def extraction(num_users: int = 10):
    i: int = 0
    # pasar por los resultados de la API y guardar los usuarios y los lugares en la base de datos
    for result in get_users(num_users):
        i += 1
        print("Processing user "+ str(i)+" ...", end="\r")
        user, location = decode_json(result)
        user.insert_user()
        location.insert_location()
        #user.print_user()
        #location.print_location()
    print("Extraction of ",str(num_users)," users completed.")
    
if __name__ == "__main__":
    extraction(500)