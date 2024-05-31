import mysql.connector
import random
import os
from PIL import Image

DB_CONFIG = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'root',
    'database': 'Havenwish'
}

def get_db_connection():
    connection = mysql.connector.connect(**DB_CONFIG)
    return connection

def create_image(file_path):
    # Generate a placeholder image using the Pillow library
    width, height = 800, 600
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    image = Image.new('RGB', (width, height), color)
    image.save(file_path)

def populate_tables():
    cities = ["Timisoara", "Paris", "New York", "London", "Tokyo", "Rome", "Berlin", "Barcelona", "Dubai", "Istanbul"]
    hotel_names = [
        "Hotel Sunshine", "Ocean View", "Mountain Retreat", "City Lights", "Cozy Corner", 
        "Grand Palace", "Royal Suite", "Luxury Stay", "Comfort Inn", "Holiday Home",
        "Paradise Resort", "Eagle Nest", "Palm Tree", "Blue Lagoon", "Riverfront",
        "Seaside Escape", "Green Valley", "Urban Haven", "Serenity Suites", "Golden Sands",
        "Silver Lining", "Majestic Manor", "Sunset Boulevard", "Maple Leaf", "White Orchid",
        "Moonlight Inn", "Starry Night", "Emerald Isle", "Crystal Waters", "Tranquil Lodge",
        "Lakeside Villa", "Vintage Charm", "Sunny Days", "Timeless Stay", "Horizon View",
        "Royal Garden", "Dreamland", "Blissful Stay", "Noble Nest", "Harmony Hotel",
        "Glamour Inn", "Zenith Hotel", "Prestige Palace", "Enchanted Stay", "Mystic Hotel",
        "Radiant Resort", "Splendid Stay", "Grand Horizon", "Sapphire Inn", "Elite Suites",
        "Golden Horizon", "Majestic View", "Premier Palace", "Starlight Stay", "Elysium Hotel",
        "Sunrise Haven", "Forest Retreat", "Crescent Moon", "Aqua Bliss", "Wanderlust Inn",
        "Bayside Breeze", "Peach Blossom", "Snowy Peaks", "Riverside Lodge", "Orchid Retreat",
        "Harbor Lights", "Zen Retreat", "Timberland Lodge", "Whispering Pines", "Desert Rose",
        "Cascade Inn", "Wildflower Hotel", "Sunnyvale Suites", "Maple Grove", "Coral Reef",
        "Sunbeam Inn", "Sandcastle", "Crystal Palace", "Royal Crest", "Echo Valley",
        "Celestial Stay", "Rainbow Ridge", "Autumn Breeze", "Golden Gate", "Aurora Borealis",
        "Mirage Hotel", "Spring Blossom", "Seascape Inn", "Urban Oasis", "Platinum Palace",
        "Opal Inn", "Shimmering Sands", "Mystic Ridge", "Azure Sky", "Imperial Hotel",
        "Galaxy Inn", "Dreamcatcher", "Evergreen Lodge", "Sunlit Shores", "Marigold Hotel",
        "Ivory Tower", "Jade Garden", "Pearl Haven", "Vivid Vistas", "Pinecone Retreat"
    ]
    room_types = ["Single", "Double", "Suite", "Family", "Deluxe"]
    facilities = ["Wifi", "AC", "Pool", "Gym", "Spa", "Restaurant", "Bar", "Parking", "Pet Friendly", "Airport Shuttle"]

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert facilities
        facility_ids = []
        for facility in facilities:
            cursor.execute("INSERT INTO facilities (name) VALUES (%s)", (facility,))
            facility_ids.append(cursor.lastrowid)

        # Insert hotels
        for i in range(100):
            hotel_name = random.choice(hotel_names)
            city = random.choice(cities)
            admin_id = random.randint(1, 10)
            stars = random.randint(1, 5)
            main_photo_path = f"images/{i+1}.jpeg"
            cursor.execute("""
                INSERT INTO hotels (name, location, admin_id, main_photo_path, stars) 
                VALUES (%s, %s, %s, %s, %s)
            """, (hotel_name, city, admin_id, main_photo_path, stars))
            hotel_id = cursor.lastrowid

            # Generate main photo
            create_image(main_photo_path)

            # Insert rooms
            for j in range(random.randint(5, 15)):
                room_type = random.choice(room_types)
                price = round(random.uniform(50, 500), 2)
                capacity = random.randint(1, 5)
                cursor.execute("""
                    INSERT INTO rooms (hotel_id, room_type, price, capacity) 
                    VALUES (%s, %s, %s, %s)
                """, (hotel_id, room_type, price, capacity))
                room_id = cursor.lastrowid

                # Insert photos for rooms
                for k in range(random.randint(1, 5)):
                    photo_path = f"images/{hotel_id}_{k+1}.jpeg"
                    cursor.execute("""
                        INSERT INTO photos (hotel_id, room_id, photo_path) 
                        VALUES (%s, %s, %s)
                    """, (hotel_id, room_id, photo_path))
                    # Generate room photo
                    create_image(photo_path)

            # Assign random facilities to hotels
            for facility_id in random.sample(facility_ids, random.randint(2, 5)):
                cursor.execute("""
                    INSERT INTO hotel_facilities (hotel_id, facility_id) 
                    VALUES (%s, %s)
                """, (hotel_id, facility_id))

        connection.commit()
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    # Create images directory if it doesn't exist
    if not os.path.exists("images"):
        os.makedirs("images")
    
    populate_tables()
    print("Database populated successfully.")
