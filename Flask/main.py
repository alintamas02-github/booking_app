import os
import mysql.connector
from mysql.connector import Error
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import *
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
app.static_folder = "templates"
app.secret_key = SECRET_KEY
# Configure CORS to allow credentials
CORS(app, supports_credentials=True)

# Set the session cookie settings
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True,  # This requires HTTPS
)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if 'credentials' not in data:
        return jsonify({'error': 'No credentials parameter provided'}), 400

    credentials = data['credentials']
    credentials['role'] = "admin" if credentials['email'] in ADMIN_EMAILS else "user"
    credentials['google_id'] = credentials['sub']
    credentials.pop('sub')

    session["user_info"] = credentials
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert the user into the database if not already present
        cursor.execute("""
        INSERT INTO users (google_id, email, name, role)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE email = VALUES(email), name = VALUES(name), role = VALUES(role)
        """, (credentials['google_id'], credentials['email'], credentials['name'], credentials['role']))
        connection.commit()
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()

    return jsonify({'message': 'Ok'}), 200


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_info')
    return jsonify({'message': 'Ok'}), 200


@app.route('/user')
def user():
    return jsonify(session.get('user_info'))


def get_current_user():
    if 'user_info' not in session:
        return None
    return session['user_info']


def get_db_connection():
    connection = mysql.connector.connect(**DB_CONFIG)
    return connection


@app.route('/api/cities', methods=['GET'])
def get_cities():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT location FROM hotels")
        cities = cursor.fetchall()
        return jsonify(cities)
    except Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/facilities', methods=['GET'])
def get_facilities():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM facilities")
        facilities = cursor.fetchall()
        return jsonify(facilities)
    except Error as e:
        return jsonify({'error': str(e)})   
    finally:
        cursor.close()
        connection.close()


