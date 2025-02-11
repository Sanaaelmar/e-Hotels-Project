from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import psycopg2
from datetime import *

views = Blueprint('views', __name__)

@views.route('/')
def home():
    current_app.clientID = 0
    return render_template("index1.html")

@views.route('/book', methods = ['GET', 'POST'])
def book():
    clientID = request.args.get('clientID')
    ide = current_app.clientID
    print("The ide is :")
    print(ide)
    print("The client id is :")
    print(clientID)
    if request.method == 'POST':
        conn = connect_db()
        cur = conn.cursor()
        data = request.form
        print("Printing data from book():")
        print(data)
        checkin = request.form.get("checkin_date")
        checkout = request.form.get("checkout_date")
        chaine = request.form.get("hotel_chain")
        city = request.form.get("city")
        cin = date.fromisoformat(checkin)
        cout = date.fromisoformat(checkout)
        if cin > cout:
            flash('Check Out Date must later than Check In date', category='error')
        else:
            cur.execute(f"SELECT hotel.id FROM hotel INNER JOIN chaine ON hotel.chaine_ID=chaine.id AND hotel.addresse = '{city}' AND chaine.nom = '{chaine}';")
            hotel = cur.fetchall()
            if(len(hotel) < 1):
                flash('No hotel meets your search', category='error')
            else:
                cur.close()
                conn.close()
                print("Printing hotel ID from book():")
                print(hotel)
                return redirect(url_for('views.result', hotelID = hotel, clientID = clientID, checkin = checkin, checkout = checkout))
    return render_template("index3.html")

@views.route('/result', methods = ['GET', 'POST'])
def result():
    conn = connect_db()
    cur = conn.cursor()
    if request.method == 'POST':
        clientID = current_app.clientID
        print("Printing clientID in result():")
        print(clientID)
        print("Entering POST in result():")
        room_id = int(request.form['room_id'])
        cin = request.form['cin']
        cout = request.form['cout']
        checkin = date.fromisoformat(cin)
        checkout = date.fromisoformat(cout)
        temp = checkout - checkin
        duration = temp.days
        cur.execute('INSERT INTO reservation (client_ID, chambre_ID, checkin, duration)'
                'VALUES (%s, %s, %s, %s)',
                (f'{clientID}',
                f'{room_id}',
                f'{cin}',
                duration)
                )
        cur.execute(f'SELECT reservation.id FROM reservation WHERE reservation.client_ID = {clientID} AND reservation.chambre_ID = {room_id};')
        res = cur.fetchall()
        
        cur.execute('INSERT INTO archive (type, correspond_ID, client_ID, chambre_ID, checkin, duration)'
                'VALUES (%s, %s, %s, %s, %s, %s)',
                ('res',
                 res[0][0],
                 f'{clientID}',
                f'{room_id}',
                f'{cin}',
                duration)
                )
        print(f"Booking confirmed for room {room_id}!")
        conn.commit()
        cur.close() 
        conn.close()
        return redirect(url_for('views.reservation', roomID = room_id))
    else:
        hotelID = request.args.get('hotelID')
        clientID = request.args.get('clientID')
        cin = request.args.get('checkin')
        cout = request.args.get('checkout')
        checkin = date.fromisoformat(cin)
        checkout = date.fromisoformat(cout)
        print("Printing hotel ID from result():")
        print(hotelID)
        if (len(hotelID) == 4):
            id = hotelID[1]
        else:
            id = hotelID[1:3]
        print("Printing integer ID from result():")
        print(id)
        cur.execute(f"SELECT chaine.nom, hotel.addresse, hotel.rang, hotel.chambre_num, hotel.email, hotel.phone FROM hotel INNER JOIN chaine ON hotel.chaine_ID=chaine.id AND hotel.id = {id};")
        hotel = cur.fetchall()
        print("Printing chaine name from result():")
        print(hotel[0][0])
        rooms = check_available(cur, id, checkin, checkout)
        print("Printing room information from result():")
        print(rooms)
        cur.close()
        conn.close()
    
    return render_template("Result.html", clientID = clientID, rooms = rooms, hotel= hotel, cin = cin, cout = cout)

