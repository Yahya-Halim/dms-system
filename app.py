from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd
import os
from datetime import datetime
import uuid
import json
from config.config import Config

# Document types for trucking DMS
DOCUMENT_TYPES = [
    {'id': 'rc', 'name': 'RC', 'color': '#dc3545', 'icon': 'fa-file-contract'},
    {'id': 'bol', 'name': 'BOL', 'color': '#fd7e14', 'icon': 'fa-file-invoice'},
    {'id': 'pod', 'name': 'POD', 'color': '#28a745', 'icon': 'fa-file-signature'},
    {'id': 'dispatcher', 'name': 'Dispatcher', 'color': '#17a2b8', 'icon': 'fa-headset'},
    {'id': 'fuel', 'name': 'Fuel', 'color': '#6f42c1', 'icon': 'fa-gas-pump'},
    {'id': 'invoice', 'name': 'Invoice', 'color': '#e83e8c', 'icon': 'fa-file-invoice-dollar'},
    {'id': 'rlp', 'name': 'RLP', 'color': '#6610f2', 'icon': 'fa-file-alt'}
]

# Document type fields
DOCUMENT_TYPE_FIELDS = {
    'rc': [
        {'id': 'load_number', 'label': 'Load Number', 'type': 'text'},
        {'id': 'dispatcher', 'label': 'Dispatcher', 'type': 'text'},
        {'id': 'broker_shipper', 'label': 'Broker/Shipper', 'type': 'text'},
        {'id': 'pickup_address', 'label': 'Pickup Address', 'type': 'text'},
        {'id': 'pickup_datetime', 'label': 'Pickup Date/Time', 'type': 'datetime-local'},
        {'id': 'dropoff_address', 'label': 'Dropoff Address', 'type': 'text'},
        {'id': 'dropoff_datetime', 'label': 'Dropoff Date/Time', 'type': 'datetime-local'},
        {'id': 'miles', 'label': 'Miles', 'type': 'number'},
        {'id': 'dh_miles', 'label': 'DH Miles', 'type': 'number'},
        {'id': 'total_miles', 'label': 'Total Miles', 'type': 'number'},
        {'id': 'rate_per_mile', 'label': 'Rate/Mile', 'type': 'number'},
        {'id': 'document_name', 'label': 'Document Name', 'type': 'text'}
    ],
    'bol': [
        {'id': 'bol_number', 'label': 'BOL #', 'type': 'text'},
        {'id': 'rc_number', 'label': 'RC Number/Load Number', 'type': 'text'},
        {'id': 'load_number', 'label': 'Load Number', 'type': 'text'},
        {'id': 'dispatcher', 'label': 'Dispatcher', 'type': 'text'},
        {'id': 'broker_shipper', 'label': 'Broker/Shipper', 'type': 'text'},
        {'id': 'pickup_address', 'label': 'Pickup Address', 'type': 'text'},
        {'id': 'pickup_datetime', 'label': 'Pickup Date/Time', 'type': 'datetime-local'},
        {'id': 'dropoff_address', 'label': 'Dropoff Address', 'type': 'text'},
        {'id': 'dropoff_datetime', 'label': 'Dropoff Date/Time', 'type': 'datetime-local'},
        {'id': 'miles', 'label': 'Miles', 'type': 'number'},
        {'id': 'dh_miles', 'label': 'DH Miles', 'type': 'number'},
        {'id': 'document_name', 'label': 'Document Name', 'type': 'text'}
    ],
    'pod': [
        {'id': 'rc_number', 'label': 'RC Number/Load Number', 'type': 'text'},
        {'id': 'load_number', 'label': 'Load Number', 'type': 'text'},
        {'id': 'dispatcher', 'label': 'Dispatcher', 'type': 'text'},
        {'id': 'broker_shipper', 'label': 'Broker/Shipper', 'type': 'text'},
        {'id': 'pickup_address', 'label': 'Pickup Address', 'type': 'text'},
        {'id': 'pickup_datetime', 'label': 'Pickup Date/Time', 'type': 'datetime-local'},
        {'id': 'dropoff_address', 'label': 'Dropoff Address', 'type': 'text'},
        {'id': 'dropoff_datetime', 'label': 'Dropoff Date/Time', 'type': 'datetime-local'},
        {'id': 'miles', 'label': 'Miles', 'type': 'number'},
        {'id': 'document_name', 'label': 'Document Name', 'type': 'text'}
    ],
    'dispatcher': [
        {'id': 'dispatcher_company', 'label': 'Dispatcher/Company', 'type': 'text'},
        {'id': 'phone_number', 'label': 'Phone Number', 'type': 'tel'},
        {'id': 'email', 'label': 'Email', 'type': 'email'},
        {'id': 'rc_number', 'label': 'RC Number', 'type': 'text'},
        {'id': 'load_number', 'label': 'Load Number', 'type': 'text'},
        {'id': 'broker_shipper', 'label': 'Broker/Shipper', 'type': 'text'},
        {'id': 'pickup_address', 'label': 'Pickup Address', 'type': 'text'},
        {'id': 'pickup_datetime', 'label': 'Pickup Date/Time', 'type': 'datetime-local'},
        {'id': 'dropoff_address', 'label': 'Dropoff Address', 'type': 'text'},
        {'id': 'dropoff_datetime', 'label': 'Dropoff Date/Time', 'type': 'datetime-local'},
        {'id': 'rc_amount', 'label': 'RC Amount $', 'type': 'number'},
        {'id': 'dispatcher_percentage', 'label': 'Dispatcher %', 'type': 'number'},
        {'id': 'dispatcher_amount', 'label': 'Dispatcher Amount', 'type': 'number'}
    ],
    'fuel': [
        {'id': 'receipt_number', 'label': 'Receipt #', 'type': 'text'},
        {'id': 'receipt_date', 'label': 'Receipt Date', 'type': 'date'},
        {'id': 'rc_number', 'label': 'RC Number', 'type': 'text'},
        {'id': 'load_number', 'label': 'Load Number', 'type': 'text'},
        {'id': 'pickup_address', 'label': 'Pickup Address', 'type': 'text'},
        {'id': 'pickup_datetime', 'label': 'Pickup Date/Time', 'type': 'datetime-local'},
        {'id': 'dropoff_address', 'label': 'Dropoff Address', 'type': 'text'},
        {'id': 'dropoff_datetime', 'label': 'Dropoff Date/Time', 'type': 'datetime-local'},
        {'id': 'rc_amount', 'label': 'RC Amount $', 'type': 'number'}
    ],
    'invoice': [
        {'id': 'invoice_number', 'label': 'Invoice #', 'type': 'text'},
        {'id': 'rc_number', 'label': 'RC Number/Load Number', 'type': 'text'},
        {'id': 'load_number', 'label': 'Load Number', 'type': 'text'},
        {'id': 'dispatcher', 'label': 'Dispatcher', 'type': 'text'},
        {'id': 'broker_shipper', 'label': 'Broker/Shipper', 'type': 'text'},
        {'id': 'pickup_address', 'label': 'Pickup', 'type': 'text'},
        {'id': 'dropoff_address', 'label': 'Dropoff', 'type': 'text'},
        {'id': 'miles', 'label': 'Miles', 'type': 'number'},
        {'id': 'dh_miles', 'label': 'DH Miles', 'type': 'number'},
        {'id': 'total_miles', 'label': 'Total Miles', 'type': 'number'},
        {'id': 'quickpay_percentage', 'label': 'Quick Pay %', 'type': 'number'},
        {'id': 'amount_received', 'label': 'Amount Received $', 'type': 'number'}
    ],
    'rlp': [
        {'id': 'rlp_number', 'label': 'RLP #', 'type': 'text'},
        {'id': 'date_received', 'label': 'Date Received', 'type': 'date'},
        {'id': 'invoice_number', 'label': 'Invoice #', 'type': 'text'},
        {'id': 'rc_number', 'label': 'RC Number/Load Number', 'type': 'text'},
        {'id': 'load_number', 'label': 'Load Number', 'type': 'text'},
        {'id': 'dispatcher', 'label': 'Dispatcher', 'type': 'text'},
        {'id': 'broker_shipper', 'label': 'Broker/Shipper', 'type': 'text'},
        {'id': 'total_miles', 'label': 'Total Miles', 'type': 'number'},
        {'id': 'quickpay_percentage', 'label': 'Quick Pay %', 'type': 'number'},
        {'id': 'amount_received', 'label': 'Amount Received $', 'type': 'number'}
    ]
}

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