@app.route('/api/search_hotels', methods=['GET'])
def search_hotels():
    city = request.args.get('city')
    facilities = request.args.getlist('facility')
    num_people = int(request.args.get('num_people'))
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    # Save search parameters in the session
    session['search_params'] = {
        'city': city,
        'start_date': start_date,
        'end_date': end_date,
        'num_people': num_people
    }

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT h.id AS hotel_id, h.name AS hotel_name, h.location, h.stars, r.id AS room_id, r.room_type, r.price
        FROM hotels h
        JOIN rooms r ON h.id = r.hotel_id
        LEFT JOIN bookings b ON r.id = b.room_id
        LEFT JOIN hotel_facilities hf ON h.id = hf.hotel_id
        LEFT JOIN facilities f ON hf.facility_id = f.id
        WHERE h.location = %s
        AND r.capacity = %s
        AND (b.start_date IS NULL OR b.end_date < %s OR b.start_date > %s)
        """
        params = [city, num_people, start_date, end_date]

        if facilities:
            query += " AND f.name IN ({})".format(','.join(['%s']*len(facilities)))
            params.extend(facilities)

        cursor.execute(query, tuple(params))
        hotels = cursor.fetchall()

        # Use a set to track hotel IDs that have already been added
        unique_hotels = {}
        for hotel in hotels:
            if hotel['hotel_id'] not in unique_hotels:
                # Fetch facilities for the hotel
                cursor.execute("""
                SELECT f.name FROM facilities f
                JOIN hotel_facilities hf ON f.id = hf.facility_id
                WHERE hf.hotel_id = %s
                """, (hotel['hotel_id'],))
                hotel_facilities = cursor.fetchall()
                hotel['facilities'] = [facility['name'] for facility in hotel_facilities]

                unique_hotels[hotel['hotel_id']] = hotel
        return jsonify(list(unique_hotels.values()))
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/api/book_room', methods=['POST'])
def book_room():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401

    if 'search_params' not in session:
        return jsonify({'error': 'No search parameters found in session'}), 400

    data = request.json

    if 'room_id' not in data:
        return jsonify({'error': 'No room_id parameterer provided'}), 400

    room_id = data['room_id']

    user_email = user["email"]
    user_name = user["name"]
    start_date = session['search_params']['start_date']
    end_date = session['search_params']['end_date']
    num_people = session['search_params']['num_people']

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch room and hotel details
        cursor.execute("""
        SELECT r.id as room_id, r.price, h.name as hotel_name, h.id as hotel_id 
        FROM rooms r
        JOIN hotels h ON r.hotel_id = h.id
        WHERE r.id = %s
        """, (room_id,))
        room = cursor.fetchone()

        if not room:
            return jsonify({'error': 'Room not found'}), 404

        hotel_id = room['hotel_id']
        room_price = room['price']
        hotel_name = room['hotel_name']
        user_id = user['google_id']

        # Create the booking
        cursor.execute("""
        INSERT INTO bookings (hotel_id, room_id, start_date, end_date, people, user_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (hotel_id, room_id, start_date, end_date, num_people, user_id))
        connection.commit()

        # Send booking confirmation email
        subject = "Booking Confirmation"
        body = f"Dear {user_name},\n\nYour booking has been confirmed.\n\nBooking details:\nHotel: {hotel_name}\nRoom ID: {room_id}\nStart Date: {start_date}\nEnd Date: {end_date}\nNumber of People: {num_people}\nPrice: {room_price}\n\nThank you for booking with us!"
        send_email(user_email, subject, body)

        return jsonify({'room_id': room_id}), 201
    except Error as e:
        print(e)
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/hotel_photo/<int:hotel_id>', methods=['GET'])
def get_hotel_photo(hotel_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT main_photo_path FROM hotels WHERE id = %s", (hotel_id,))
        photo = cursor.fetchone()
        if not photo:
            return jsonify({'error': 'Hotel not found'}), 404

        print(photo)
        photo_path = photo['main_photo_path']
        if not os.path.exists(photo_path):
            return jsonify({'error': 'Photo not found'}), 404

        return send_file(photo_path, mimetype='image/jpeg')
    except Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()
    

@app.route('/api/room_photo/<int:room_id>', methods=['GET'])
def get_room_photo(room_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT photo_path FROM photos WHERE room_id = %s", (room_id,))
        photo = cursor.fetchone()
        if not photo:
            return jsonify({'error': 'Room photo not found'}), 404

        photo_path = photo['photo_path']
        if not os.path.exists(photo_path):
            return jsonify({'error': 'Photo file not found'}), 404

        return send_file(photo_path, mimetype='image/jpeg')
    except Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/user_bookings', methods=['GET'])
def get_user_bookings():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401

    user_id = user['google_id']

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
        SELECT b.id, b.hotel_id, h.name as hotel_name, b.room_id, b.start_date, b.end_date, b.people
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.id
        WHERE b.user_id = %s
        """, (user_id,))
        bookings = cursor.fetchall()

        return jsonify(bookings)
    except Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/cancel_booking', methods=['POST'])
def cancel_booking():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401

    data = request.json

    if 'booking_id' not in data:
        return jsonify({'error': 'No booking_id parameter provided'}), 400

    booking_id = data['booking_id']

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
        DELETE FROM bookings 
        WHERE id = %s AND user_id = %s
        """, (booking_id, user['google_id']))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Booking not found or not authorized to cancel'}), 404

        return jsonify({'message': 'Booking canceled successfully'})
    except Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/admin/add_hotel', methods=['POST'])
def add_hotel():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'User not authorized'}), 403

    data = request.form.to_dict()
    print(data)

    if 'name' not in data:
        return jsonify({'error': 'No name parameter provided'}), 400
    if 'location' not in data:
        return jsonify({'error': 'No location parameter provided'}), 400
    if 'stars' not in data:
        return jsonify({'error': 'No stars parameter provided'}), 400

    name = data['name']
    location = data['location']
    stars = data['stars']
    main_photo = request.files.get('main_photo')
    print(main_photo)
    facilities = data.get('facilities', '')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Save the main photo
        main_photo_path = None
        if main_photo:
            filename = secure_filename(main_photo.filename)
            main_photo_path = os.path.join(IMAGE_FOLDER, filename)
            main_photo.save(main_photo_path)

        cursor.execute("""
        INSERT INTO hotels (name, location, admin_id, main_photo_path, stars) 
        VALUES (%s, %s, %s, %s, %s)
        """, (name, location, user['google_id'], main_photo_path, stars))
        hotel_id = cursor.lastrowid

        if facilities:
            facility_list = [facility.strip() for facility in facilities.split(',')]
            for facility in facility_list:
                print(facility)
                cursor.execute("""
                INSERT INTO hotel_facilities (hotel_id, facility_id)
                SELECT %s, id FROM facilities WHERE name = %s
                """, (hotel_id, facility))

        connection.commit()

        return jsonify({'message': 'Hotel added successfully', 'hotel_id': hotel_id})
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/admin/hotels', methods=['GET'])
def get_admin_hotels():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'User not authorized'}), 403

    admin_id = user['google_id']

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
        SELECT id, name, location, main_photo_path, stars
        FROM hotels
        WHERE admin_id = %s
        """, (admin_id,))
        hotels = cursor.fetchall()

        for hotel in hotels:
            cursor.execute("""
            SELECT f.name FROM facilities f
            JOIN hotel_facilities hf ON f.id = hf.facility_id
            WHERE hf.hotel_id = %s
            """, (hotel['id'],))
            hotel_facilities = cursor.fetchall()
            hotel['facilities'] = [facility['name'] for facility in hotel_facilities]
        print(hotels)
        return jsonify(hotels)
    except Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/admin/edit_hotel', methods=['POST'])
def edit_hotel():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'User not authorized'}), 403

    data = request.form.to_dict()

    if 'hotel_id' not in data:
        return jsonify({'error': 'No hotel_id parameter provided'}), 400

    hotel_id = data['hotel_id']
    name = data.get('name')
    location = data.get('location')
    stars = data.get('stars')
    main_photo = request.files.get('main_photo')
    facilities = data.get('facilities', '')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the hotel belongs to the admin
        cursor.execute("SELECT admin_id FROM hotels WHERE id = %s", (hotel_id,))
        hotel = cursor.fetchone()
        if not hotel or hotel[0] != user['google_id']:
            return jsonify({'error': 'Hotel not found or not authorized to edit'}), 404

        update_fields = []
        params = []

        if name:
            update_fields.append("name = %s")
            params.append(name)
        if location:
            update_fields.append("location = %s")
            params.append(location)
        if stars:
            update_fields.append("stars = %s")
            params.append(stars)

        if main_photo:
            filename = secure_filename(main_photo.filename)
            main_photo_path = os.path.join(IMAGE_FOLDER, filename)
            main_photo.save(main_photo_path)
            update_fields.append("main_photo_path = %s")
            params.append(main_photo_path)

        if update_fields:
            params.append(hotel_id)
            cursor.execute(f"""
            UPDATE hotels 
            SET {', '.join(update_fields)}
            WHERE id = %s
            """, tuple(params))

        if facilities:
            # First, remove existing facilities for the hotel
            cursor.execute("DELETE FROM hotel_facilities WHERE hotel_id = %s", (hotel_id,))
            # Then, add the new facilities
            facility_list = [facility.strip() for facility in facilities.split(',')]
            for facility in facility_list:
                cursor.execute("""
                INSERT INTO hotel_facilities (hotel_id, facility_id)
                SELECT %s, id FROM facilities WHERE name = %s
                """, (hotel_id, facility))

        connection.commit()

        return jsonify({'message': 'Hotel updated successfully'})
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/admin/hotel_bookings', methods=['GET'])
def get_hotel_bookings():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'User not authorized'}), 403

    hotel_id = request.args.get('hotel_id')
    if not hotel_id:
        return jsonify({'error': 'No hotel_id parameter specified'}), 400
    
    admin_id = user['google_id']

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if the hotel belongs to the admin
        cursor.execute("SELECT admin_id FROM hotels WHERE id = %s", (hotel_id,))
        hotel = cursor.fetchone()
        if not hotel or hotel['admin_id'] != admin_id:
            return jsonify({'error': 'Hotel not found or not authorized to view bookings'}), 404

        cursor.execute("""
        SELECT b.id, b.room_id, b.start_date, b.end_date, b.people, u.name as user_name, u.email as user_email
        FROM bookings b
        JOIN users u ON b.user_id = u.google_id
        WHERE b.hotel_id = %s
        """, (hotel_id,))
        bookings = cursor.fetchall()
        print(bookings)
        return jsonify(bookings)
    except Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/admin/add_room', methods=['POST'])
def add_room():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'User not authorized'}), 403

    data = request.form.to_dict()
    print(data)

    if 'hotel_id' not in data:
        return jsonify({'error': 'No hotel_id parameter provided'}), 400
    if 'room_type' not in data:
        return jsonify({'error': 'No room_type parameter provided'}), 400
    if 'price' not in data:
        return jsonify({'error': 'No price parameter provided'}), 400
    if 'capacity' not in data:
        return jsonify({'error': 'No capacity parameter provided'}), 400

    hotel_id = data['hotel_id']
    room_type = data['room_type']
    price = data['price']
    capacity = data['capacity']
    room_photo = request.files.get('room_photo')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the hotel belongs to the admin
        cursor.execute("SELECT admin_id FROM hotels WHERE id = %s", (hotel_id,))
        hotel = cursor.fetchone()
        if not hotel or hotel[0] != user['google_id']:
            return jsonify({'error': 'Hotel not found or not authorized to add rooms'}), 404

        cursor.execute("""
        INSERT INTO rooms (hotel_id, room_type, price, capacity)
        VALUES (%s, %s, %s, %s)
        """, (hotel_id, room_type, price, capacity))
        room_id = cursor.lastrowid

        if room_photo:
            filename = secure_filename(room_photo.filename)
            room_photo_path = os.path.join(IMAGE_FOLDER, filename)
            room_photo.save(room_photo_path)

            cursor.execute("""
            INSERT INTO photos (hotel_id, room_id, photo_path)
            VALUES (%s, %s, %s)
            """, (hotel_id, room_id, room_photo_path))

        connection.commit()

        return jsonify({'message': 'Room added successfully', 'room_id': room_id})
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/admin/edit_room', methods=['POST'])
def edit_room():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'User not authorized'}), 403

    data = request.form.to_dict()

    if 'room_id' not in data:
        return jsonify({'error': 'No room_id parameter provided'}), 400

    room_id = data['room_id']
    room_type = data.get('room_type')
    price = data.get('price')
    capacity = data.get('capacity')
    room_photo = request.files.get('room_photo')

    if not room_id:
        return jsonify({'error': 'Room ID is required'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the room belongs to a hotel managed by the admin
        cursor.execute("""
        SELECT r.hotel_id, h.admin_id 
        FROM rooms r
        JOIN hotels h ON r.hotel_id = h.id
        WHERE r.id = %s
        """, (room_id,))
        room = cursor.fetchone()
        if not room or room[1] != user['google_id']:
            return jsonify({'error': 'Room not found or not authorized to edit'}), 404

        update_fields = []
        params = []

        if room_type:
            update_fields.append("room_type = %s")
            params.append(room_type)
        if price:
            update_fields.append("price = %s")
            params.append(price)
        if capacity:
            update_fields.append("capacity = %s")
            params.append(capacity)

        if room_photo:
            filename = secure_filename(room_photo.filename)
            room_photo_path = os.path.join(IMAGE_FOLDER, filename)
            room_photo.save(room_photo_path)

            cursor.execute("""
            INSERT INTO photos (hotel_id, room_id, photo_path)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE photo_path = VALUES(photo_path)
            """, (room['hotel_id'], room_id, room_photo_path))

        if update_fields:
            params.append(room_id)
            cursor.execute(f"""
            UPDATE rooms 
            SET {', '.join(update_fields)}
            WHERE id = %s
            """, tuple(params))
            connection.commit()

        return jsonify({'message': 'Room updated successfully'})
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/admin/hotel_rooms', methods=['GET'])
def get_hotel_rooms():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'User not authorized'}), 403

    hotel_id = request.args.get('hotel_id')
    if not hotel_id:
        return jsonify({'error': 'No hotel_id parameter specified'}), 400
    
    admin_id = user['google_id']

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if the hotel belongs to the admin
        cursor.execute("SELECT admin_id FROM hotels WHERE id = %s", (hotel_id,))
        hotel = cursor.fetchone()
        if not hotel or hotel['admin_id'] != admin_id:
            return jsonify({'error': 'Hotel not found or not authorized to view rooms'}), 404

        cursor.execute("""
        SELECT id, room_type, price, capacity
        FROM rooms
        WHERE hotel_id = %s
        """, (hotel_id,))
        rooms = cursor.fetchall()   
        print(rooms)
        return jsonify(rooms)
    except Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/admin/remove_hotel', methods=['POST'])
def remove_hotel():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'User not authorized'}), 403

    data = request.json
    if 'hotel_id' not in data:
         return jsonify({'error': 'No hotel_id parameter provided'}), 400

    hotel_id = data['hotel_id']

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the hotel belongs to the admin
        cursor.execute("SELECT admin_id FROM hotels WHERE id = %s", (hotel_id,))
        hotel = cursor.fetchone()
        if not hotel or hotel[0] != user['google_id']:
            return jsonify({'error': 'Hotel not found or not authorized to remove'}), 404

        # Delete the hotel
        cursor.execute("DELETE FROM hotels WHERE id = %s", (hotel_id,))
        connection.commit()

        return jsonify({'message': 'Hotel removed successfully'})
    except Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


@app.route('/api/admin/remove_room', methods=['POST'])
def remove_room():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'User not authorized'}), 403

    data = request.json

    if 'room_id' not in data:
        return jsonify({'error': 'No room_id parameter provided'}), 400
    
    room_id = data['room_id']

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the room belongs to a hotel managed by the admin
        cursor.execute("""
        SELECT r.hotel_id, h.admin_id 
        FROM rooms r
        JOIN hotels h ON r.hotel_id = h.id
        WHERE r.id = %s
        """, (room_id,))
        room = cursor.fetchone()
        if not room or room[1] != user['google_id']:
            return jsonify({'error': 'Room not found or not authorized to remove'}), 404

        # Delete the room
        cursor.execute("DELETE FROM rooms WHERE id = %s", (room_id,))
        connection.commit()

        return jsonify({'message': 'Room removed successfully'})
    except Error as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()


def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_CONFIG['smtp_username']
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['smtp_username'], EMAIL_CONFIG['smtp_password'])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['smtp_username'], to_email, text)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == '__main__':
    app.run(debug=True, host=SERVER_IP, port=SERVER_PORT, ssl_context=('server.crt', 'server.key'))

