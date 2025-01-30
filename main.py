from db_manager import init_db
from gui import lancer_interface

if __name__ == "__main__":
    # Initialisation de la base de données
    init_db()

    # Lancer l'interface utilisateur
    lancer_interface()
    