# Initialize app
Config.init_app()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def ensure_document_ids():
    """Ensure all documents have valid IDs and proper structure"""
    try:
        # Check if file exists and has content
        if not os.path.exists(Config.CSV_FILE):
            return
        
        # Check file size
        if os.path.getsize(Config.CSV_FILE) == 0:
            return
        
        df = pd.read_csv(Config.CSV_FILE)
        if df.empty:
            return
        
        needs_update = False
        updated_docs = []
        
        for index, row in df.iterrows():
            try:
                doc = row.to_dict()
                
                # Generate new ID if missing or invalid
                if not doc.get('id') or doc['id'] == '' or pd.isna(doc['id']):
                    doc['id'] = str(uuid.uuid4())
                    needs_update = True
                
                # Ensure required fields have defaults
                if not doc.get('document_type') or pd.isna(doc['document_type']):
                    doc['document_type'] = 'rc'
                    needs_update = True
                
                if not doc.get('title') or pd.isna(doc['title']):
                    doc['title'] = doc.get('original_name', 'Untitled')
                    needs_update = True
                
                if not doc.get('amount') or pd.isna(doc['amount']):
                    doc['amount'] = 0.0
                    needs_update = True
                
                if not doc.get('driver_name') or pd.isna(doc['driver_name']):
                    doc['driver_name'] = 'System'
                    needs_update = True
                
                if not doc.get('driver_username') or pd.isna(doc['driver_username']):
                    doc['driver_username'] = 'system'
                    needs_update = True
                
                if not doc.get('driver_id') or pd.isna(doc['driver_id']):
                    doc['driver_id'] = 'system'
                    needs_update = True
                
                if not doc.get('download_count') or pd.isna(doc['download_count']):
                    doc['download_count'] = 0
                    needs_update = True
                
                # Ensure all CSV columns exist
                for col in Config.CSV_COLUMNS:
                    if col not in doc:
                        doc[col] = ''
                        needs_update = True
                
                updated_docs.append(doc)
                
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                continue
        
        if needs_update:
            updated_df = pd.DataFrame(updated_docs)
            updated_df.to_csv(Config.CSV_FILE, index=False)
            print("Updated document IDs and structure")
    
    except Exception as e:
        print(f"Error ensuring document IDs: {e}")
        # Create fresh CSV if there's an error
        try:
            df = pd.DataFrame(columns=Config.CSV_COLUMNS)
            df.to_csv(Config.CSV_FILE, index=False)
        except Exception as e2:
            print(f"Error creating fresh CSV: {e2}")

