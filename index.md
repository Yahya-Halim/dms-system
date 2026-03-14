---
layout: default
title: Truck DMS - Document Management System
description: A comprehensive document management system for trucking companies
permalink: /
---

# Truck DMS - Document Management System

A professional document management system designed specifically for trucking companies, supporting multiple document types with advanced filtering and export capabilities.

## 🚀 Features

### Document Management
- **Multiple Document Types**: RC, BOL, POD, Dispatcher, Fuel, Invoice, RLP
- **File Upload Support**: PDF, Excel, Word, images, and more
- **Smart Filtering**: Filter by document type, file type, and search terms
- **Document Editing**: Edit document details and custom fields

### Export Capabilities
- **PDF Export**: Generate professional PDF reports with document tables
- **Excel Export**: Create multi-sheet Excel workbooks with summary data
- **Filtered Export**: Export only documents you've filtered

### User Interface
- **Modern Design**: Clean, responsive interface with Tailwind CSS
- **Navigation Dropdowns**: Quick access to filters and export options
- **Real-time Updates**: Live document count and total amounts
- **Mobile Friendly**: Works on tablets and mobile devices

## 📋 Supported Document Types

| Type | Description | Key Fields |
|------|-------------|-------------|
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
- **Windows OS** (optimized for Windows with batch files)
- **2GB+ RAM** recommended
- **100MB+ Disk Space**

## 📦 Dependencies

The application uses these Python packages:
- `flask` - Web framework
- `pandas` - Data manipulation
- `openpyxl` - Excel file handling
- `xlrd` - Excel reading
- `xlsxwriter` - Excel writing

## 🚀 Quick Start

### Windows Setup
1. **Download** the project to your computer
2. **Run** `start_dms_simple.bat` for automatic setup
3. **Access** the application at `http://localhost:5000`

### Manual Setup
1. **Install Python 3.8+** from [python.org](https://www.python.org/)
2. **Clone** this repository
3. **Install dependencies**: `pip install flask pandas openpyxl xlrd xlsxwriter`
4. **Run**: `python app.py`
5. **Open browser** to `http://localhost:5000`

## 📁 Project Structure

```
dms-system/
├── app.py                 # Flask application
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
├── start_dms_simple.bat   # Windows launcher
└── README.md              # Documentation
```

## 🔍 Troubleshooting

### Common Issues

**"Python is not installed"**
- Download Python from [python.org](https://www.python.org/)
- Make sure to check "Add Python to PATH" during installation

**"Server won't start"**
- Check if port 5000 is already in use
- Try running `python app.py` directly
- Ensure all dependencies are installed

**"Documents not loading"**
- Verify `data/documents.csv` file exists
- Check file permissions on data folder
- Restart the application

## 📞 Support

For technical support or questions:
1. Check the [troubleshooting guide](#troubleshooting)
2. Review console output for error messages
3. Ensure all requirements are met

---

**Truck DMS** - Making document management simple for trucking professionals.

## 🤝 Contributing

We welcome contributions! Please feel free to:
- Report issues
- Suggest features
- Submit pull requests

## 📄 License

This project is open source and available under the MIT License.
