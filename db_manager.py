import sqlite3
import os
from pathlib import Path
"""
# Get the directory of the executable or script
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "stock_management.db")
"""
# Chemin permanent pour la base de données (dans le dossier de l'utilisateur)
def get_db_path():
    # Chemin du dossier de l'utilisateur
    user_dir = Path.home() / "GestionStockApp"
    # Créer le dossier s'il n'existe pas
    user_dir.mkdir(exist_ok=True)
    # Chemin complet de la base de données
    return user_dir / "stock_management.db"

db_path = get_db_path()
print('Emplacement de la Base De Donnée : ',db_path)

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table des matières premières
    # cursor.execute('''DELETE FROM matieres_premieres WHERE id = ?;''', (12,))
    # cursor.execute("ALTER TABLE matieres_premieres ADD COLUMN prix_unitaire REAL;")
    # cursor.execute('''UPDATE matieres_premieres SET quantite = ? WHERE id = ?; ''', ('10', '2'))
    cursor.execute('''CREATE TABLE IF NOT EXISTS matieres_premieres (
        id INTEGER PRIMARY KEY,
        nom TEXT NOT NULL,
        reference TEXT UNIQUE NOT NULL,
        quantite REAL NOT NULL,
        prix_unitaire REAL NOT NULL
    )''')

    # Table des matières produites
    # cursor.execute("ALTER TABLE matieres_produites ADD COLUMN fodec TEXT;")
    # cursor.execute('''DELETE FROM matieres_produites WHERE id = ?;''', (6,))
    # cursor.execute('''UPDATE matieres_produites SET fodec = ? WHERE id = ?; ''', ('1', '5'))
    cursor.execute('''CREATE TABLE IF NOT EXISTS matieres_produites (
        id INTEGER PRIMARY KEY,
        nom TEXT NOT NULL,
        reference TEXT UNIQUE NOT NULL,
        quantite REAL NOT NULL,
        prix_unitaire REAL NOT NULL,
        fodec TEXT NOT NULL
    )''')

    # Table des dosages
    cursor.execute('''CREATE TABLE IF NOT EXISTS dosages (
        id INTEGER PRIMARY KEY,
        matiere_produite_reference TEXT NOT NULL,
        matiere_premiere_id INTEGER NOT NULL,
        proportion REAL NOT NULL,
        FOREIGN KEY (matiere_produite_reference) REFERENCES matieres_produites(reference),
        FOREIGN KEY (matiere_premiere_id) REFERENCES matieres_premieres(id)
    )''')


    # Table des bons de livraison
    # cursor.execute('''DROP TABLE IF EXISTS bons_livraison_temp;''')
    # cursor.execute("ALTER TABLE bons_livraison ADD COLUMN num_facture INTEGER;")
    # cursor.execute('''UPDATE bons_livraison SET num_bl = ? WHERE id = ?; ''', ('1', '45'))

    cursor.execute('''CREATE TABLE IF NOT EXISTS bons_livraison (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT ,
        client TEXT NOT NULL,
        num_bl INTEGER ,
        num_facture INTEGER 
    )''')

    # Table d'historique de bon de commande'
    #changer le nom de cette table à ==>  historique_bon_comande
    cursor.execute('''CREATE TABLE IF NOT EXISTS historique_matiere_produite (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        quantite REAL NOT NULL,
        prix_unitaire REAL NOT NULL,
        date_creation DEFAULT CURRENT_TIMESTAMP
    )''')

    # Table d'historique de bon de livraison'
    # cursor.execute("ALTER TABLE historique_bon_livraison ADD COLUMN articles TEXT;")
    # cursor.execute('''DROP TABLE IF EXISTS historique_bon_livraison;''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS historique_bon_livraison (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bon_id INTEGER NOT NULL,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        client TEXT NOT NULL,
        total REAL NOT NULL,
        articles TEXT,
        FOREIGN KEY (bon_id) REFERENCES bons_livraison (id)
    )''')

        # matiere_produite_nom TEXT NOT NULL,
        # quantite REAL NOT NULL,
    cursor.execute('''CREATE TABLE IF NOT EXISTS details_bon_livraison (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bon_livraison_id INTEGER,
        matiere_produite_id INTEGER,
        quantite REAL,
        FOREIGN KEY (bon_livraison_id) REFERENCES bons_livraison(id),
        FOREIGN KEY (matiere_produite_id) REFERENCES matieres_produites(id)
    )''')

    # cursor.execute('''DELETE FROM clients WHERE id = ?;''', (4,))
    cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        adresse TEXT,
        phone TEXT,
        reference TEXT
    )''')

    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(db_path)
