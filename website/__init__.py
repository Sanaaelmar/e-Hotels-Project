from flask import Flask
import psycopg2

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    from .views import views

    app.clientID = 0

    create_database()

    app.register_blueprint(views, url_prefix = '/')
    print("Starting app")

    return app

def create_database():
    conn = psycopg2.connect(
            host = "localhost",
            database = "flask_db",
            user = "postgres",
            port = "5432",
            password = "berserk")
    
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS chaine CASCADE;')
    cur.execute('DROP TABLE IF EXISTS hotel CASCADE;')
    cur.execute('DROP TABLE IF EXISTS chambre CASCADE;')
    cur.execute('DROP TABLE IF EXISTS client;')
    cur.execute('DROP TABLE IF EXISTS reservation;')
    cur.execute('DROP TABLE IF EXISTS location;')
    cur.execute('DROP TABLE IF EXISTS employe;')
    cur.execute('DROP TABLE IF EXISTS paiement;')
    cur.execute('DROP TABLE IF EXISTS archive;')
    cur.execute('DROP TABLE IF EXISTS reservation_log;')
    
    cur.execute('CREATE TABLE chaine (id serial PRIMARY KEY,'
                                 'nom varchar (150) NOT NULL,'
                                 'addresse varchar (50) NOT NULL,'
                                 'hotel_num integer NOT NULL,'
                                 'email varchar (150) NOT NULL,'
                                 'phone varchar(20) NOT NULL);'
                                 )
    
    
    
    cur.execute('CREATE TABLE hotel (id serial PRIMARY KEY,'
                                 'rang integer NOT NULL,'
                                 'addresse varchar (50) NOT NULL,'
                                 'chambre_num integer NOT NULL,'
                                 'email varchar (150) NOT NULL,'
                                 'phone varchar(20) NOT NULL,'
                                 'chaine_ID integer,'
                                 'reservation_count integer,'
                                 'CONSTRAINT fk_chaine '
                                 'FOREIGN KEY (chaine_ID) '
                                 'REFERENCES chaine (id) '
                                 'ON DELETE CASCADE);'
                                 )
    
    
    
    cur.execute('CREATE TABLE chambre (id serial PRIMARY KEY,'
                                'numero integer NOT NULL,'
                                 'hotel_ID integer NOT NULL,'
                                 'prix integer NOT NULL,'
                                 'capacite integer NOT NULL,'
                                 'CONSTRAINT fk_hotel '
                                 'FOREIGN KEY (hotel_ID) '
                                 'REFERENCES hotel (id) '
                                 'ON DELETE CASCADE);'
                                 )
    
    cur.execute('CREATE TABLE client (id serial PRIMARY KEY,'
                                'email varchar (150) NOT NULL,'
                                'password varchar (150) NOT NULL,'
                                'NAS integer NOT NULL,'
                                'nom varchar (150) NOT NULL,'
                                'addresse varchar (150) NOT NULL,'
                                'card_number varchar (150) NOT NULL,'
                                'date_added date DEFAULT CURRENT_TIMESTAMP);'
                                 )
    
    cur.execute('CREATE TABLE reservation (id serial PRIMARY KEY,'
                                'client_ID integer NOT NULL,'
                                'chambre_ID integer NOT NULL,'                       
                                'checkin DATE NOT NULL, '
                                'duration integer NOT NULL'
                                ');'
                                 )
    
    cur.execute('CREATE TABLE employe (id serial PRIMARY KEY,'
                                'email varchar (150) NOT NULL,'
                                'password varchar (150) NOT NULL,'
                                'NAS integer NOT NULL,'
                                'hotel_ID integer NOT NULL,'
                                'nom varchar (150) NOT NULL,'
                                'addresse varchar (150) NOT NULL,'
                                'role varchar (150) NOT NULL);'
                                 )
    
    cur.execute('CREATE TABLE location (id serial PRIMARY KEY,'
                                'client_ID integer NOT NULL,'
                                'chambre_ID integer NOT NULL,'                       
                                'checkin DATE NOT NULL, '
                                'duration integer NOT NULL'
                                ');'
                                 )
    
    cur.execute('CREATE TABLE paiement (id serial PRIMARY KEY,'
                                'location_ID integer NOT NULL,'
                                'card_number varchar (150) NOT NULL'
                                ');'
                                 )
    
    cur.execute('CREATE TABLE archive (id serial PRIMARY KEY,'
                                'type varchar (150) NOT NULL,'
                                'correspond_ID integer NOT NULL,'
                                'client_ID integer NOT NULL,'
                                'chambre_ID integer NOT NULL,'                       
                                'checkin DATE NOT NULL, '
                                'duration integer NOT NULL'
                                ');'
                                 )
    
    cur.execute('CREATE VIEW chambres_disponibles_hotel AS '
                'SELECT c.id AS chambre_id, c.numero AS numero_chambre, c.prix AS prix_chambre, c.capacite AS capacite_chambre '
                'FROM chambre c '
                'LEFT JOIN reservation r ON c.id = r.chambre_ID ' 
                'WHERE r.id IS NULL;')
    
    cur.execute('CREATE VIEW chambres_disponibles_par_adresse AS '
                'SELECT h.addresse AS adresse_hotel, '
                    'c.id AS chambre_id, '
                    'c.numero AS numero_chambre, '
                    'c.prix AS prix_chambre,'
                    'c.capacite AS capacite_chambre '
                'FROM hotel h '
                'JOIN chambre c ON h.id = c.hotel_ID '
                'LEFT JOIN reservation r ON c.id = r.chambre_ID '
                'WHERE r.id IS NULL '
                'GROUP BY h.addresse, c.id;')
    
    cur.execute('CREATE TABLE reservation_log(reservation_id integer PRIMARY KEY)')
    
    cur.execute('CREATE INDEX idx_chaine_hoteliere ON hotel(chaine_ID);')
    cur.execute('CREATE INDEX I1_NumChambre On chambre(numero);')
    cur.execute('CREATE INDEX I3_Chambre On chambre(hotel_ID);')
    
    cur.execute('CREATE OR REPLACE FUNCTION log_new_reservation() '
                'RETURNS TRIGGER AS $$ '
                'BEGIN '
                    'INSERT INTO reservation_log(reservation_id) '
                    'VALUES (NEW.id);'
                    'RETURN NEW;'
                'END;'
                '$$ LANGUAGE plpgsql;'

                'CREATE TRIGGER trigger_log_new_reservation '
                'AFTER INSERT ON reservation '
                'FOR EACH ROW '
                'EXECUTE FUNCTION log_new_reservation();')
    
    cur.execute('CREATE OR REPLACE FUNCTION update_hotel_reservation_count()'
                'RETURNS TRIGGER AS $$'
                'BEGIN '
                    'UPDATE hotel SET reservation_count = reservation_count + 1 '
                    'WHERE id = (SELECT hotel_ID FROM chambre WHERE id = NEW.chambre_ID);'
                    'RETURN NEW;'
                'END;'
                '$$ LANGUAGE plpgsql;'

                'CREATE TRIGGER trigger_update_hotel_reservation_count '
                'AFTER INSERT ON reservation '
                'FOR EACH ROW '
                'EXECUTE FUNCTION update_hotel_reservation_count();')
    
    cur.execute('INSERT INTO chaine (nom, addresse, hotel_num, email, phone)'
                'VALUES (%s, %s, %s, %s, %s)',
                ('Accora',
                'Hello St, New York',
                8,
                'admin@accora.com',
                '1234567890'
                )
                )
    
    cur.execute('INSERT INTO chaine (nom, addresse, hotel_num, email, phone)'
                'VALUES (%s, %s, %s, %s, %s)',
                ('Four Season',
                'Hello St, New York',
                8,
                'admin@4season.com',
                '1234567890'
                )
                )
    
    cur.execute('INSERT INTO chaine (nom, addresse, hotel_num, email, phone)'
                'VALUES (%s, %s, %s, %s, %s)',
                ('Ritz-Carlton',
                'Hello St, New York',
                8,
                'admin@ritz.com',
                '1234567890'
                )
                )
    
    cur.execute('INSERT INTO chaine (nom, addresse, hotel_num, email, phone)'
                'VALUES (%s, %s, %s, %s, %s)',
                ('Marriott',
                'Hello St, New York',
                8,
                'admin@marriott.com',
                '1234567890'
                )
                )
    
    cur.execute('INSERT INTO chaine (nom, addresse, hotel_num, email, phone)'
                'VALUES (%s, %s, %s, %s, %s)',
                ('Hyatt',
                'Hello St, New York',
                8,
                'admin@hyatt.com',
                '1234567890'
                )
                )
    
    chaine = ['accora', '4season', 'ritz', 'marriott', 'hyatt']
    hotels_rank = [[3,4,3,5,3,4,5,3],[4,4,4,5,4,3,4,5],[5,3,4,4,3,3,4,5],[4,4,4,4,4,3,4,5],[3,4,5,3,4,3,4,5]]
    hotels_address = [['Montreal', 'Quebec City', 'Toronto', 'Ottawa', 'New York City', 'Buffalo', 'Los Angeles', 'San Francisco'], 
                      ['Buffalo', 'Los Angeles', 'San Francisco','San Diego', 'Vancouver', 'Victoria', 'Miami', 'Orlando'], 
                      ['Victoria', 'Miami', 'Orlando', 'Boston', 'Los Angeles', 'Montreal', 'Quebec City', 'Toronto'],
                      ['San Francisco','Montreal', 'Quebec City', 'Toronto', 'Ottawa', 'New York City', 'Buffalo', 'Los Angeles'],
                      ['New York City', 'Buffalo', 'Los Angeles', 'San Francisco','Montreal', 'Vancouver', 'Toronto', 'Miami']]
    
    for i in range(1,6):
        for j in range(0,8):
            cur.execute('INSERT INTO hotel (rang, addresse, chambre_num, email, phone, chaine_ID)'
                        'VALUES (%s, %s, %s, %s, %s, %s)',
                        (hotels_rank[i-1][j],
                        hotels_address[i-1][j],
                        5,
                        hotels_address[i-1][j] + '@' + chaine[i-1]+'.com',
                        '+1 234 567 8901',
                        i)
                        )
            cur.execute('INSERT INTO employe (email, password, NAS, hotel_ID, nom, addresse, role)'
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        ('employe'+ str(j) + '@' + chaine[i-1]+'.com',
                        '1234567',
                        111222333,
                        j+(i-1)*8+1,
                        'James ' + chaine[i-1],
                        '70 Rue Here',
                        'Manager')
                        )
            
    capacite = 0
    for i in range(1,41):
        for j in range(1,6):
            if (j < 3):
                capacite = j
            else:
                capacite = 3

            
            cur.execute('INSERT INTO chambre (numero, hotel_ID, prix, capacite)'
                        'VALUES (%s, %s, %s, %s)',
                        (j,
                        i,
                        capacite * 100,
                        capacite)
                        )
    
    cur.execute('INSERT INTO client (email, password, NAS, nom, addresse, card_number)'
                'VALUES (%s, %s, %s, %s, %s, %s)',
                ('allo@gmail.com',
                 '1234567',
                111222333,
                'Tim',
                '70 Rue Here',
                '1111222233334444')
                )
    
    cur.execute('INSERT INTO reservation (client_ID, chambre_ID, checkin, duration)'
                'VALUES (%s, %s, %s, %s)',
                (1,
                128,
                '2024-04-13',
                9)
                )
    
    cur.execute('INSERT INTO archive (type, correspond_ID, client_ID, chambre_ID, checkin, duration)'
                'VALUES (%s, %s, %s, %s, %s, %s)',
                ('res',
                 1,
                 1,
                128,
                '2024-04-13',
                9)
                )
    
    
    cur.execute('INSERT INTO reservation (client_ID, chambre_ID, checkin, duration)'
                'VALUES (%s, %s, %s, %s)',
                (1,
                23,
                '2024-04-13',
                9)
                )
    
    cur.execute('INSERT INTO archive (type, correspond_ID, client_ID, chambre_ID, checkin, duration)'
                'VALUES (%s, %s, %s, %s, %s, %s)',
                ('res',
                 2,
                 1,
                23,
                '2024-04-13',
                9)
                )
    
    cur.execute('SELECT reservation.id, reservation.chambre_ID, reservation.checkin FROM reservation;')
    reservations = cur.fetchall()
    print(reservations)
    print(reservations[0][2].year)
    print(type(reservations[0][2]))


    
    
    # commit the changes 
    conn.commit()
    
    # close the cursor and connection 
    cur.close() 
    conn.close() 
    