@views.route('/reservation')
def reservation():
    clientID = current_app.clientID
    print(clientID)
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'SELECT client.nom, client.email, client.date_added FROM client WHERE client.id = {clientID};')
    client = cur.fetchall()
    cur.execute(f'SELECT reservation.id, chambre.id, chambre.numero, chambre.hotel_ID, chambre.prix, chambre.capacite, reservation.checkin, reservation.duration, reservation.client_ID FROM chambre INNER JOIN reservation ON reservation.client_ID = {clientID} AND reservation.chambre_ID = chambre.id;')
    reservations = cur.fetchall()
    print(reservations)
    hotels = []
    for reservation in reservations :
        cur.execute(f"SELECT chaine.nom, hotel.addresse, hotel.rang FROM hotel INNER JOIN chaine ON hotel.chaine_ID=chaine.id AND hotel.id = {reservation[3]};")
        hotel = cur.fetchall()
        hotels.append(hotel[0])
    lengt = len(reservations)
    cur.execute(f'SELECT location.id, chambre.id, chambre.numero, chambre.hotel_ID, chambre.prix, chambre.capacite, location.checkin, location.duration, location.client_ID FROM chambre INNER JOIN location ON location.client_ID = {clientID} AND location.chambre_ID = chambre.id;')
    locations = cur.fetchall()
    print(locations)
    hotelsLoc = []
    for location in locations :
        cur.execute(f"SELECT chaine.nom, hotel.addresse, hotel.rang FROM hotel INNER JOIN chaine ON hotel.chaine_ID=chaine.id AND hotel.id = {location[3]};")
        hotelLoc = cur.fetchall()
        hotelsLoc.append(hotelLoc[0])
    lengtLoc = len(locations)
    print(lengtLoc)
    return render_template("reserv.html", hotels = hotels, reservations = reservations, len = lengt, hotelsLoc = hotelsLoc, lenLoc = lengtLoc, locations = locations, client = client)

