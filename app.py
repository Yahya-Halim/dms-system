from flask import Flask, request, jsonify, send_file, render_template, session, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd
import os
from datetime import datetime
import uuid
import hashlib
from functools import wraps
from config.config import Config
from settings_manager import load_settings, save_settings

app = Flask(__name__)
app.secret_key = 'truck_dms_secret_key_123'
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

# Initialize app
Config.init_app()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Admin privileges required'}), 403
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def ensure_document_ids():
    try:
        if not os.path.exists(Config.CSV_FILE):
            return
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
                if not doc.get('id') or doc['id'] == '' or pd.isna(doc['id']):
                    doc['id'] = str(uuid.uuid4())
                    needs_update = True
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
                for col in Config.CSV_COLUMNS:
                    if col not in doc:
                        doc[col] = ''
                        needs_update = True
                updated_docs.append(doc)
            except Exception as e:
                continue
        if needs_update:
            updated_df = pd.DataFrame(updated_docs)
            updated_df.to_csv(Config.CSV_FILE, index=False)
    except Exception as e:
        try:
            df = pd.DataFrame(columns=Config.CSV_COLUMNS)
            df.to_csv(Config.CSV_FILE, index=False)
        except Exception:
            pass

def get_document_by_id(doc_id):
    try:
        if not os.path.exists(Config.CSV_FILE):
            return None
        if os.path.getsize(Config.CSV_FILE) == 0:
            return None
        df = pd.read_csv(Config.CSV_FILE)
        if df.empty:
            return None
        documents = df.to_dict('records')
        for doc in documents:
            if isinstance(doc, dict) and doc.get('id') == doc_id:
                return doc
        return None
    except Exception:
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            df = pd.read_csv(Config.USERS_FILE)
            user_row = df[(df['username'] == username) & (df['is_active'] == True)]
            
            if not user_row.empty:
                hashed_pw = hashlib.sha256(password.encode()).hexdigest()
                user = user_row.iloc[0]
                
                if user['password'] == hashed_pw:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    
                    # Update last login
                    df.loc[df['id'] == user['id'], 'last_login'] = datetime.now().isoformat()
                    df.to_csv(Config.USERS_FILE, index=False)
                    
                    return redirect(url_for('index'))
            
            error = 'Invalid credentials or inactive account.'
        except Exception as e:
            error = f"Error reading users database: {str(e)}"
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role')
    }
    import json
    return render_template('index.html', user=json.dumps(user))

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html')

