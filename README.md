# Truck DMS - Document Management System

A comprehensive document management system for trucking companies, supporting multiple document types with advanced filtering and export capabilities.

## 🚀 Quick Start

### Method 1: Using the Batch File (Recommended)

1. **Download/Clone** the project to your desired location
2. **Double-click** `start_dms.bat` to run the application
3. The application will:
   - Check for Python installation
   - Create virtual environment if needed
   - Install required packages
   - Start the server automatically
   - Open your browser to `http://localhost:5000`

### Method 2: Manual Setup

1. **Install Python 3.8+** from [python.org](https://www.python.org/)
2. **Open Command Prompt** in the project directory
3. **Run these commands:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install flask pandas openpyxl xlrd xlsxwriter
   python app.py
   ```
4. **Open your browser** and go to `http://localhost:5000`

## 📁 Project Structure

```
dms-system/
├── start_dms.bat          # Main launcher script
├── setup_shortcut.bat     # Create desktop/taskbar shortcut
├── app.py                 # Flask application
├── migrate_csv.py         # Data migration script
├── config/
│   └── config.py          # Configuration settings
├── static/
│   ├── css/
│   │   └── styles.css     # Styling
│   └── js/
│       └── app.js         # Frontend JavaScript
├── templates/
│   └── index.html         # Main HTML template
├── uploads/               # Document uploads
├── data/
│   └── documents.csv      # Document database
└── README.md              # This file
```

## 🎯 Features

### Document Management
- **Multiple Document Types**: RC, BOL, POD, Dispatcher, Fuel, Invoice, RLP
- **File Upload**: Support for PDF, Excel, Word, images, and more
- **Smart Filtering**: Filter by document type, file type, and search terms
- **Document Editing**: Edit document details and custom fields

### Export Capabilities
- **PDF Export**: Generate professional PDF reports with document tables
- **Excel Export**: Create multi-sheet Excel workbooks with summary data
- **Filtered Export**: Export only the documents you've filtered

### User Interface
- **Modern Design**: Clean, responsive interface with Tailwind CSS
- **Navigation Dropdowns**: Quick access to filters and export options
- **Real-time Updates**: Live document count and total amounts
- **Mobile Friendly**: Works on tablets and mobile devices

## 🔧 Setup Taskbar Shortcut

### Automatic Setup
1. **Run** `setup_shortcut.bat` (as Administrator if needed)
2. **Follow the prompts** to create a desktop shortcut
3. **Right-click** the desktop shortcut and select "Pin to taskbar"

### Manual Setup
1. **Right-click** on `start_dms.bat`
2. **Select "Send to" → "Desktop (create shortcut)"**
3. **Right-click** the desktop shortcut and "Pin to taskbar"

## 📋 Supported Document Types

| Type | Description | Key Fields |
|------|-------------|------------|
| **RC** | Rate Confirmation | Load Number, Dispatcher, Pickup/Dropoff, Miles, Rate |
| **BOL** | Bill of Lading | BOL Number, RC Number, Load Details |
| **POD** | Proof of Delivery | RC Number, Load Number, Delivery Details |
| **Dispatcher** | Dispatcher Info | Company, Contact, Commission Details |
| **Fuel** | Fuel Receipts | Receipt Number, Amount, RC Reference |
| **Invoice** | Invoicing | Invoice Number, Amount Received, Quick Pay |
| **RLP** | Rate Lock Protection | RLP Number, Amount Received, Dates |

## 🛠️ Technical Requirements

- **Python 3.8+**
- **Modern Web Browser** (Chrome, Firefox, Edge, Safari)
- **Windows OS** (batch files optimized for Windows)
- **2GB+ RAM** recommended
- **100MB+ Disk Space**

## 📦 Dependencies

The application automatically installs these packages:
- `flask` - Web framework
- `pandas` - Data manipulation
- `openpyxl` - Excel file handling
- `xlrd` - Excel reading
- `xlsxwriter` - Excel writing

## 🔍 Troubleshooting

### Common Issues

**"Python is not installed"**
- Download Python from [python.org](https://www.python.org/)
- Make sure to check "Add Python to PATH" during installation

**"Virtual environment creation failed"**
- Run Command Prompt as Administrator
- Ensure you have write permissions in the project folder

**"Server won't start"**
- Check if port 5000 is already in use
- Try running `python app.py` directly in the activated virtual environment

**"Documents not loading"**
- Ensure the `data/documents.csv` file exists
- Check file permissions on the data folder

### Getting Help

1. **Check the console output** when running `start_dms.bat`
2. **Verify all files** are in the correct locations
3. **Try running as Administrator** if you encounter permission issues

## 🔄 Updates and Maintenance

### Updating the Application
1. **Download the new version** of the files
2. **Replace** the existing files (except `data/documents.csv`)
3. **Run** `start_dms.bat` to apply updates

### Backup Your Data
- Regularly backup the `data/documents.csv` file
- Keep copies of uploaded files in the `uploads` folder
- Consider using cloud storage for additional backup

## 📞 Support

For technical support or questions:
1. Check this README for common solutions
2. Review the console output for error messages
3. Ensure all requirements are met

---

**Truck DMS** - Making document management simple for trucking professionals.
