import sqlite3
import matplotlib

class Database:
    def __init__(self):
        try:
            self.conn = sqlite3.connect("user_data.db")
            self.cursor = self.conn.cursor()
            self.create_tables()
        except Exception as e:
            print("Error connecting to the database:", e)
            exit(1)

    def create_tables(self):
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS stats (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_count INTEGER,
                                stat_name TEXT,
                                stat_value TEXT
                            )
                            """)
        pass
    def insert_stat(self, stat_name:str, stat_value:any):
        self.create_tables()
        self.cursor.execute("SELECT COUNT(*) FROM users")
        user_count = self.cursor.fetchone()[0]
        self.cursor.execute("INSERT INTO stats (user_count, stat_name, stat_value) VALUES (?, ?, ?)", (user_count, stat_name, stat_value))
        self.conn.commit()
        
    def get_user_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        return self.cursor.fetchone()[0]

    def get_unique_countries(self):
        self.cursor.execute("SELECT DISTINCT country FROM locations")
        return [row[0] for row in self.cursor.fetchall()]

    def get_average_age(self):
        self.cursor.execute("""
            SELECT AVG((julianday('now') - julianday(dob)) / 365.25) AS average_age
            FROM users
            WHERE dob IS NOT NULL
        """)
        result = self.cursor.fetchone()
        return result[0] if result is not None else None

    def get_users_by_country(self):
        self.cursor.execute("""
            SELECT country, COUNT(*) as user_count
            FROM locations
            GROUP BY country
        """)
        return {row[0]: row[1] for row in self.cursor.fetchall()}

    def get_common_city(self):
        self.cursor.execute("""
            SELECT city, COUNT(*) as city_count
            FROM locations
            GROUP BY city
            ORDER BY city_count DESC
            LIMIT 1
        """)
        result = self.cursor.fetchone()
        return result if result else None

# Nueva función para obtener la distribución de género por país
    def get_top_gender_distribution_country(self, top_n=10):
        self.cursor.execute("""
            SELECT country, gender, COUNT(*) as count
            FROM users
            JOIN locations ON users.user_id = locations.user_id
            GROUP BY country, gender
            ORDER BY count DESC
            LIMIT ?
        """, (top_n,))
        return self.cursor.fetchall()

# Nueva función para obtener la distribución por generación y país
    def get_top_generation_distribution_country(self, top_n=10):
        self.cursor.execute("""
            SELECT country, generation, COUNT(*) as count
            FROM users
            JOIN locations ON users.user_id = locations.user_id
            GROUP BY country, generation
            ORDER BY count DESC
            LIMIT ?
        """, (top_n,))
        return self.cursor.fetchall()

# Nueva función para obtener la cantidad de usuarios por zona horaria
    def get_user_count_by_timezone(self):
        self.cursor.execute("""
            SELECT timezone, COUNT(*) as user_count
            FROM locations
            GROUP BY timezone
            ORDER BY user_count DESC
        """)
        return self.cursor.fetchall()

# Nueva función para obtener la cantidad de usuarios por continente
    def get_top_user_count_by_continent(self, top_n=10):
        self.cursor.execute("""
            SELECT continent, COUNT(*) as user_count
            FROM locations
            GROUP BY continent
            ORDER BY user_count DESC
            LIMIT ?
        """, (top_n,))
        return self.cursor.fetchall()

# Nueva función para obtener la edad promedio por país
    def get_top_average_age_by_country(self, top_n=10):
        self.cursor.execute("""
            SELECT country, AVG((julianday('now') - julianday(dob)) / 365.25) AS average_age
            FROM users
            JOIN locations ON users.user_id = locations.user_id
            WHERE dob IS NOT NULL
            GROUP BY country
            ORDER BY average_age DESC
            LIMIT ?
        """, (top_n,))
        return self.cursor.fetchall()

# Nueva función para obtener la distribución de 'time_registered'
    def get_time_registered_distribution(self):
        self.cursor.execute("""
            SELECT (strftime('%Y', 'now') - strftime('%Y', date_of_registration)) AS time_registered, COUNT(*) as user_count
            FROM users
            WHERE date_of_registration IS NOT NULL
            GROUP BY time_registered
            ORDER BY time_registered
        """)
        return self.cursor.fetchall()

# Nueva función para obtener la distribución de edad al momento del registro en rangos de 5 años
    def get_age_at_registration_distribution(self):
        self.cursor.execute("""
            SELECT (strftime('%Y', date_of_registration) - strftime('%Y', dob)) AS age_at_registration, COUNT(*) as user_count
            FROM users
            WHERE date_of_registration IS NOT NULL AND dob IS NOT NULL
            GROUP BY age_at_registration
            ORDER BY age_at_registration
        """)
        return self.cursor.fetchall()

# Nueva función para obtener estadísticas de edad al momento del registro por generación
    def get_age_at_registration_by_generation(self):
        self.cursor.execute("""
            WITH AgeData AS (
                SELECT generation,
                    (strftime('%Y', date_of_registration) - strftime('%Y', dob)) AS age
                FROM users
                WHERE date_of_registration IS NOT NULL AND dob IS NOT NULL
            ),
            RankedAges AS (
                SELECT generation,
                    age,
                    ROW_NUMBER() OVER (PARTITION BY generation ORDER BY age) AS row_num,
                    COUNT(*) OVER (PARTITION BY generation) AS total_count
                FROM AgeData
            )
            SELECT generation,
                MIN(age) AS min_age,
                MAX(age) AS max_age,
                AVG(age) AS avg_age,
                CASE 
                    WHEN total_count % 2 = 1 THEN 
                        (SELECT age FROM RankedAges 
                            WHERE row_num = (total_count + 1) / 2 AND generation = RankedAges.generation)
                    ELSE 
                        (SELECT (age + (SELECT age FROM RankedAges 
                                        WHERE row_num = total_count / 2 + 1 AND generation = RankedAges.generation)) / 2.0
                            FROM RankedAges
                            WHERE row_num = total_count / 2 AND generation = RankedAges.generation)
                END AS median_age
            FROM RankedAges
            GROUP BY generation
            ORDER BY generation
        """)
        return self.cursor.fetchall()
    

    def load_stat(self, stat_name:str):
        self.cursor.execute("SELECT user_count,stat_value FROM stats WHERE stat_name = ?", (stat_name,))
        result = self.cursor.fetchall()
        return [[age[0],float(age[1])] for age in result] if result is not None else None

    def close(self):
        self.cursor.close()
        self.conn.close()


def transformation():
    db = Database()
    db.insert_stat("Average age", db.get_average_age())
    

    '''
    print("Users by country:", db.get_users_by_country())
    print("Most common city:", db.get_common_city())
    print("Total users:", db.get_user_count())
    print("Unique countries:", db.get_unique_countries())
    print("Average age:", db.get_average_age())
    print("Gender distribution by country:", db.get_top_gender_distribution_country()) #se aplicara grafico en barras simple
    print("Generation distribution by country:", db.get_top_generation_distribution_country()) #se aplicara grafico en barras apilada
    print("user count by timezone:", db.get_user_count_by_timezone()) #se aplicara grafico en barras simple
    print("user count by continent:", db.get_top_user_count_by_continent()) #se aplicara grafico en barras simple
    print("average age by country:", db.get_top_average_age_by_country()) #se aplicara grafico en barras simple
    print("time registered distribution:", db.get_time_registered_distribution()) #se aplicara grafico en barras simple
    print("age at registration distribution:", db.get_age_at_registration_distribution()) #se aplicara grafico en barras simple
    print("age at registration by generation:", db.get_age_at_registration_by_generation()) #se aplicara grafico en barras simple
    '''


    
    db.close()
    
if __name__ == "__main__":
    transformation()