@app.route('/api/debug', methods=['GET'])
def debug_data():
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
                    debug_info['sample_data'] = df.head(1).to_dict('records')
            except Exception as e:
                debug_info['df_error'] = str(e)
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
@login_required
def get_documents():
    try:
        ensure_document_ids()
        if not os.path.exists(Config.CSV_FILE):
            return jsonify({'success': True, 'documents': []})
        if os.path.getsize(Config.CSV_FILE) == 0:
            return jsonify({'success': True, 'documents': []})
        df = pd.read_csv(Config.CSV_FILE)
        if df.empty:
            return jsonify({'success': True, 'documents': []})
        documents = []
        for index, row in df.iterrows():
            try:
                doc = row.to_dict()
                if not doc.get('id') or doc['id'] == '' or pd.isna(doc['id']):
                    doc['id'] = str(uuid.uuid4())
                documents.append(doc)
            except Exception:
                continue
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
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents/<doc_id>', methods=['GET'])
@login_required
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
            original_filename = secure_filename(file.filename)
            file_ext = original_filename.rsplit('.', 1)[1].lower()
            unique_id = str(uuid.uuid4())
            filename = f"{unique_id}.{file_ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            document_type = request.form.get('document_type', '')
            title = request.form.get('title', '')
            amount = request.form.get('amount', 0)
            description = request.form.get('description', '')
            driver_id = session.get('user_id', 'system')
            driver_name = session.get('username', 'System User')
            driver_username = session.get('username', 'system')
            field_data = {}
            settings = load_settings()
            if document_type and document_type in settings.get('document_type_fields', {}):
                for field_dict in settings['document_type_fields'][document_type]:
                    field_id = field_dict['id']
                    field_value = request.form.get(field_id, '')
                    field_data[field_id] = field_value if field_value else ''
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
            for col in Config.CSV_COLUMNS:
                if col not in document:
                    document[col] = ''
            try:
                df = pd.read_csv(Config.CSV_FILE)
            except (FileNotFoundError, pd.errors.EmptyDataError):
                df = pd.DataFrame(columns=Config.CSV_COLUMNS)
            doc_df = pd.DataFrame([document])
            df = pd.concat([df, doc_df], ignore_index=True)
            df.to_csv(Config.CSV_FILE, index=False)
            return jsonify({'success': True, 'document': document})
        return jsonify({'success': False, 'error': 'File type not allowed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<doc_id>', methods=['GET'])
def download_file(doc_id):
    try:
        doc = get_document_by_id(doc_id)
        if not doc:
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        filename = doc.get('filename')
        if not filename:
            return jsonify({'success': False, 'error': 'Filename not found'}), 404
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found on server'}), 404
        try:
            df = pd.read_csv(Config.CSV_FILE)
            if not df.empty and 'id' in df.columns:
                mask = df['id'] == doc_id
                if mask.any():
                    df.loc[mask, 'download_count'] = df.loc[mask, 'download_count'].fillna(0) + 1
                    df.to_csv(Config.CSV_FILE, index=False)
        except Exception:
            pass
        original_name = doc.get('original_name', filename)
        return send_file(file_path, as_attachment=True, download_name=original_name)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete/<doc_id>', methods=['DELETE'])
def delete_file(doc_id):
    try:
        doc = get_document_by_id(doc_id)
        if not doc:
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        filename = doc.get('filename')
        if filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        try:
            df = pd.read_csv(Config.CSV_FILE)
            if not df.empty and 'id' in df.columns:
                df = df[df['id'] != doc_id]
                df.to_csv(Config.CSV_FILE, index=False)
        except Exception:
            pass
        return jsonify({'success': True, 'message': 'Document deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/document-types', methods=['GET'])
@login_required
def get_document_types():
    settings = load_settings()
    return jsonify({'success': True, 'document_types': settings.get('document_types', [])})

@app.route('/api/document-fields/<document_type>', methods=['GET'])
@login_required
def get_document_fields(document_type):
    settings = load_settings()
    fields = settings.get('document_type_fields', {}).get(document_type, [])
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
        for field in ['title', 'amount', 'description', 'document_type']:
            if field in data:
                df.loc[df['id'] == doc_id, field] = data[field]
        doc_type = data.get('document_type')
        if not doc_type:
            try:
                doc_type = df.loc[df['id'] == doc_id, 'document_type'].iloc[0]
            except (IndexError, KeyError):
                doc_type = None
        settings = load_settings()
        if doc_type and doc_type in settings.get('document_type_fields', {}):
            for field_dict in settings['document_type_fields'][doc_type]:
                field_id = field_dict['id']
                field_value = data.get(field_id, '')
                df.loc[df['id'] == doc_id, field_id] = field_value
        df.to_csv(Config.CSV_FILE, index=False)
        return jsonify({'success': True, 'message': 'Document updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_documents():
    try:
        query = request.args.get('q', '').lower()
        document_type = request.args.get('document_type', '')
        file_type = request.args.get('type', '')
        filter_types = request.args.getlist('filter_types')
        df = pd.read_csv(Config.CSV_FILE)
        if df.empty:
            return jsonify({'success': True, 'documents': []})
        if query:
            title_mask = df['title'].astype(str).str.lower().str.contains(query, na=False) if 'title' in df.columns else False
            desc_mask = df['description'].astype(str).str.lower().str.contains(query, na=False) if 'description' in df.columns else False
            driver_mask = df['driver_name'].astype(str).str.lower().str.contains(query, na=False) if 'driver_name' in df.columns else False
            load_mask = df['load_number'].astype(str).str.lower().str.contains(query, na=False) if 'load_number' in df.columns else False
            rc_mask = df['rc_number'].astype(str).str.lower().str.contains(query, na=False) if 'rc_number' in df.columns else False
            bol_mask = df['bol_number'].astype(str).str.lower().str.contains(query, na=False) if 'bol_number' in df.columns else False
            dispatcher_mask = df['dispatcher'].astype(str).str.lower().str.contains(query, na=False) if 'dispatcher' in df.columns else False
            broker_mask = df['broker_shipper'].astype(str).str.lower().str.contains(query, na=False) if 'broker_shipper' in df.columns else False
            df = df[title_mask | desc_mask | driver_mask | load_mask | rc_mask | bol_mask | dispatcher_mask | broker_mask]
        if filter_types and 'document_type' in df.columns:
            df = df[df['document_type'].isin(filter_types)]
        elif document_type and 'document_type' in df.columns:
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

@app.route('/api/summary', methods=['GET'])
def get_summary():
    try:
        df = pd.read_csv(Config.CSV_FILE)
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
        total_amount = 0.0
        if 'amount' in df.columns:
            total_amount = df['amount'].fillna(0).sum()
        type_counts = {}
        if 'document_type' in df.columns:
            type_counts = df['document_type'].value_counts().to_dict()
        recent_docs = []
        if 'created_at' in df.columns and len(df) > 0:
            try:
                df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
                recent_df = df.nlargest(5, 'created_at')
                recent_docs = recent_df.replace({pd.NA: None, float('nan'): None}).to_dict('records')
            except Exception:
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

@app.route('/api/admin/users', methods=['GET', 'POST'])
@admin_required
def manage_users():
    try:
        df = pd.read_csv(Config.USERS_FILE)
        if request.method == 'GET':
            users = df.to_dict('records')
            for u in users:
                u.pop('password', None)
            return jsonify({'success': True, 'users': users})
            
        elif request.method == 'POST':
            data = request.json
            if data.get('username') in df['username'].values:
                return jsonify({'success': False, 'error': 'Username already exists'}), 400
            
            hashed_pw = hashlib.sha256(data.get('password', 'driver123').encode()).hexdigest()
            new_user = {
                'id': str(uuid.uuid4()),
                'username': data.get('username'),
                'password': hashed_pw,
                'email': data.get('email', ''),
                'role': data.get('role', 'driver'),
                'created_at': datetime.now().isoformat(),
                'last_login': '',
                'is_active': True
            }
            df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
            df.to_csv(Config.USERS_FILE, index=False)
            new_user.pop('password', None)
            return jsonify({'success': True, 'user': new_user})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<user_id>', methods=['PUT', 'DELETE'])
@admin_required
def manage_user(user_id):
    try:
        df = pd.read_csv(Config.USERS_FILE)
        if user_id not in df['id'].values:
            return jsonify({'success': False, 'error': 'User not found'}), 404
            
        if request.method == 'DELETE':
            df = df[df['id'] != user_id]
            df.to_csv(Config.USERS_FILE, index=False)
            return jsonify({'success': True, 'message': 'User deleted'})
            
        elif request.method == 'PUT':
            data = request.json
            idx = df.index[df['id'] == user_id].tolist()[0]
            if 'password' in data and data['password']:
                df.at[idx, 'password'] = hashlib.sha256(data['password'].encode()).hexdigest()
            for field in ['email', 'role', 'is_active']:
                if field in data:
                    df.at[idx, field] = data[field]
            df.to_csv(Config.USERS_FILE, index=False)
            return jsonify({'success': True, 'message': 'User updated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/settings', methods=['GET', 'POST'])
@admin_required
def manage_settings():
    if request.method == 'GET':
        settings = load_settings()
        return jsonify({'success': True, 'settings': settings})
    elif request.method == 'POST':
        settings = request.json
        save_settings(settings)
        return jsonify({'success': True, 'message': 'Settings saved'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
