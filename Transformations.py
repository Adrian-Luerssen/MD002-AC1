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

# Nueva función para obtener la distribución de género por país, nico
    def get_gender_distribution_country(self):
        self.cursor.execute("""
            SELECT country, gender, COUNT(*) as count
            FROM users
            JOIN locations ON users.user_id = locations.user_id
            GROUP BY country, gender
            ORDER BY count DESC
        """)
        return self.cursor.fetchall()  

    def close(self):
        self.cursor.close()
        self.conn.close()


def transformation():
    db = Database()
    print("Total users:", db.get_user_count())
    print("Unique countries:", db.get_unique_countries())
    print("Average age:", db.get_average_age())
    db.insert_stat("Average age", db.get_average_age())
    print("Users by country:", db.get_users_by_country())
    print("Most common city:", db.get_common_city())
    print("Gender distribution by country:", db.get_gender_distribution_country()) # Nueva función para obtener la distribución de género por país, nico
    db.close()
    
if __name__ == "__main__":
    transformation()