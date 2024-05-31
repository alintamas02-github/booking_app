import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'root',
    'database': 'Havenwish'
}

COUNTRY_PRICE_FACTOR = {
    'Timisoara': 1.0,
    'Paris': 1.5,
    'New York': 2.0,
    'London': 1.8,
    'Tokyo': 1.7,
    'Rome': 1.4,
    'Berlin': 1.3,
    'Barcelona': 1.4,
    'Dubai': 2.5,
    'Istanbul': 1.2
}

FACILITY_PRICE_INCREMENT = {
    'Wifi': 10,
    'AC': 15,
    'Pool': 20,
    'Gym': 15,
    'Spa': 25,
    'Restaurant': 20,
    'Bar': 10,
    'Parking': 5,
    'Pet Friendly': 15,
    'Airport Shuttle': 20
}

ROOM_TYPE_CAPACITY = {
    'Single': 1,
    'Double': 2,
    'Suite': 3,
    'Family': 4,
    'Deluxe': 2
}

CAPACITY_PRICE_MULTIPLIER = {
    1: 1.0,
    2: 1.5,
    3: 2.0,
    4: 2.5
}

def get_db_connection():
    connection = mysql.connector.connect(**DB_CONFIG)
    return connection

def round_price_to_nearest_10(price):
    return round(price / 10) * 10

def calculate_base_price(city, facilities):
    base_price = 50
    city_factor = COUNTRY_PRICE_FACTOR.get(city, 1.0)
    facilities_increment = sum(FACILITY_PRICE_INCREMENT.get(facility, 0) for facility in facilities)
    return base_price * city_factor + facilities_increment

def calculate_stars(base_price, num_facilities):
    if base_price > 200 and num_facilities >= 8:
        return 5
    elif base_price > 150 and num_facilities >= 6:
        return 4
    elif base_price > 100 and num_facilities >= 4:
        return 3
    elif base_price > 75 and num_facilities >= 2:
        return 2
    else:
        return 1

def update_room_details_and_stars():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Fetch all hotels with their city and the number of facilities
        cursor.execute("""
            SELECT h.id, h.location, GROUP_CONCAT(f.name) AS facilities
            FROM hotels h
            LEFT JOIN hotel_facilities hf ON h.id = hf.hotel_id
            LEFT JOIN facilities f ON hf.facility_id = f.id
            GROUP BY h.id
        """)
        hotels = cursor.fetchall()

        for hotel in hotels:
            hotel_id = hotel['id']
            city = hotel['location']
            facilities = hotel['facilities'].split(',') if hotel['facilities'] else []
            num_facilities = len(facilities)
            base_price = calculate_base_price(city, facilities)
            stars = calculate_stars(base_price, num_facilities)
            
            # Update hotel stars
            cursor.execute("UPDATE hotels SET stars = %s WHERE id = %s", (stars, hotel_id))
            
            # Fetch rooms for each hotel
            cursor.execute("SELECT id, room_type FROM rooms WHERE hotel_id = %s", (hotel_id,))
            rooms = cursor.fetchall()

            for room in rooms:
                room_id = room['id']
                room_type = room['room_type']
                capacity = ROOM_TYPE_CAPACITY.get(room_type, 1)
                price_multiplier = CAPACITY_PRICE_MULTIPLIER.get(capacity, 1.0)

                # Special price adjustment for Deluxe rooms
                if room_type == 'Deluxe':
                    price_multiplier *= 2

                new_price = round_price_to_nearest_10(base_price * price_multiplier)

                # Update room capacity and price
                cursor.execute("""
                    UPDATE rooms 
                    SET capacity = %s, price = %s 
                    WHERE id = %s
                """, (capacity, new_price, room_id))
        
        connection.commit()
        print("Room details and hotel stars updated successfully.")
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    update_room_details_and_stars()