def get_document_by_id(doc_id):
    try:
        # Check if file exists and has content
        if not os.path.exists(Config.CSV_FILE):
            return None
        
        # Check file size
        if os.path.getsize(Config.CSV_FILE) == 0:
            return None
        
        df = pd.read_csv(Config.CSV_FILE)
        # Convert to records and handle the case where df might be empty
        if df.empty:
            return None
        
        documents = df.to_dict('records')
        # Find document by id
        for doc in documents:
            try:
                # Ensure doc is a dictionary and has an id
                if isinstance(doc, dict) and doc.get('id') == doc_id:
                    return doc
            except Exception as e:
                print(f"Error checking document ID: {e}")
                continue
        return None
    except Exception as e:
        print(f"Error in get_document_by_id: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/debug', methods=['GET'])
def debug_data():
    """Debug endpoint to check data structure"""
    try:
        debug_info = {
            'csv_exists': os.path.exists(Config.CSV_FILE),
            'csv_size': os.path.getsize(Config.CSV_FILE) if os.path.exists(Config.CSV_FILE) else 0,
            'csv_columns': Config.CSV_COLUMNS,
            'csv_file_path': Config.CSV_FILE
        }
        
        if os.path.exists(Config.CSV_FILE) and os.path.getsize(Config.CSV_FILE) > 0:
            try:
                df = pd.read_csv(Config.CSV_FILE)
                debug_info['df_shape'] = df.shape
                debug_info['df_columns'] = list(df.columns)
                debug_info['df_empty'] = df.empty
                
                if not df.empty:
                    # Show first few rows
                    debug_info['sample_data'] = df.head(1).to_dict('records')
                    
                    # Check for IDs
                    ids = df['id'].tolist() if 'id' in df.columns else []
                    debug_info['ids'] = ids[:5]  # First 5 IDs
                    debug_info['missing_ids'] = df['id'].isna().sum() if 'id' in df.columns else 'N/A'
            except Exception as e:
                debug_info['df_error'] = str(e)
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    try:
        # Ensure all documents have proper IDs and structure
        ensure_document_ids()
        
        # Check if file exists and has content
        if not os.path.exists(Config.CSV_FILE):
            return jsonify({'success': True, 'documents': []})
        
        # Check file size
        if os.path.getsize(Config.CSV_FILE) == 0:
            return jsonify({'success': True, 'documents': []})
        
        df = pd.read_csv(Config.CSV_FILE)
        # Handle empty DataFrame
        if df.empty:
            return jsonify({'success': True, 'documents': []})
        
        # Convert to records with proper handling
        documents = []
        for index, row in df.iterrows():
            try:
                doc = row.to_dict()
                # Ensure document has an ID
                if not doc.get('id') or doc['id'] == '' or pd.isna(doc['id']):
                    doc['id'] = str(uuid.uuid4())
                documents.append(doc)
            except Exception as e:
                print(f"Error processing document {index}: {e}")
                continue
        
        # Convert NaN to None for JSON serialization
        clean_documents = []
        for doc in documents:
            clean_doc = {}
            for key, value in doc.items():
                if pd.isna(value) or value == '':
                    clean_doc[key] = None if key not in ['amount', 'download_count'] else 0
                else:
                    clean_doc[key] = value
            clean_documents.append(clean_doc)
        
        return jsonify({'success': True, 'documents': clean_documents})
    except Exception as e:
        print(f"Error in get_documents: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    try:
        doc = get_document_by_id(doc_id)
        if doc:
            return jsonify({'success': True, 'document': doc})
        return jsonify({'success': False, 'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            file_ext = original_filename.rsplit('.', 1)[1].lower()
            unique_id = str(uuid.uuid4())
            filename = f"{unique_id}.{file_ext}"
            
            # Save file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Get file metadata
            file_size = os.path.getsize(file_path)
            
            # Get form data
            document_type = request.form.get('document_type', '')
            title = request.form.get('title', '')
            amount = request.form.get('amount', 0)
            description = request.form.get('description', '')
            driver_id = request.form.get('driver_id', 'system')
            driver_name = request.form.get('driver_name', 'System User')
            driver_username = request.form.get('driver_username', 'system')
            
            # Get document-specific fields - FIXED VERSION
            field_data = {}
            if document_type and document_type in DOCUMENT_TYPE_FIELDS:
                for field_dict in DOCUMENT_TYPE_FIELDS[document_type]:
                    field_id = field_dict['id']
                    # Get the field value directly from form (without field_ prefix)
                    field_value = request.form.get(field_id, '')
                    if field_value:
                        field_data[field_id] = field_value
                    else:
                        field_data[field_id] = ''
            
            # Create document record with guaranteed unique ID
            document = {
                'id': unique_id,
                'filename': filename,
                'original_name': original_filename,
                'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'file_size': file_size,
                'file_type': file_ext,
                'document_type': document_type,
                'title': title,
                'amount': float(amount) if amount else 0.0,
                'description': description,
                'driver_id': driver_id,
                'driver_name': driver_name,
                'driver_username': driver_username,
                'created_at': datetime.now().isoformat(),
                'download_count': 0,
                **field_data
            }
            
            # Ensure all CSV columns have values
            for col in Config.CSV_COLUMNS:
                if col not in document:
                    document[col] = ''
            
            # Save to CSV
            try:
                df = pd.read_csv(Config.CSV_FILE)
            except (FileNotFoundError, pd.errors.EmptyDataError):
                df = pd.DataFrame(columns=Config.CSV_COLUMNS)
            
            # Convert document to DataFrame and append
            doc_df = pd.DataFrame([document])
            df = pd.concat([df, doc_df], ignore_index=True)
            df.to_csv(Config.CSV_FILE, index=False)
            
            return jsonify({'success': True, 'document': document})
        
        return jsonify({'success': False, 'error': 'File type not allowed'}), 400
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<doc_id>', methods=['GET'])
def download_file(doc_id):
    try:
        doc = get_document_by_id(doc_id)
        if not doc:
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        # Handle case where doc might be None or missing filename
        filename = doc.get('filename')
        if not filename:
            return jsonify({'success': False, 'error': 'Filename not found'}), 404
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found on server'}), 404
        
        # Update download count
        try:
            df = pd.read_csv(Config.CSV_FILE)
            if not df.empty and 'id' in df.columns:
                mask = df['id'] == doc_id
                if mask.any():
                    df.loc[mask, 'download_count'] = df.loc[mask, 'download_count'].fillna(0) + 1
                    df.to_csv(Config.CSV_FILE, index=False)
        except Exception as e:
            print(f"Error updating download count: {e}")
        
        # Get original name for download
        original_name = doc.get('original_name', filename)
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=original_name
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete/<doc_id>', methods=['DELETE'])
def delete_file(doc_id):
    try:
        doc = get_document_by_id(doc_id)
        if not doc:
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        # Delete file from uploads folder
        filename = doc.get('filename')
        if filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete from CSV
        try:
            df = pd.read_csv(Config.CSV_FILE)
            if not df.empty and 'id' in df.columns:
                df = df[df['id'] != doc_id]
                df.to_csv(Config.CSV_FILE, index=False)
        except Exception as e:
            print(f"Error deleting from CSV: {e}")
        
        return jsonify({'success': True, 'message': 'Document deleted successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/document-types', methods=['GET'])
def get_document_types():
    return jsonify({'success': True, 'document_types': DOCUMENT_TYPES})

@app.route('/api/document-fields/<document_type>', methods=['GET'])
def get_document_fields(document_type):
    fields = DOCUMENT_TYPE_FIELDS.get(document_type, [])
    return jsonify({'success': True, 'fields': fields})

@app.route('/api/update/<doc_id>', methods=['PUT'])
def update_document(doc_id):
    try:
        data = request.json
        df = pd.read_csv(Config.CSV_FILE)
        
        if df.empty or 'id' not in df.columns:
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        if doc_id not in df['id'].values:
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        # Update basic fields
        for field in ['title', 'amount', 'description', 'document_type']:
            if field in data:
                df.loc[df['id'] == doc_id, field] = data[field]
        
        # Update document-specific fields - FIXED VERSION
        doc_type = data.get('document_type')
        if not doc_type:
            try:
                doc_type = df.loc[df['id'] == doc_id, 'document_type'].iloc[0]
            except (IndexError, KeyError):
                doc_type = None
        
        if doc_type and doc_type in DOCUMENT_TYPE_FIELDS:
            for field_dict in DOCUMENT_TYPE_FIELDS[doc_type]:
                field_id = field_dict['id']
                # Get field value directly from data
                field_value = data.get(field_id, '')
                df.loc[df['id'] == doc_id, field_id] = field_value
        
        df.to_csv(Config.CSV_FILE, index=False)
        
        return jsonify({'success': True, 'message': 'Document updated successfully'})
    
    except Exception as e:
        print(f"Update error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/api/search', methods=['GET'])
def search_documents():
    try:
        query = request.args.get('q', '').lower()
        document_type = request.args.get('document_type', '')
        file_type = request.args.get('type', '')
        
        df = pd.read_csv(Config.CSV_FILE)
        
        # Handle empty DataFrame
        if df.empty:
            return jsonify({'success': True, 'documents': []})
        
        # Apply filters
        if query:
            # Safe string operations with check for missing columns
            title_mask = df['title'].astype(str).str.lower().str.contains(query, na=False) if 'title' in df.columns else False
            desc_mask = df['description'].astype(str).str.lower().str.contains(query, na=False) if 'description' in df.columns else False
            driver_mask = df['driver_name'].astype(str).str.lower().str.contains(query, na=False) if 'driver_name' in df.columns else False
            
            df = df[title_mask | desc_mask | driver_mask]
        
        if document_type and 'document_type' in df.columns:
            df = df[df['document_type'] == document_type]
        
        if file_type and 'file_type' in df.columns:
            df = df[df['file_type'] == file_type]
        
        documents = df.replace({pd.NA: None, float('nan'): None}).to_dict('records')
        return jsonify({'success': True, 'documents': documents})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        df = pd.read_csv(Config.CSV_FILE)
        if df.empty or 'document_type' not in df.columns:
            return jsonify({'success': True, 'categories': []})
        
        document_types = df['document_type'].dropna().unique().tolist()
        return jsonify({'success': True, 'categories': document_types})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/api/debug/upload-test', methods=['POST'])
def debug_upload():
    """Debug endpoint to see what form data is being received"""
    try:
        debug_info = {
            'form_keys': list(request.form.keys()),
            'files_keys': list(request.files.keys()) if request.files else [],
            'form_data': {}
        }
        
        for key in request.form.keys():
            debug_info['form_data'][key] = request.form.get(key)
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/summary', methods=['GET'])
def get_summary():
    try:
        df = pd.read_csv(Config.CSV_FILE)
        
        # Handle empty DataFrame
        if df.empty:
            return jsonify({
                'success': True,
                'summary': {
                    'total_amount': 0.0,
                    'document_count': 0,
                    'type_counts': {},
                    'recent_documents': []
                }
            })
        
        # Total amount
        total_amount = 0.0
        if 'amount' in df.columns:
            total_amount = df['amount'].fillna(0).sum()
        
        # Count by document type
        type_counts = {}
        if 'document_type' in df.columns:
            type_counts = df['document_type'].value_counts().to_dict()
        
        # Recent documents
        recent_docs = []
        if 'created_at' in df.columns and len(df) > 0:
            try:
                # Convert created_at to datetime if it's not already
                df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
                recent_df = df.nlargest(5, 'created_at')
                recent_docs = recent_df.replace({pd.NA: None, float('nan'): None}).to_dict('records')
            except Exception as e:
                print(f"Error getting recent documents: {e}")
                recent_docs = []
        
        return jsonify({
            'success': True,
            'summary': {
                'total_amount': float(total_amount),
                'document_count': len(df),
                'type_counts': type_counts,
                'recent_documents': recent_docs
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
