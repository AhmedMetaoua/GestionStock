import json
import tkinter as tk
from tkinter import END, messagebox, ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import csv
import os
import sys

globalId1 = ''
def majGlobale(id,tab) :
    try:
        # Connexion à la base de données pour récupérer le nom
        conn = get_connection()  
        cursor = conn.cursor()
        if (tab==0):
            cursor.execute("SELECT nom,prix_unitaire FROM matieres_premieres WHERE id = ?", (id,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return str(result[0]),str(result[1]) 
        elif (tab==1):  
            cursor.execute("SELECT nom,prix_unitaire,fodec FROM matieres_produites WHERE id = ?", (str(id),))
            result = cursor.fetchone()
            conn.close()
            print('result=',result[0],result[1],result[2])
            if result:
                return str(result[0]),str(result[1]),str(result[2])  
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la récupération du nom: {e}")


from business_logic import (
    ajouter_matiere_premiere,
    modifier_quantite_matiere_premiere,
    mettre_aJour_produit_fini,
    ajouter_dosage,
    ajouter_client,
    creer_bon_de_commande,
    creer_bon_livraison,
)
from db_manager import get_connection
    
def valid(P):
            try:
                if P == "":
                    return True
                float(P)
                return True
            except ValueError:
                return False
            
def get_client_data(table, nom): 
    """
    Récupère toutes les informations d'un client depuis la table spécifiée.
    Args:
        table (str): Nom de la table (ex: "clients").
        nom (str): Nom du client (recherche partielle possible).
    Returns:
        dict: Dictionnaire contenant 'nom', 'adresse', 'phone', 'reference', ou None si non trouvé.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = f"SELECT nom, adresse, phone, reference FROM {table} WHERE nom LIKE ?"
    cursor.execute(query, (f"%{nom}%",))  # Sécurisé contre les injections SQL
    
    row = cursor.fetchone()  # Récupère un seul résultat
    conn.close()

    if row:
        return {
            "nom": row[0],
            "adresse": row[1],
            "phone": row[2],
            "reference": row[3]
        }
    return None  # Aucun client trouvé


def get_suggestions(table, column):
    """
    Récupère les suggestions depuis la base de données.
    
    Args:
        table (str): Nom de la table.
        column (str): Nom de la colonne.
    
    Returns:
        list: Liste des valeurs uniques de la colonne.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT {column} FROM {table}")
    suggestions = [row[0] for row in cursor.fetchall()]
    conn.close()
    return suggestions


def get_table_data(table):
    """
    Récupère toutes les données d'une table pour l'afficher dans un tableau.
    
    Args:
        table (str): Nom de la table.
    
    Returns:
        list: Liste des lignes de la table.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_historique_matiere_produite():
    """
    Récupère l'historique des matières produites depuis la base de données.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM historique_matiere_produite ORDER BY date_creation DESC")
        historique = cursor.fetchall()
        conn.close()
        return historique
    except Exception as e:
        raise Exception(f"Erreur lors de la récupération de l'historique : {e}")


def get_historique_bon_livraison():
    """
    Récupère l'historique des bons de livraison.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Récupérer l'historique des bons avec leurs détails
    cursor.execute("""
        SELECT bon_id, articles, total, client, date_creation
        FROM historique_bon_livraison
    """)
    historique = cursor.fetchall()
    conn.close()
    return historique


def lancer_interface():
    # Couleurs du thème (rendu un peu plus clair pour simuler la transparence)
    BG_COLOR = "#0aa893" #76b5c5"  # bleu claire  #abdbe3
    BTN_COLOR = "#2a4684"  #154c79"  # bleu foncé
    BTN_TEXT_COLOR = "#ffffff"
    ENTRY_BG = "#ffffff"
    ENTRY_FG = "#000000"
    TABLE_BG = "#f5f5f5"  # Gris clair

    # Créer la fenêtre principale
    root = tk.Tk()
    root.title("Gestion de Stock")

    # Récupérer la taille de l'écran
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Dimensions de la fenêtre
    window_width = 900
    window_height = 650

    # Calculer les coordonnées pour centrer la fenêtre
    x = max(0, (screen_width - window_width) // 2)
    y = max(0, (screen_height - window_height) // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{30}")
    # root.geometry("900x650")
    root.resizable(False, False)
    root.config(bg=BG_COLOR)

    # Get the path to the folder containing images
    if getattr(sys, 'frozen', False):  # If the app is frozen (packed .exe)
        base_path = sys._MEIPASS  # Get the temporary folder where resources are extracted
    else:
        base_path = os.path.abspath(".")  # Normal execution, using the current folder
    # Construct the full path to the image
    image_path = os.path.join(base_path, "image.png")
    # Charger l'image d'arrière-plan
    bg_image = Image.open(image_path)  # Placez une image d'agriculture nommée 'background.jpg'
    bg_image = bg_image.resize((1000, 700), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Canvas pour l'arrière-plan
    canvas = tk.Canvas(root, width=1000, height=700)
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Frame principale
    frame_principale = tk.Frame(root, bg=BG_COLOR)
    frame_principale.place(relx=0.5, rely=0.5, anchor="center", width=850, height=610)

    # Fonction pour afficher une section
    def afficher_section(section):
        for widget in frame_principale.winfo_children():
            widget.destroy()
        section()
    
    def exporter_donnees_csv():
        """
        Exporte toutes les données des tables dans des fichiers CSV distincts.
        """
        try:
            # Demander à l'utilisateur où sauvegarder les fichiers CSV
            dossier = filedialog.askdirectory(title="Sélectionnez le dossier pour l'exportation")
            if not dossier:
                return
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # Récupérer les noms des tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                # Récupérer les données et les colonnes de chaque table
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]
                
                # Définir le chemin du fichier CSV
                fichier_csv = f"{dossier}/{table}.csv"
                
                # Écrire dans le fichier CSV
                with open(fichier_csv, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(column_names)  # En-têtes
                    writer.writerows(rows)  # Données
                
                print(f"Table {table} exportée vers {fichier_csv}")
            
            conn.close()
            messagebox.showinfo("Succès", f"Exportation terminée dans le dossier : {dossier}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

        
    def reset_and_show_section(section):
        global globalId1 
        globalId1 = ''  # Réinitialiser la variable globale
        afficher_section(section)  # Afficher la section souhaitée

    # Menu principal
    menu = tk.Menu(root)
    root.config(menu=menu)

    menu.add_command(label="Accueil", command=lambda: afficher_section(afficher_accueil))

    menu.add_command(label="Ajouter Client", command=lambda: afficher_section(ajouter_client_ui))
    menu.add_command(label="Modifier Produit Fini", command=lambda: reset_and_show_section(modifier_produit_fini_ui))

    # Sous-menu Gestion des Matières
    menu_gestion = tk.Menu(menu, tearoff=0)
    menu_gestion.add_command(label="Nouvelle Matière Première", command=lambda: afficher_section(ajouter_matiere_premiere_ui))
    menu_gestion.add_command(label="Modifier Matière Première", command=lambda: reset_and_show_section(modifier_quantite_ui))
    menu_gestion.add_command(label="Ajouter Dosage", command=lambda: afficher_section(ajouter_dosage_ui))
    menu.add_cascade(label="Gestion des Matières Première", menu=menu_gestion)

    # Sous-menu Affichage
    menu_affichage = tk.Menu(menu, tearoff=0)
    menu_affichage.add_command(label="Afficher Tableau Matières", command=lambda: afficher_section(afficher_tableau_ui))
    menu_affichage.add_command(label="Historique Bon Des Commandes", command=lambda: afficher_section(afficher_historique_ui))
    menu_affichage.add_command(label="Historique des Bons de Livraison", command=lambda: afficher_section(afficher_historique_bon_livraison_ui))
    menu.add_cascade(label="Affichage", menu=menu_affichage)

    # Commandes supplémentaires
    menu.add_command(label="Créer Bon De Commande", command=lambda: afficher_section(bon_de_commande_ui))
    menu.add_command(label="Créer Bon de Livraison", command=lambda: afficher_section(creer_bon_livraison_ui))
    menu.add_command(label="Exporter en CSV", command=exporter_donnees_csv)


    # Section : Ajouter une matière première
    def ajouter_matiere_premiere_ui():
        tk.Label(frame_principale, text="Ajouter une Matière Première", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=20)

        tk.Label(frame_principale, text="Nom :", bg=BG_COLOR, font=("Arial", 16)).pack()
        nom_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        nom_entry.pack(ipadx=10, ipady=5, pady=5)

        tk.Label(frame_principale, text="Référence :", bg=BG_COLOR, font=("Arial", 16)).pack()
        ref_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        ref_entry.pack(ipadx=10, ipady=5, pady=5)

        tk.Label(frame_principale, text="Quantité (Kg ou Litre):", bg=BG_COLOR, font=("Arial", 16)).pack()
        quantite_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        quantite_entry.pack(ipadx=10, ipady=5, pady=5)
        
        vcmd_quantite = frame_principale.register(valid)
        quantite_entry.config(validate="key", validatecommand=(vcmd_quantite, "%P"))

        tk.Label(frame_principale, text="Prix Unitaire (Dinar):", bg=BG_COLOR, font=("Arial", 16)).pack()
        prix_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        prix_entry.pack(ipadx=10, ipady=5, pady=5)

        prix_entry.config(validate="key", validatecommand=(vcmd_quantite, "%P"))

        def ajouter():
            nom = nom_entry.get()
            ref = ref_entry.get()
            quantite = quantite_entry.get()
            prix = prix_entry.get()
            if (nom!='' and ref!='' and quantite!='' and prix!=''):
                try:
                    ajouter_matiere_premiere(nom, ref, float(quantite), float(prix))
                    messagebox.showinfo("Succès", "Matière première ajoutée avec succès.")
                    nom_entry.delete(0, END)
                    ref_entry.delete(0, END)
                    quantite_entry.delete(0, END)
                except Exception as e:
                    messagebox.showerror("Erreur", str(e))
            else :
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")

        tk.Button(frame_principale, text="Ajouter", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 18, "bold"), command=ajouter).pack(pady=18, ipadx=18, ipady=8)

    # Section : Modifier la quantité d'une matière première
    def modifier_quantite_ui():
        global globalId1 
        tk.Label(frame_principale, text="Ajout De Quantité Du Matière Première", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=20)

        suggestions = get_suggestions("matieres_premieres", "nom")
        tk.Label(frame_principale, text="Nom Du Matière Première :", bg=BG_COLOR, font=("Arial", 18)).pack()
        identifiant_combobox = ttk.Combobox(frame_principale, values=suggestions, font=("Arial", 18))
        identifiant_combobox.pack(ipadx=10, ipady=5, pady=10)
        # Définir la valeur de globalId1 dans la combobox
        if globalId1:
            identifiant_combobox.set(globalId1[0])

        tk.Label(frame_principale, text="Quantité à Ajouter (Kg ou Litre) :", bg=BG_COLOR, font=("Arial", 18)).pack()
        quantite_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 18))
        quantite_entry.pack(ipadx=10, ipady=5, pady=5)
        
        vcmd_quantite = frame_principale.register(valid)
        quantite_entry.config(validate="key", validatecommand=(vcmd_quantite, "%P"))

        def modifier():
            identifiant = identifiant_combobox.get()
            quantite = quantite_entry.get()
            try:
                if (identifiant!='' and quantite!=''):
                    modifier_quantite_matiere_premiere(identifiant, float(quantite))
                    messagebox.showinfo("Succès", "Quantité modifiée avec succès.")
                    identifiant_combobox.set('')
                    quantite_entry.delete(0, END)
                    prix_entry.delete(0, END)
                    afficher_section(afficher_tableau_ui)
                else :
                    messagebox.showerror("Erreur", "Veuillez remplir les champs (Nom, Quantité).")
            except Exception as e:
                messagebox.showerror("Erreur", "Remplir les champs avec des informations correctes")

        tk.Button(frame_principale, text="Ajouter", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 14, "bold"), command=modifier).pack(pady=16, ipadx=16, ipady=6)
       
        def obtenir_prix_matiere(event):
            identifiant = identifiant_combobox.get()
            if identifiant:
                try:
                    # Connexion à la base de données pour récupérer le prix
                    conn = get_connection()  # Remplace par le chemin correct de ta base de données
                    cursor = conn.cursor()
                    cursor.execute("SELECT prix_unitaire FROM matieres_premieres WHERE nom = ?", (identifiant,))
                    result = cursor.fetchone()
                    conn.close()

                    if result:
                        prix_entry.delete(0, tk.END)
                        prix_entry.insert(0, str(result[0]))  # Met à jour le champ de prix avec la valeur trouvée
                    else:
                        prix_entry.delete(0, tk.END)  # Vider la case si l'élément n'existe pas
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la récupération du prix: {e}")

        identifiant_combobox.bind("<<ComboboxSelected>>", obtenir_prix_matiere)
        # Champ de prix
        tk.Label(frame_principale, text="Prix Unitaire (Dinar) :", bg=BG_COLOR, font=("Arial", 18)).pack()
        prix_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 18))
        prix_entry.pack(ipadx=10, ipady=5, pady=5)
        prix_entry.config(validate="key", validatecommand=(vcmd_quantite, "%P"))
        if (globalId1) :
            prix_entry.insert(0,float(globalId1[1]))
        
        def modifier_prix():
            identifiant = identifiant_combobox.get()
            nouveau_prix = prix_entry.get()
            if identifiant and nouveau_prix:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE matieres_premieres SET prix_unitaire = ? WHERE nom = ?", (float(nouveau_prix), identifiant))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Succès", "Prix mis à jour avec succès.")
                    identifiant_combobox.set('')
                    quantite_entry.delete(0, END)
                    prix_entry.delete(0, END)
                    afficher_section(afficher_tableau_ui)
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la mise à jour du prix: {e}")
            else :
                messagebox.showerror("Erreur", "Veuillez remplir les champs (Nom, Prix).")

        tk.Button(frame_principale, text="Modifier Prix", bg="#FFA500", fg="white", font=("Arial", 14, "bold"), command=modifier_prix).pack(pady=10, ipadx=16, ipady=6)

    # Section : Ajouter un dosage
    def ajouter_dosage_ui():
        tk.Label(frame_principale, text="Ajouter un Dosage", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=20)

        # Combobox pour les noms des matières produites
        matieres_produites = get_suggestions("matieres_produites", "nom")
        tk.Label(frame_principale, text="Produit Fini (Nom):", bg=BG_COLOR, font=("Arial", 16)).pack()
        matiere_produite_combobox = ttk.Combobox(frame_principale, values=matieres_produites, font=("Arial", 16))
        matiere_produite_combobox.pack(ipadx=10, ipady=5, pady=10)

        # Section pour les matières premières et quantités
        tk.Label(frame_principale, text="Matière Première (Nom)         Quantité (Kg/Litre)", bg=BG_COLOR, font=("Arial", 16)).pack()
        matieres_frame = tk.Frame(frame_principale, bg=BG_COLOR)
        matieres_frame.pack(pady=10)

        matieres_premieres = get_suggestions("matieres_premieres", "nom")

        def ajouter_matiere_premiere():
            frame = tk.Frame(matieres_frame, bg=BG_COLOR)
            frame.pack(fill="x", pady=5)

            matiere_premiere_combobox = ttk.Combobox(frame, values=matieres_premieres, font=("Arial", 14), width=30)
            matiere_premiere_combobox.pack(side="left", padx=5)

            quantite_entry = tk.Entry(frame, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 14), width=10)
            quantite_entry.pack(side="left", padx=5)
            def valid(P):
                try:
                    if P == "":
                        return True
                    float(P)
                    return True
                except ValueError:
                    return False
            
            vcmd_quantite = frame_principale.register(valid)
            quantite_entry.config(validate="key", validatecommand=(vcmd_quantite, "%P"))

            remove_button = tk.Button(frame, text="X", font=("Arial", 12, "bold"), bg="red", fg="white",
                                    command=lambda: frame.destroy())
            remove_button.pack(side="left", padx=5)

        # Bouton pour ajouter une matière première
        tk.Button(frame_principale, text="Ajouter une Matière Première", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, 
                font=("Arial", 16), command=ajouter_matiere_premiere).pack(pady=10)

        # Ajouter une matière première initiale
        ajouter_matiere_premiere()

        def ajouter():
            matiere_produite = matiere_produite_combobox.get()
            dosages = []
            for child in matieres_frame.winfo_children():
                widgets = child.winfo_children()
                matiere_premiere = widgets[0].get()  # Combobox
                quantite = widgets[1].get()  # Entry
                if matiere_premiere and quantite:
                    dosages.append((matiere_premiere, float(quantite)))

            if not matiere_produite or not dosages:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
                return

            try:
                ajouter_dosage(matiere_produite, dosages)
                messagebox.showinfo("Succès", "Dosage ajouté avec succès.")
                matiere_produite_combobox.set('')
                for child in matieres_frame.winfo_children():
                    child.destroy()
                ajouter_matiere_premiere()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        tk.Button(frame_principale, text="Ajouter Dosage", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, 
                font=("Arial", 16, "bold"), command=ajouter).pack(pady=18, ipadx=18, ipady=8)

    # Section : Ajouter client
    def ajouter_client_ui():
        tk.Label(frame_principale, text="Ajouter un Client", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=20)
        
        tk.Label(frame_principale, text="Nom :", bg=BG_COLOR, font=("Arial", 16)).pack()
        nom_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        nom_entry.pack(ipadx=10, ipady=5, pady=5)
        
        tk.Label(frame_principale, text="Adresse :", bg=BG_COLOR, font=("Arial", 16)).pack()
        adresse_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        adresse_entry.pack(ipadx=10, ipady=5, pady=5)
        
        tk.Label(frame_principale, text="Téléphone :", bg=BG_COLOR, font=("Arial", 16)).pack()
        phone_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        phone_entry.pack(ipadx=10, ipady=5, pady=5)
        
        def validate_phone(P):
            return P.isdigit() or P == ""
        
        vcmd = frame_principale.register(validate_phone)
        phone_entry.config(validate="key", validatecommand=(vcmd, "%P"))
        
        tk.Label(frame_principale, text="MF :", bg=BG_COLOR, font=("Arial", 16)).pack()
        reference_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        reference_entry.pack(ipadx=10, ipady=5, pady=5)
        
        def ajouter():
            nom = nom_entry.get()
            adresse = adresse_entry.get()
            phone = phone_entry.get()
            reference = reference_entry.get()

            if not nom or not adresse or not phone or not reference:
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
                return
            
            try:
                ajouter_client(nom, adresse, phone, reference)
                messagebox.showinfo("Succès", "Client ajouté avec succès.")
                nom_entry.delete(0, tk.END)
                adresse_entry.delete(0, tk.END)
                phone_entry.delete(0, tk.END)
                reference_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
        
        tk.Button(frame_principale, text="Ajouter", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 16, "bold"), command=ajouter).pack(pady=18, ipadx=18, ipady=8)

    # Section : Modifier les valeurs de Produit fini
    def modifier_produit_fini_ui():
        global globalId1
        tk.Label(frame_principale, text="Ajout ou Modification Du Produit fini", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=20)

        suggestions = get_suggestions("matieres_produites", "nom")
        tk.Label(frame_principale, text="Nom Du Produit fini :", bg=BG_COLOR, font=("Arial", 16)).pack()
        identifiant_combobox = ttk.Combobox(frame_principale, values=suggestions, font=("Arial", 16))
        identifiant_combobox.pack(ipadx=10, ipady=5, pady=10)
        # Définir la valeur de globalId1 dans la combobox
        if globalId1:
            identifiant_combobox.set(globalId1[0])

        tk.Label(frame_principale, text="Quantité à Ajouter (Kg ou Litre) :", bg=BG_COLOR, font=("Arial", 16)).pack()
        quantite_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        quantite_entry.pack(ipadx=10, ipady=5, pady=5)
        quantite_entry.insert(0,0)
        
        vcmd_quantite = frame_principale.register(valid)
        quantite_entry.config(validate="key", validatecommand=(vcmd_quantite, "%P"))

        def obtenir_details_produit(event):
            nom_produit = identifiant_combobox.get()
            if nom_produit:
                try:
                    # Exécuter une requête SQL pour obtenir le prix et le FODEC du produit
                    conn = get_connection()  
                    cursor = conn.cursor()
                    cursor.execute("SELECT prix_unitaire, fodec FROM matieres_produites WHERE nom = ?", (nom_produit,))
                    result = cursor.fetchone()
                    conn.close()

                    if result:
                        # Mettre à jour le champ de prix avec la valeur trouvée
                        prix_entry.delete(0, tk.END)
                        prix_entry.insert(0, str(result[0]))

                        # Mettre à jour le champ FODEC en fonction de la valeur récupérée
                        if result[1] == '1':
                            fodec.set("1")  # Oui
                        else:
                            fodec.set("-1")  # Non
                    else:
                        prix_entry.delete(0, tk.END)  # Vider la case si aucun produit trouvé
                        fodec.set("0")  # Réinitialiser le FODEC
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la récupération des informations: {e}")

        # Lier la fonction à l'événement de sélection de l'élément dans la combobox
        identifiant_combobox.bind("<<ComboboxSelected>>", obtenir_details_produit)

        # Champ de prix
        tk.Label(frame_principale, text="Prix Unitaire (Dinar) :", bg=BG_COLOR, font=("Arial", 16)).pack()
        prix_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        prix_entry.pack(ipadx=10, ipady=5, pady=5)
        prix_entry.config(validate="key", validatecommand=(vcmd_quantite, "%P"))
        if (globalId1) :
            prix_entry.insert(0,float(globalId1[1]))

        # Champ de fodec
        tk.Label(frame_principale, text="FODEC :", bg=BG_COLOR, font=("Arial", 16)).pack(pady=10)
        fodec = tk.StringVar(value='0')  # Initialiser avec une chaîne vide
        if (globalId1) :
            # prix_entry.insert(0,float(globalId1[1]))
            if globalId1[2] == '1':
                fodec.set("1")  # Oui
            else:
                fodec.set("-1")  # Non
        def update_fodec(value):
            fodec.set("1" if value == "oui" else "-1")

        fodec_frame = tk.Frame(frame_principale, bg=BG_COLOR)
        fodec_frame.pack()

        fodec_oui = tk.Radiobutton(
            fodec_frame, text="Oui", variable=fodec, value="1", bg=BG_COLOR, font=("Arial", 14),
            command=lambda: update_fodec("oui")
        )
        fodec_oui.pack(side=tk.LEFT, padx=5)

        fodec_non = tk.Radiobutton(
            fodec_frame, text="Non", variable=fodec, value="-1", bg=BG_COLOR, font=("Arial", 14),
            command=lambda: update_fodec("non")
        )
        fodec_non.pack(side=tk.RIGHT, padx=5)

        def modifier():
            identifiant = identifiant_combobox.get()
            quantite = quantite_entry.get()
            prix = prix_entry.get()
            fodec_value = fodec.get()
            if (identifiant!='' and quantite!='' and prix!='' and fodec_value != '0'):
                try:
                        mettre_aJour_produit_fini(identifiant, float(quantite), prix, fodec_value)
                        messagebox.showinfo("Succès", "Modification faite avec succès.")
                        identifiant_combobox.set('')
                        quantite_entry.delete(0, END)
                        prix_entry.delete(0, END)
                        fodec.set("0")
                except Exception as e:
                    messagebox.showerror("Erreur", "Remplir les champs avec des informations correctes \n {e}")
            else :
                messagebox.showerror("Erreur", "Veuillez remplir les champs (Nom, Quantité).")

        tk.Button(frame_principale, text="Ajouter les Modifications", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 14, "bold"), command=modifier).pack(pady=16, ipadx=16, ipady=6)
       

    # Section : Créer une matière produite
    def bon_de_commande_ui():
        global globalId1 
        globalId1='0'
        tk.Label(frame_principale, text="Crée Bon De Commande", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=20)

        matieres_produites = get_suggestions("matieres_produites", "nom")
        # Entrées pour ajouter un article

        tk.Label(frame_principale, text="Nom de Produit Fini :", bg=BG_COLOR, font=("Arial", 18)).pack()
        matiere_produite_combobox = ttk.Combobox(frame_principale, values=matieres_produites, font=("Arial", 16))
        matiere_produite_combobox.pack(ipadx=10, ipady=5, pady=5)

        def obtenir_details_produit(event):
            global globalId1
            nom_produit = matiere_produite_combobox.get()
            if nom_produit:
                try:
                    # Exécuter une requête SQL pour obtenir le prix et le FODEC du produit
                    conn = get_connection()  
                    cursor = conn.cursor()
                    cursor.execute("SELECT prix_unitaire, fodec FROM matieres_produites WHERE nom = ?", (nom_produit,))
                    result = cursor.fetchone()
                    conn.close()

                    if result:
                        # Mettre à jour le champ de prix avec la valeur trouvée
                        prix_entry.delete(0, tk.END)
                        prix_entry.insert(0, str(result[0]))

                        # Mettre à jour le champ FODEC en fonction de la valeur récupérée
                        if result[1] == '1':
                            fodec.set("1")  # Oui
                        else:
                            fodec.set("-1")  # Non
                    else:
                        prix_entry.delete(0, tk.END)  # Vider la case si aucun produit trouvé
                        fodec.set("0")  # Réinitialiser le FODEC
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la récupération des informations: {e}")

        # Lier la fonction à l'événement de sélection de l'élément dans la combobox
        matiere_produite_combobox.bind("<<ComboboxSelected>>", obtenir_details_produit)


        tk.Label(frame_principale, text="Quantité (Kg ou Litre):", bg=BG_COLOR, font=("Arial", 18)).pack()
        qte_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        qte_entry.pack(ipadx=10, ipady=5, pady=5)
        
        vcmd_quantite = frame_principale.register(valid)
        qte_entry.config(validate="key", validatecommand=(vcmd_quantite, "%P"))

        tk.Label(frame_principale, text="Prix Unitaire (Dinar):", bg=BG_COLOR, font=("Arial", 16)).pack()
        prix_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        prix_entry.pack(ipadx=10, ipady=5, pady=5)
        prix_entry.config(validate="key", validatecommand=(vcmd_quantite, "%P"))

        tk.Label(frame_principale, text="FODEC :", bg=BG_COLOR, font=("Arial", 16)).pack(pady=10)
        fodec = tk.StringVar(value='0')  # Initialiser avec une chaîne vide
        def update_fodec(value):
            fodec.set("1" if value == "oui" else "-1")

        fodec_frame = tk.Frame(frame_principale, bg=BG_COLOR)
        fodec_frame.pack()

        fodec_oui = tk.Radiobutton(
            fodec_frame, text="Oui", variable=fodec, value="1", bg=BG_COLOR, font=("Arial", 14),
            command=lambda: update_fodec("oui")
        )
        fodec_oui.pack(side=tk.LEFT, padx=5)

        fodec_non = tk.Radiobutton(
            fodec_frame, text="Non", variable=fodec, value="-1", bg=BG_COLOR, font=("Arial", 14),
            command=lambda: update_fodec("non")
        )
        fodec_non.pack(side=tk.RIGHT, padx=5)

        def creer():
            nom = matiere_produite_combobox.get()
            qte = qte_entry.get()
            prix = prix_entry.get()
            fodec_value = fodec.get()
            if (nom!='' and qte!='' and prix!='' and fodec_value != '0'):
                try:
                    creer_bon_de_commande(nom, float(qte), float(prix), fodec_value)
                    messagebox.showinfo("Succès", "Bon De Commande crée avec succès.")
                    matiere_produite_combobox.set('')
                    qte_entry.delete(0, END)
                    prix_entry.delete(0, END)
                    fodec.set("0")
                except Exception as e:
                    messagebox.showerror("Erreur", str(e))
            else :
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
        tk.Button(frame_principale, text="Créer", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 16, "bold"), command=creer).pack(pady=18, ipadx=18, ipady=8)

    # Section : Créer un bon de livraison
    def creer_bon_livraison_ui():
        style = ttk.Style()
        style.configure("Treeview", rowheight=20)

        tk.Label(frame_principale, text="Créer Bon de Livraison", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=10)
        
        # Liste des matières produites disponibles
        matieres_produites = get_suggestions("matieres_produites", "nom")
        clients = get_suggestions("clients", "nom")

        # Frame pour contenir la table et la scrollbar
        table_frame = tk.Frame(frame_principale)
        table_frame.pack(pady=10, padx=20)

        # Ajout de la barre de défilement verticale
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # Table pour ajouter les articles avec la scrollbar associée
        columns = ("Produit Fini", "Quantité")
        treeview = ttk.Treeview(table_frame, columns=columns, show="headings", height=4, yscrollcommand=scrollbar.set)

        for col in columns:
            treeview.heading(col, text=col, anchor="center")
            treeview.column(col, anchor="center", width=150)

        treeview.pack(side="left", fill="both", expand=True)

        # Associer la scrollbar à la treeview
        scrollbar.config(command=treeview.yview)

        # Entrées pour ajouter un article
        tk.Label(frame_principale, text="Produit Fini :", bg=BG_COLOR, font=("Arial", 14)).pack()
        matiere_produite_combobox = ttk.Combobox(frame_principale, values=matieres_produites, font=("Arial", 16))
        matiere_produite_combobox.pack(ipadx=10, ipady=5, pady=5)

        tk.Label(frame_principale, text="Quantité (Kg ou Litre):", bg=BG_COLOR, font=("Arial", 14)).pack()
        quantite_entry = tk.Entry(frame_principale, font=("Arial", 14))
        quantite_entry.pack(ipadx=10, ipady=5, pady=5)
        
        vcmd_quantite = frame_principale.register(valid)
        quantite_entry.config(validate="key", validatecommand=(vcmd_quantite, "%P"))

        def ajouter_article():
            matiere_produite = matiere_produite_combobox.get()
            quantite = quantite_entry.get()
            if matiere_produite and quantite:
                treeview.insert("", "end", values=(matiere_produite, quantite))
                matiere_produite_combobox.set("")
                quantite_entry.delete(0, tk.END)

        tk.Button(frame_principale, text="Ajouter Article", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 14), command=ajouter_article).pack(pady=10)

        tk.Label(frame_principale, text="Client :", bg=BG_COLOR, font=("Arial", 16)).pack()
        client_entry = ttk.Combobox(frame_principale, values=clients, font=("Arial", 16))
        client_entry.pack(ipadx=10, ipady=5, pady=5)

        # Cases à cocher pour BL et Facture
        bl = tk.StringVar(value='0')  # Initialiser avec une chaîne vide
        def update_bl(value):
            bl.set("1" if value == "oui" else "-1")

        bl_frame = tk.Frame(frame_principale, bg=BG_COLOR)
        bl_frame.pack()
        bl_label = tk.Label(bl_frame, text="Demande BL :", bg=BG_COLOR, font=("Arial", 14))
        bl_label.pack(side=tk.LEFT, padx=10)

        bl_oui = tk.Radiobutton(
            bl_frame, text="Oui", variable=bl, value="1", bg=BG_COLOR, font=("Arial", 14),
            command=lambda: update_bl("oui")
        )
        bl_oui.pack(side=tk.LEFT, padx=5)

        bl_non = tk.Radiobutton(
            bl_frame, text="Non", variable=bl, value="-1", bg=BG_COLOR, font=("Arial", 14),
            command=lambda: update_bl("non")
        )
        bl_non.pack(side=tk.RIGHT, padx=5)

        # Bouton pour créer le bon de livraison
        def creer_bon():
            articles = [
                {"matiere_produite_nom": treeview.item(item)["values"][0], "quantite": float(treeview.item(item)["values"][1])}
                for item in treeview.get_children()
            ]
            if not articles:
                messagebox.showinfo("Entrée manquante","Ajouter Des Article")
                return
            client = client_entry.get()
            if not client :
                messagebox.showinfo("Entrée manquante","Entrer Le Champs Client")
                return
            bl_value = bl.get()
            if bl_value == "0" :
                messagebox.showinfo("Entrée manquante","Choisir si vous souhaitez avoir une BL ou NON!")
                return
            client_info = get_client_data('clients', client)
            try:
                message = creer_bon_livraison(articles, client, client_info, bl_value)
                messagebox.showinfo("Succès", message)
                treeview.delete(*treeview.get_children())
                client_entry.delete(0, END)
                bl.set("0")

            except Exception as e:
                messagebox.showerror("Erreur", str(e))
        
        tk.Button(frame_principale, text="Créer Bon de Livraison", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 16, "bold"), command=creer_bon).pack(pady=15, ipadx=10, ipady=5)

    # Section : Afficher un tableau pour les matières premières et produites
    def afficher_tableau_ui():
        style = ttk.Style()
        style.configure("Treeview", rowheight=20)  

        # Titre pour les matières premières
        tk.Label(frame_principale, text="Tableau des Matières Premières", font=("Arial", 18, "bold"), bg=BG_COLOR).pack(pady=10)

        # Frame pour encapsuler le tableau et les boutons
        frame_mp = tk.Frame(frame_principale)
        frame_mp.pack(pady=8, padx=18, fill="both", expand=True)

        # Scrollbar verticale pour les matières premières
        scrollbar_mp = tk.Scrollbar(frame_mp)
        scrollbar_mp.pack(side="right", fill="y")

        # Tableau des matières premières
        columns_1 = ("ID", "Nom", "Référence", "Quantité", "prix_unitaire")
        treeview_1 = ttk.Treeview(frame_mp, columns=columns_1, show="headings", height=7, yscrollcommand=scrollbar_mp.set)
        treeview_1.pack(side="left", fill="both", expand=True)

        scrollbar_mp.config(command=treeview_1.yview)

        # Définir les en-têtes et colonnes
        column_widths = [100, 160, 160, 100, 100]
        for col, width in zip(columns_1, column_widths):
            treeview_1.heading(col, text=col, anchor="center")
            treeview_1.column(col, anchor="center", width=width)

        # Remplir le tableau
        for row in get_table_data("matieres_premieres"):
            treeview_1.insert("", "end", values=row)

        # Boutons Modifier et Supprimer pour matières premières
        def supprimer_matiere():
            selected_item = treeview_1.selection()
            if not selected_item:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner une ligne à supprimer.")
                return
            item_values = treeview_1.item(selected_item, 'values')
            id_to_delete = item_values[0]

            # Suppression dans la base de données
            response = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cet élément ?")
            if response:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM matieres_premieres WHERE id = ?", (id_to_delete,))
                    conn.commit()
                    conn.close()
                    treeview_1.delete(selected_item)
                    messagebox.showinfo("Succès", "Matière première supprimée avec succès.")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")

        def modifier_matiere():
            global globalId1
            selected_item = treeview_1.selection()
            if not selected_item:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner une ligne à modifier.")
                return
            item_values = treeview_1.item(selected_item, 'values')
            id_to_edit = item_values[0]
            globalId1 = majGlobale(id_to_edit,0)
            afficher_section(modifier_quantite_ui)

        frame_btn_mp = tk.Frame(frame_principale, bg=BG_COLOR)
        frame_btn_mp.pack(pady=10)

        tk.Button(frame_btn_mp, text="Modifier", bg="orange", fg="white", font=("Arial", 14, "bold"), command=modifier_matiere).pack(side="left", padx=10, ipadx=10)
        tk.Button(frame_btn_mp, text="Supprimer", bg="red", fg="white", font=("Arial", 14, "bold"), command=supprimer_matiere).pack(side="right", padx=10, ipadx=10)

        # Titre pour les matières produites
        tk.Label(frame_principale, text="Tableau des Produits Finis", font=("Arial", 18, "bold"), bg=BG_COLOR).pack(pady=10)

        # Frame pour le tableau des produits finis
        frame_pf = tk.Frame(frame_principale)
        frame_pf.pack(pady=8, padx=18, fill="both", expand=True)

        # Scrollbar verticale pour les produits finis
        scrollbar_pf = tk.Scrollbar(frame_pf)
        scrollbar_pf.pack(side="right", fill="y")

        # Tableau des matières produites
        columns_2 = ("ID", "Nom", "Référence", "Quantité", "Prix Unité", "Fodec")
        treeview_2 = ttk.Treeview(frame_pf, columns=columns_2, show="headings", height=7, yscrollcommand=scrollbar_pf.set)
        treeview_2.pack(side="left", fill="both", expand=True)

        scrollbar_pf.config(command=treeview_2.yview)

        # Définir les en-têtes et colonnes
        column_widths = [100, 150, 180, 180, 100, 100]
        for col, width in zip(columns_2, column_widths):
            treeview_2.heading(col, text=col, anchor="center")
            treeview_2.column(col, anchor="center", width=width)

        # Remplir le tableau
        for row in get_table_data("matieres_produites"):
            treeview_2.insert("", "end", values=row)

        # Boutons Modifier et Supprimer pour produits finis
        def supprimer_produit():
            selected_item = treeview_2.selection()
            if not selected_item:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner une ligne à supprimer.")
                return
            item_values = treeview_2.item(selected_item, 'values')
            id_to_delete = item_values[0]
            response = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cet élément ?")
            if response:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM matieres_produites WHERE id = ?", (id_to_delete,))
                    conn.commit()
                    conn.close()
                    treeview_2.delete(selected_item)
                    messagebox.showinfo("Succès", "Produit supprimé avec succès.")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")

        def modifier_produit():
            global globalId1
            selected_item = treeview_2.selection()
            if not selected_item:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner une ligne à modifier.")
                return
            item_values = treeview_2.item(selected_item, 'values')
            id_to_edit = item_values[0]
            globalId1 = majGlobale(id_to_edit,1)
            print(id_to_edit,globalId1,' aa')
            afficher_section(modifier_produit_fini_ui)

        frame_btn_pf = tk.Frame(frame_principale, bg=BG_COLOR)
        frame_btn_pf.pack(pady=10)

        tk.Button(frame_btn_pf, text="Modifier", bg="orange", fg="white", font=("Arial", 14, "bold"), command=modifier_produit).pack(side="left", padx=10, ipadx=10)
        tk.Button(frame_btn_pf, text="Supprimer", bg="red", fg="white", font=("Arial", 14, "bold"), command=supprimer_produit).pack(side="right", padx=10, ipadx=10)

        # Bouton Retour
        def retour():
            afficher_section(afficher_accueil)

        tk.Button(frame_principale, text="Retour", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 14, "bold"), command=retour).pack(pady=16, ipadx=15, ipady=5)


    # Section : Afficher un tableau pour l'historique des bon de commande
    def afficher_historique_ui():
        style = ttk.Style()
        style.configure("Treeview", rowheight=20)  # Définit une hauteur de ligne de 20 pixels

        # Titre
        tk.Label(frame_principale, text="Historique des Bon De Commande", font=("Arial", 20, "bold"), bg=BG_COLOR).pack(pady=18)
        
        # Récupérer l'historique depuis la base de données
        historique = get_historique_matiere_produite()

        # Création d'un cadre pour contenir le tableau et la scrollbar
        frame_table = tk.Frame(frame_principale)
        frame_table.pack(pady=10, padx=20, fill="both", expand=True)

        # Scrollbar verticale
        scrollbar = tk.Scrollbar(frame_table)
        scrollbar.pack(side="right", fill="y")

        # Tableau pour afficher l'historique
        columns = ("ID", "Nom", "Quantité", "Date de Création", "Prix_Unitaire")
        treeview = ttk.Treeview(frame_table, columns=columns, show="headings", height=12, yscrollcommand=scrollbar.set)
        treeview.pack(side="left", fill="both", expand=True)

        # Associer la scrollbar au Treeview
        scrollbar.config(command=treeview.yview)

        # Définir les en-têtes de colonnes
        column_widths = [100, 160, 100, 180, 100]  # Largeurs spécifiques pour chaque colonne
        for col, width in zip(columns, column_widths):
            treeview.heading(col, text=col, anchor="center")
            treeview.column(col, anchor="center", width=width)

         # Configurer des couleurs pour les lignes
        style = ttk.Style()
        style.configure("Treeview", background="lightgray", fieldbackground="lightblue", foreground="black")

        # Remplir le tableau avec l'historique des matières produites
        for row in historique:
            treeview.insert("", "end", values=row)

        # Ajouter un bouton pour revenir à l'interface principale
        def retour():
            afficher_section(afficher_accueil)

        tk.Button(frame_principale, text="Retour", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 14, "bold"), command=retour).pack(pady=16, ipadx=16, ipady=8)


    def afficher_historique_bon_livraison_ui():
        style = ttk.Style()
        style.configure("Treeview", rowheight=50)  # Définit une hauteur de ligne de 45 pixels

        # Titre
        tk.Label(frame_principale, text="Historique des Bons de Livraison", font=("Arial", 20, "bold"), bg=BG_COLOR).pack(pady=18)

        # Récupérer l'historique depuis la base de données
        historique = get_historique_bon_livraison()

        # Cadre pour contenir le tableau et la scrollbar
        frame_table = tk.Frame(frame_principale)
        frame_table.pack(pady=10, padx=20, fill="both", expand=True)

        # Scrollbar verticale
        scrollbar = tk.Scrollbar(frame_table)
        scrollbar.pack(side="right", fill="y")

        # Tableau pour afficher l'historique
        columns = ("ID Bon", "Produits Finis", "Prix Total", "Client", "Date de Création")
        treeview = ttk.Treeview(frame_table, columns=columns, show="headings", height=8, yscrollcommand=scrollbar.set)
        treeview.pack(side="left", fill="both", expand=True)

        # Associer la scrollbar au Treeview
        scrollbar.config(command=treeview.yview)

        # Définir les en-têtes de colonnes
        column_widths = [100, 250, 120, 120, 160]  # Largeurs spécifiques pour chaque colonne
        for col, width in zip(columns, column_widths):
            treeview.heading(col, text=col, anchor="center")
            treeview.column(col, anchor="center", width=width)

         # Configurer des couleurs pour les lignes
        style = ttk.Style()
        style.configure("Treeview", background="lightgray", fieldbackground="lightblue", foreground="black")

        # Remplir le tableau avec l'historique des bons de livraison
        for row in historique:
            bon_id, articles_json, total, client, date_creation = row

            # Convertir les articles JSON en texte lisible
            articles = json.loads(articles_json)
            articles_str = "\n".join([
                f"{article['nom']} (Quantité: {article['quantite']}, Total: {article['total']:.2f})"
                for article in articles
            ])

            treeview.insert("", "end", values=(bon_id, articles_str, f"{total:.2f}", client, date_creation))
        
        # Ajouter un bouton pour revenir à l'interface principale
        def retour():
            afficher_section(afficher_accueil)

        tk.Button(frame_principale, text="Retour", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 14, "bold"), command=retour).pack(pady=16, ipadx=16, ipady=6)
    
    def afficher_accueil():
        # Effacer le contenu précédent
        for widget in frame_principale.winfo_children():
            widget.destroy()

        # Couleurs
        BTN_COLOR = "#2a4684" #4CAF50"  # Vert doux
        BTN_HOVER = "#4c63b4" #45a049"  # Vert plus foncé
        TEXT_COLOR = "white"

        # Appliquer un fond général
        frame_principale.configure(bg=BG_COLOR)

        # Conteneur central
        container = tk.Frame(frame_principale, bg=BG_COLOR, bd=5, relief="ridge")
        container.pack(pady=40, padx=20, ipadx=20, ipady=20)

        # Titre principal
        tk.Label(container, text="🌟 Gestion de Stock 🌟", font=("Arial", 26, "bold"), bg=BG_COLOR, fg="#333").grid(row=0, column=0, columnspan=2, pady=8)

        # Fonction pour changer la couleur au survol
        def on_enter(e, btn):
            btn.config(bg=BTN_HOVER)

        def on_leave(e, btn):
            btn.config(bg=BTN_COLOR)

        # Fonction pour créer un bouton stylisé
        def creer_bouton(text, command, row, col):
            btn = tk.Button(
                container, text=text, bg=BTN_COLOR, fg=TEXT_COLOR, font=("Arial", 14, "bold"),
                relief="raised", bd=3, width=30, height=2, command=command, cursor="hand2"
            )
            btn.grid(row=row, column=col, padx=10, pady=5, ipadx=10, ipady=2, sticky="nsew")
            btn.bind("<Enter>", lambda e: on_enter(e, btn))
            btn.bind("<Leave>", lambda e: on_leave(e, btn))
            return btn

        # Ajouter les boutons en deux colonnes🚚
        creer_bouton("➕ Ajouter un Client", lambda: afficher_section(ajouter_client_ui), row=1, col=0)
        creer_bouton("➕ Nouvelle Matière Première", lambda: afficher_section(ajouter_matiere_premiere_ui), row=2, col=0)
        creer_bouton("➕ Ajouter un dosage", lambda: afficher_section(ajouter_dosage_ui), row=3, col=0)
        creer_bouton("📝 Créer bon de commande", lambda: afficher_section(bon_de_commande_ui), row=4, col=0)
        creer_bouton("📝 Créer bon de livraison", lambda: afficher_section(creer_bon_livraison_ui), row=5, col=0)
        creer_bouton("📊 Tableau des Produits", lambda: afficher_section(afficher_tableau_ui), row=1, col=1)
        creer_bouton("🖊️ Modifier Matiere Premiére", lambda: reset_and_show_section(modifier_quantite_ui), row=2, col=1)
        creer_bouton("🖊️ Modifier Produit Fini", lambda: reset_and_show_section(modifier_produit_fini_ui), row=3, col=1)
        creer_bouton("📜 Historique des Bons de Commande", lambda: afficher_section(afficher_historique_ui), row=4, col=1)
        creer_bouton("📜 Historique des Bons de Livraison", lambda: afficher_section(afficher_historique_bon_livraison_ui), row=5, col=1)

        # Bouton quitter (centré sur deux colonnes)
        quitter_btn = tk.Button(
            container, text="❌ Quitter", bg="#D81313", fg="white", font=("Arial", 15, "bold"),
            relief="raised", bd=3, width=20, height=1, command=root.quit, cursor="hand2"
        )
        quitter_btn.grid(row=6, column=0, columnspan=2, pady=16, ipadx=10, ipady=3)
        quitter_btn.bind("<Enter>", lambda e: quitter_btn.config(bg="#b22222"))
        quitter_btn.bind("<Leave>", lambda e: quitter_btn.config(bg="#D81313"))

        # Ajuster les colonnes pour qu'elles aient la même largeur
        container.grid_columnconfigure(1, weight=1)
        container.grid_columnconfigure(1, weight=1)


    # Lancer l'application avec une section par défaut
    afficher_section(afficher_accueil)
    root.mainloop()
