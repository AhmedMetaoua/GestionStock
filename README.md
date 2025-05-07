# Gestion de Stock - Stock Management Application

A comprehensive stock management system built with Python and Tkinter, designed to help businesses manage their inventory, track products, and handle orders efficiently.

## 🌟 Features

### Inventory Management
- Track raw materials and finished products
- Monitor stock levels in real-time
- Manage product quantities and prices
- Support for different units (Kg/Litre)

### Order Management
- Create and manage purchase orders
- Generate delivery notes (Bons de Livraison)
- Track order history
- Support for FODEC (Tax) management

### Customer Management
- Maintain customer database
- Store customer details (name, address, phone, reference)
- Quick access to customer information

### Product Management
- Add and modify raw materials
- Create finished products with specific formulations
- Track product pricing and specifications
- Manage product dosages and recipes

## 🚀 Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd GestionStock
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## 📋 Requirements

- Python 3.x
- Tkinter (usually comes with Python)
- PIL (Python Imaging Library)
- SQLite3 (included in Python standard library)

## 💻 Usage

### Main Interface
The application provides an intuitive interface with the following main sections:

1. **Home Screen**
   - Quick access to all main functions
   - Modern and user-friendly design

2. **Inventory Management**
   - Add new raw materials
   - Modify existing products
   - View current stock levels

3. **Order Processing**
   - Create purchase orders
   - Generate delivery notes
   - View order history

4. **Customer Management**
   - Add new customers
   - View customer details
   - Manage customer information

### Key Functions

1. **Adding Raw Materials**
   - Enter material name, reference, quantity, and unit price
   - System automatically tracks inventory levels

2. **Managing Finished Products**
   - Create new products with specific formulations
   - Set pricing and tax (FODEC) information
   - Track product inventory

3. **Creating Orders**
   - Select products and quantities
   - Generate delivery notes
   - Track order history

4. **Customer Management**
   - Add new customers with complete details
   - Quick access to customer information
   - Link customers to orders

## 🔧 Database Structure

The application uses SQLite database with the following main tables:
- `matieres_premieres`: Raw materials inventory
- `matieres_produites`: Finished products inventory
- `clients`: Customer information
- `historique_bon_livraison`: Delivery note history
- `historique_matiere_produite`: Production history

## 📊 Data Export

The application supports data export functionality:
- Export all data to CSV format
- Maintain data backup
- Generate reports

## 🔐 Security

- Input validation for all entries
- Data integrity checks
- Secure database operations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For support, please open an issue in the repository or contact the development team.

## 🔄 Updates

Regular updates are provided to improve functionality and fix bugs. Check the repository for the latest version.





python -m PyInstaller --onefile --windowed --add-data "image.png;." --add-data "FACTURE-Copy.xlsx;." --icon="icon.ico" main.py