@views.route('/signin', methods = ['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get("username")
        password = request.form.get("password")
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(f"SELECT client.id, client.email, client.password FROM client WHERE client.email = '{email}';")
        data = cur.fetchall()
        cur.execute(f"SELECT employe.id, employe.email, employe.password FROM employe WHERE employe.email = '{email}';")
        employeData = cur.fetchall()
        print("Printing client information from signin():")
        print(data)
        if(len(data) < 1):
            if len(employeData) < 1:
                flash('Email doesn\'t exist', category='error')
            elif (password != employeData[0][2]):
                flash('Incorrect password, try again.', category='error')
            else:
                current_app.clientID = employeData[0][0]
                return redirect(url_for('views.admin', clientID = employeData[0][0]))
        elif (password != data[0][2]):
            flash('Incorrect password, try again.', category='error')
        else:
            current_app.clientID = data[0][0]
            return redirect(url_for('views.book', clientID = data[0][0]))
    return render_template("signin.html")

@views.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        nom = request.form.get("nom")
        nas = request.form.get("NAS")
        addresse = request.form.get("addresse")
        card_number = request.form.get("card_number")
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(f"SELECT client.id, client.email, client.password FROM client WHERE client.email = '{email}';")
        data = cur.fetchall()
        if(len(data) > 0):
            flash('Email already exists', category='error')
        elif len(password) < 7:
            flash('Password must be longer than or 7 characters', category='error')
        elif password != password2:
            flash('Passwords don\'t match', category='error')
        else:
            cur.execute('INSERT INTO client (email, password, NAS, nom, addresse, card_number)'
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (f'{email}',
                f'{password}',
                f'{nas}',
                f'{nom}',
                f'{addresse}',
                f'{card_number}')
                )
            flash('Account created successfully', category='success')
            conn.commit()
            cur.close() 
            conn.close()

    return render_template("signup.html")

@views.route('/admin', methods = ['GET', 'POST'])
def admin():
    employeID = current_app.clientID
    conn = connect_db()
    cur = conn.cursor()
    if request.method == 'POST':
        reservationID = int(request.form['reservationID'])
        cur.execute(f'SELECT reservation.client_ID, reservation.chambre_ID, reservation.checkin, reservation.duration FROM reservation WHERE reservation.id = {reservationID};')
        reservation = cur.fetchall()
        cur.execute('INSERT INTO location (client_ID, chambre_ID, checkin, duration)'
                'VALUES (%s, %s, %s, %s)',
                (f'{reservation[0][0]}',
                f'{reservation[0][1]}',
                f'{reservation[0][2]}',
                f'{reservation[0][3]}')
                )
        cur.execute(f'DELETE FROM reservation WHERE reservation.id = {reservationID};')
        cur.execute(f'SELECT location.id FROM location WHERE location.client_ID = {reservation[0][0]} AND location.chambre_ID = {reservation[0][1]};')
        location = cur.fetchall()
        cur.execute(f'SELECT client.card_number FROM client WHERE client.id = {reservation[0][0]};')
        card = cur.fetchall()
        cur.execute('INSERT INTO paiement (location_ID, card_number)'
                'VALUES (%s, %s)',
                (f'{location[0][0]}',
                f'{card[0][0]}'
                )
                )
        cur.execute('INSERT INTO archive (type, correspond_ID, client_ID, chambre_ID, checkin, duration)'
                'VALUES (%s, %s, %s, %s, %s, %s)',
                ('loc',
                 location[0][0],
                 f'{reservation[0][0]}',
                f'{reservation[0][1]}',
                f'{reservation[0][2]}',
                reservation[0][3]
                )
                )
        flash('Reservation confirmed', category='success')
        conn.commit()
        cur.close() 
        conn.close()
    employeID = current_app.clientID
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'SELECT employe.nom, employe.email, employe.role FROM employe WHERE employe.id = {employeID};')
    employe = cur.fetchall()
    cur.execute(f'SELECT reservation.id, chambre.id, chambre.numero, chambre.hotel_ID, chambre.prix, chambre.capacite, reservation.checkin, reservation.duration, reservation.client_ID FROM chambre INNER JOIN reservation ON chambre.hotel_ID = {employeID} AND reservation.chambre_ID = chambre.id;')
    reservations = cur.fetchall()
    lengt = len(reservations)
    return render_template("admin.html", reservations = reservations, len = lengt, employe = employe)
    

def connect_db():
    conn = psycopg2.connect(
            host = "localhost",
            database = "flask_db",
            user = "postgres",
            port = "5432",
            password = "berserk")
    
    return conn

def check_available(cur, hotel_ID, checkin, checkout):
    cur.execute(f'SELECT chambre.id FROM chambre WHERE chambre.hotel_ID = {hotel_ID};')
    rooms = cur.fetchall()
    print(rooms)
    print(rooms[0][0])
    newrooms = []
    for room in rooms:
        cur.execute(f'SELECT reservation.id FROM reservation WHERE reservation.chambre_ID = {room[0]}')
        fodder = cur.fetchall()
        print("Printing fodder from cheeck_available():")
        print(fodder)
        if len(fodder) < 1:
            cur.execute(f"SELECT chambre.id, chambre.numero, chambre.prix, chambre.capacite FROM chambre WHERE chambre.id = {room[0]};")
            temp = cur.fetchall()
            newrooms.append(temp[0])
        else:
            cur.execute(f'SELECT reservation.checkin, reservation.duration FROM reservation')
            temp2 = cur.fetchall()
            reservation = temp2[0][0]
            reservDuration = timedelta(days = temp2[0][1])
            if  not( reservation <= checkin <= reservation + reservDuration
                    or reservation <= checkout <= reservation + reservDuration
                    or checkin <= reservation <= checkout
                    or print(checkin <= reservation + reservDuration <= checkout)):
                cur.execute(f"SELECT chambre.id, chambre.numero, chambre.prix, chambre.capacite FROM chambre WHERE chambre.id = {room[0]};")
                temp = cur.fetchall()
                newrooms.append(temp[0])
    return newrooms