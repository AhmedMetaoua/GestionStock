# gestionDeStock

pour installer cette application il faut suivre les étapes suivantes :

1. Cloner le repository
2. Installer les dépendances :

   1. mettre le dossier 'GestionStockApp' sous C:\Utilisateur\nomUtilisateur
   2. ouvrir le terminal et lancer cette commande : python -m PyInstaller --onefile --windowed --add-data "image.png;." --add-data "FACTURE-Copy.xlsx;." --icon="icon.ico" main.

3. Lancer l'application
4. Pour lancer l'application, il faut avoir python 3.9 et les bibliotheque neccessaire

python -m PyInstaller --onefile --windowed --add-data "image.png;." --add-data "FACTURE-Copy.xlsx;." --icon="icon.ico" main.py
