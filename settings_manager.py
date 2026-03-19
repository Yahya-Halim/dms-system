import json
import os
from config.config import Config

SETTINGS_FILE = os.path.join(Config.DATA_FOLDER, 'settings.json')

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {
        'document_types': [
            {'id': 'rc', 'name': 'RC', 'color': '#dc3545', 'icon': 'fa-file-contract'},
            {'id': 'bol', 'name': 'BOL', 'color': '#fd7e14', 'icon': 'fa-file-invoice'},
            {'id': 'pod', 'name': 'POD', 'color': '#28a745', 'icon': 'fa-file-signature'},
            {'id': 'dispatcher', 'name': 'Dispatcher', 'color': '#17a2b8', 'icon': 'fa-headset'},
            {'id': 'fuel', 'name': 'Fuel', 'color': '#6f42c1', 'icon': 'fa-gas-pump'},
            {'id': 'invoice', 'name': 'Invoice', 'color': '#e83e8c', 'icon': 'fa-file-invoice-dollar'},
            {'id': 'rlp', 'name': 'RLP', 'color': '#6610f2', 'icon': 'fa-file-alt'}
        ],
        'document_type_fields': {
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
    }

def save_settings(settings):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)
