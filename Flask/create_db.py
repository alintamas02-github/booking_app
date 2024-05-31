import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'root',
    'database': 'Havenwish'
}

def get_db_connection():
    connection = mysql.connector.connect(**DB_CONFIG)
    return connection

def create_table(connection):
    cursor = connection.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hotels (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        location VARCHAR(255) NOT NULL,
        admin_id INT NOT NULL,
        main_photo TEXT,
        stars INT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INT AUTO_INCREMENT PRIMARY KEY,
        hotel_id INT NOT NULL,
        room_type VARCHAR(255) NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        capacity INT NOT NULL,
        FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS photos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        hotel_id INT,
        room_id INT,
        photo TEXT,
        FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE,
        FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facilities (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hotel_facilities (
        hotel_id INT NOT NULL,
        facility_id INT NOT NULL,
        FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE,
        FOREIGN KEY (facility_id) REFERENCES facilities(id) ON DELETE CASCADE,
        PRIMARY KEY (hotel_id, facility_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        hotel_id INT NOT NULL,
        room_id INT NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        people INT NOT NULL,
        FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE,
        FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
    );
    """)

    # Commit the changes and close the connection
    connection.commit()
    cursor.close()
    
create_table(get_db_connection())