import os
import uuid
from datetime import datetime

class Config:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Upload folder
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    DATA_FOLDER = os.path.join(BASE_DIR, 'data')
    
    # Allowed extensions
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
    
    # Max file size (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # CSV file path
    CSV_FILE = os.path.join(DATA_FOLDER, 'documents.csv')
    USERS_FILE = os.path.join(DATA_FOLDER, 'users.csv')
    TAGS_FILE = os.path.join(DATA_FOLDER, 'tags.csv')
    
    # CSV columns - updated for trucking DMS
    CSV_COLUMNS = ['id', 'filename', 'original_name', 'upload_date', 'file_size', 
                   'file_type', 'document_type', 'title', 'amount', 'description', 
                   'driver_id', 'driver_name', 'driver_username', 'created_at',
                   'load_number', 'dispatcher', 'broker_shipper', 'pickup_address', 
                   'pickup_datetime', 'dropoff_address', 'dropoff_datetime', 'miles', 
                   'dh_miles', 'total_miles', 'rate_per_mile', 'bol_number', 'rc_number', 
                   'receipt_number', 'receipt_date', 'invoice_number', 'quickpay_percentage', 
                   'amount_received', 'rlp_number', 'date_received', 'dispatcher_company', 
                   'phone_number', 'email', 'rc_amount', 'dispatcher_percentage', 
                   'dispatcher_amount', 'document_name', 'download_count']
    
    # Users CSV columns
    USERS_COLUMNS = ['id', 'username', 'password', 'email', 'role', 'created_at', 'last_login', 'is_active']
    
    # Tags CSV columns
    TAGS_COLUMNS = ['id', 'name', 'color', 'description', 'created_by', 'created_at']
    
    @staticmethod
    def init_app():
        import pandas as pd
        import hashlib
        
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.DATA_FOLDER, exist_ok=True)
        
        # Create CSV if it doesn't exist
        if not os.path.exists(Config.CSV_FILE):
            df = pd.DataFrame(columns=Config.CSV_COLUMNS)
            df.to_csv(Config.CSV_FILE, index=False)
        
        # Create users CSV if it doesn't exist
        if not os.path.exists(Config.USERS_FILE):
            default_password = hashlib.sha256('admin123'.encode()).hexdigest()
            df_users = pd.DataFrame([{
                'id': str(uuid.uuid4()),
                'username': 'admin',
                'password': default_password,
                'email': 'admin@truckdms.com',
                'role': 'admin',
                'created_at': datetime.now().isoformat(),
                'last_login': '',
                'is_active': 'true'
            }])
            df_users.to_csv(Config.USERS_FILE, index=False)
        
        # Create tags CSV if it doesn't exist
        if not os.path.exists(Config.TAGS_FILE):
            df_tags = pd.DataFrame([{
                'id': str(uuid.uuid4()),
                'name': 'Urgent',
                'color': '#dc3545',
                'description': 'Urgent documents',
                'created_by': 'system',
                'created_at': datetime.now().isoformat()
            }])
            df_tags.to_csv(Config.TAGS_FILE, index=False)
        else:
            # Check if CSV has correct columns and update if needed
            try:
                df = pd.read_csv(Config.CSV_FILE)
                # Check if we need to update the structure
                if set(df.columns) != set(Config.CSV_COLUMNS):
                    # Backup old data and create new structure
                    old_data = df.to_dict('records') if len(df) > 0 else []
                    new_df = pd.DataFrame(columns=Config.CSV_COLUMNS)
                    
                    # Map old data to new structure if possible
                    for old_doc in old_data:
                        new_doc = {col: '' for col in Config.CSV_COLUMNS}
                        # Map existing fields
                        for col in old_doc:
                            if col in new_doc:
                                new_doc[col] = old_doc[col]
                        
                        # Ensure ID exists
                        if not new_doc.get('id') or new_doc['id'] == '':
                            new_doc['id'] = str(uuid.uuid4())
                        
                        # Set defaults for new required fields
                        if not new_doc.get('document_type'):
                            new_doc['document_type'] = 'rc'
                        if not new_doc.get('title'):
                            new_doc['title'] = new_doc.get('original_name', 'Untitled')
                        if not new_doc.get('amount'):
                            new_doc['amount'] = '0'
                        if not new_doc.get('driver_name'):
                            new_doc['driver_name'] = 'System'
                        if not new_doc.get('driver_username'):
                            new_doc['driver_username'] = 'system'
                        if not new_doc.get('driver_id'):
                            new_doc['driver_id'] = 'system'
                        if not new_doc.get('created_at'):
                            new_doc['created_at'] = old_doc.get('upload_date', '')
                        if not new_doc.get('download_count'):
                            new_doc['download_count'] = '0'
                        
                        new_df = pd.concat([new_df, pd.DataFrame([new_doc])], ignore_index=True)
                    
                    new_df.to_csv(Config.CSV_FILE, index=False)
            except Exception as e:
                print(f"Error updating CSV structure: {e}")
                # If there's an error, create a fresh CSV
                df = pd.DataFrame(columns=Config.CSV_COLUMNS)
                df.to_csv(Config.CSV_FILE, index=False)
