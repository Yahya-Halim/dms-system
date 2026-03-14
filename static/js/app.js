// API Base URL
const API_BASE = 'http://localhost:5000/api';

// Global variables
let documents = [];
let documentTypes = [];
let selectedFilterTypes = [];
let uploadedFile = null;
let currentFilteredDocuments = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDocumentTypes();
    loadDocuments();
    setupEventListeners();
    setupDropdowns();
});

// Dropdown functions
function setupDropdowns() {
    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#export-dropdown')) {
            document.getElementById('export-menu').classList.add('hidden');
        }
        if (!e.target.closest('#filter-dropdown')) {
            document.getElementById('filter-menu').classList.add('hidden');
        }
    });
}

function toggleExportDropdown() {
    const menu = document.getElementById('export-menu');
    menu.classList.toggle('hidden');
    // Close filter dropdown when opening export dropdown
    document.getElementById('filter-menu').classList.add('hidden');
}

function toggleFilterDropdown() {
    const menu = document.getElementById('filter-menu');
    menu.classList.toggle('hidden');
    // Close export dropdown when opening filter dropdown
    document.getElementById('export-menu').classList.add('hidden');
}

function applyNavFilters() {
    const documentType = document.getElementById('nav-document-type-filter').value;
    const fileType = document.getElementById('nav-file-type-filter').value;
    
    // Update the main filter inputs
    document.getElementById('document-type-filter').value = documentType;
    document.getElementById('type-filter').value = fileType;
    
    // Apply search
    searchDocuments();
    
    // Close dropdown
    document.getElementById('filter-menu').classList.add('hidden');
}

function exportFilteredDocuments(format) {
    if (currentFilteredDocuments.length === 0) {
        showNotification('No documents to export. Apply filters first.', 'error');
        return;
    }
    
    if (format === 'pdf') {
        exportToPDF();
    } else if (format === 'excel') {
        exportToExcel();
    }
    
    // Close dropdown
    document.getElementById('export-menu').classList.add('hidden');
}

function setupEventListeners() {
    // Search input with debounce
    let searchTimeout;
    document.getElementById('search-input').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchDocuments();
        }, 500);
    });

    // Filter changes
    document.getElementById('document-type-filter').addEventListener('change', searchDocuments);
    document.getElementById('type-filter').addEventListener('change', searchDocuments);

    // File drop area
    const dropArea = document.getElementById('file-drop-area');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    dropArea.addEventListener('drop', handleDrop, false);
    dropArea.addEventListener('click', () => document.getElementById('file-input').click());

    // Upload form submission
    document.getElementById('upload-form').addEventListener('submit', handleUpload);

    // Edit form submission
    document.getElementById('edit-form').addEventListener('submit', handleEdit);

    // Document type change
    document.getElementById('document-type').addEventListener('change', renderDocumentFields);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    document.getElementById('file-drop-area').classList.add('dragover');
}

function unhighlight() {
    document.getElementById('file-drop-area').classList.remove('dragover');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    document.getElementById('file-input').files = files;
    handleFileSelect(document.getElementById('file-input'));
}

function handleFileSelect(input) {
    const fileName = input.files[0]?.name;
    const fileNameElement = document.getElementById('selected-file-name');
    if (fileName) {
        fileNameElement.textContent = `Selected: ${fileName}`;
        fileNameElement.classList.add('text-green-600');
    } else {
        fileNameElement.textContent = '';
    }
}

// Modal functions
function openUploadModal() {
    document.getElementById('upload-modal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeUploadModal() {
    document.getElementById('upload-modal').classList.add('hidden');
    document.getElementById('upload-form').reset();
    document.getElementById('selected-file-name').textContent = '';
    document.getElementById('document-fields-container').innerHTML = '';
    document.body.style.overflow = 'auto';
}

async function openEditModal(doc) {
    currentEditId = doc.id;
    document.getElementById('edit-doc-id').value = doc.id;
    document.getElementById('edit-title').value = doc.title || '';
    document.getElementById('edit-amount').value = doc.amount || '';
    document.getElementById('edit-description').value = doc.description || '';
    
    // Populate document type selector
    const typeSelector = document.getElementById('edit-document-type');
    if (typeSelector) {
        // Clear existing options
        typeSelector.innerHTML = '<option value="">Select Document Type</option>';
        
        // Add all document types
        documentTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type.id;
            option.textContent = type.name;
            option.selected = doc.document_type === type.id;
            typeSelector.appendChild(option);
        });
        
        // Set current value
        typeSelector.value = doc.document_type || '';
        
        // Add change event listener
        typeSelector.onchange = async function() {
            const newType = this.value;
            await renderEditFields(newType, doc);
        };
    }
    
    // Get document type and render fields
    const documentType = doc.document_type;
    const type = documentTypes.find(t => t.id === documentType) || { name: documentType || 'Unknown', color: '#3b82f6', icon: 'fa-file' };
    
    // Create edit fields container
    const container = document.getElementById('edit-document-fields-container');
    if (!container) {
        // Add container if it doesn't exist
        const modal = document.getElementById('edit-modal');
        const form = modal.querySelector('form');
        const fieldsContainer = document.createElement('div');
        fieldsContainer.id = 'edit-document-fields-container';
        fieldsContainer.className = 'mb-6';
        
        // Insert before the buttons
        const buttonsContainer = form.querySelector('.flex.justify-end');
        form.insertBefore(fieldsContainer, buttonsContainer);
    }
    
    // Render initial fields
    if (documentType) {
        await renderEditFields(documentType, doc);
    }
    
    document.getElementById('edit-modal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

async function renderEditFields(documentType, doc) {
    const container = document.getElementById('edit-document-fields-container');
    if (!container) return;
    
    const type = documentTypes.find(t => t.id === documentType) || { name: documentType || 'Unknown', color: '#3b82f6', icon: 'fa-file' };
    
    try {
        const response = await fetch(`${API_BASE}/document-fields/${documentType}`);
        const data = await response.json();
        
        if (data.success) {
            const fields = data.fields;
            
            let html = `
                <fieldset class="border-2 border-gray-200 rounded-lg p-4 mb-4">
                    <legend class="text-sm font-medium text-gray-700 px-2" style="background: ${type.color}20; color: ${type.color}; border: 1px solid ${type.color}40; border-radius: 0.375rem;">
                        <i class="fas ${type.icon} mr-2"></i>${type.name} Fields
                    </legend>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            `;
            
            fields.forEach(field => {
                const fieldValue = doc[field.id] || '';
                html += `
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">${field.label}</label>
                        <input type="${field.type}" name="edit_field_${field.id}" value="${fieldValue}" placeholder="${field.label}" 
                               class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    </div>
                `;
            });
            
            html += '</div></fieldset>';
            container.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading document fields:', error);
    }
}

function closeEditModal() {
    document.getElementById('edit-modal').classList.add('hidden');
    document.getElementById('edit-form').reset();
    // Clear document fields
    const fieldsContainer = document.getElementById('edit-document-fields-container');
    if (fieldsContainer) {
        fieldsContainer.innerHTML = '';
    }
    document.body.style.overflow = 'auto';
}

function showLoading() {
    document.getElementById('loading-spinner').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-spinner').classList.add('hidden');
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white z-50 transition-all transform translate-x-0`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// API Calls
async function loadDocumentTypes() {
    try {
        const response = await fetch(`${API_BASE}/document-types`);
        const data = await response.json();
        
        if (data.success) {
            documentTypes = data.document_types;
            populateDocumentTypeDropdown();
            renderFilterTags();
        }
    } catch (error) {
        console.error('Error loading document types:', error);
    }
}

async function loadDocuments() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/documents`);
        const data = await response.json();
        
        if (data.success) {
            documents = data.documents;
            currentFilteredDocuments = data.documents;
            displayDocuments(documents);
            updateDocumentCount(documents.length);
            updateTotalAmount(documents);
            populateNavDropdowns();
        } else {
            showNotification('Failed to load documents', 'error');
        }
    } catch (error) {
        console.error('Error loading documents:', error);
        showNotification('Error loading documents', 'error');
    } finally {
        hideLoading();
    }
}

function populateDocumentTypeDropdown() {
    const typeSelect = document.getElementById('document-type');
    const navTypeSelect = document.getElementById('nav-document-type-filter');
    
    if (typeSelect) {
        typeSelect.innerHTML = '<option value="">Select document type</option>';
        documentTypes.forEach(type => {
            typeSelect.innerHTML += `<option value="${type.id}">${type.name}</option>`;
        });
    }
    
    if (navTypeSelect) {
        navTypeSelect.innerHTML = '<option value="">All Types</option>';
        documentTypes.forEach(type => {
            navTypeSelect.innerHTML += `<option value="${type.id}">${type.name}</option>`;
        });
    }
}

function populateNavDropdowns() {
    // Populate file type dropdown
    const fileTypeSelect = document.getElementById('type-filter');
    const navFileTypeSelect = document.getElementById('nav-file-type-filter');
    
    if (fileTypeSelect) {
        const fileTypes = [...new Set(documents.map(doc => doc.file_type).filter(Boolean))];
        fileTypeSelect.innerHTML = '<option value="">All File Types</option>';
        fileTypes.forEach(type => {
            fileTypeSelect.innerHTML += `<option value="${type}">${type.toUpperCase()}</option>`;
        });
    }
    
    if (navFileTypeSelect) {
        const fileTypes = [...new Set(documents.map(doc => doc.file_type).filter(Boolean))];
        navFileTypeSelect.innerHTML = '<option value="">All File Types</option>';
        fileTypes.forEach(type => {
            navFileTypeSelect.innerHTML += `<option value="${type}">${type.toUpperCase()}</option>`;
        });
    }
}

function renderFilterTags() {
    const container = document.getElementById('filter-tags');
    if (!container) return;
    
    container.innerHTML = '';
    documentTypes.forEach(type => {
        const button = document.createElement('button');
        button.className = `filter-tag ${selectedFilterTypes.includes(type.id) ? 'active' : ''}`;
        button.style.backgroundColor = selectedFilterTypes.includes(type.id) ? type.color : '';
        button.style.borderColor = selectedFilterTypes.includes(type.id) ? type.color : '#e2e8f0';
        button.textContent = type.name;
        button.onclick = () => {
            const index = selectedFilterTypes.indexOf(type.id);
            if (index === -1) {
                selectedFilterTypes.push(type.id);
            } else {
                selectedFilterTypes.splice(index, 1);
            }
            renderFilterTags();
            searchDocuments();
        };
        container.appendChild(button);
    });
}

async function renderDocumentFields() {
    const documentType = document.getElementById('document-type').value;
    const container = document.getElementById('document-fields-container');
    
    if (!container || !documentType) {
        container.innerHTML = '';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/document-fields/${documentType}`);
        const data = await response.json();
        
        if (data.success) {
            const type = documentTypes.find(t => t.id === documentType);
            const fields = data.fields;
            
            let html = `
                <fieldset class="border-2 border-gray-200 rounded-lg p-4 mb-4">
                    <legend class="text-sm font-medium text-gray-700 px-2" style="background: ${type?.color}20; color: ${type?.color}; border: 1px solid ${type?.color}40; border-radius: 0.375rem;">
                        <i class="fas ${type?.icon} mr-2"></i>${type?.name} Fields
                    </legend>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            `;
            
            fields.forEach(field => {
                html += `
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">${field.label}</label>
                        <input type="${field.type}" name="field_${field.id}" placeholder="${field.label}" 
                               class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    </div>
                `;
            });
            
            html += '</div></fieldset>';
            container.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading document fields:', error);
    }
}

async function searchDocuments() {
    const query = document.getElementById('search-input').value;
    const documentType = document.getElementById('document-type-filter').value;
    const fileType = document.getElementById('type-filter').value;
    
    // Update navigation dropdowns to match
    document.getElementById('nav-document-type-filter').value = documentType;
    document.getElementById('nav-file-type-filter').value = fileType;
    
    showLoading();
    try {
        const params = new URLSearchParams();
        if (query) params.append('q', query);
        if (documentType) params.append('document_type', documentType);
        if (fileType) params.append('type', fileType);
        
        const response = await fetch(`${API_BASE}/search?${params}`);
        const data = await response.json();
        
        if (data.success) {
            currentFilteredDocuments = data.documents;
            displayDocuments(data.documents);
            updateDocumentCount(data.documents.length);
            updateTotalAmount(data.documents);
        }
    } catch (error) {
        console.error('Error searching documents:', error);
        showNotification('Error searching documents', 'error');
    } finally {
        hideLoading();
    }
}

async function handleUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('file-input');
    if (!fileInput.files[0]) {
        showNotification('Please select a file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('document_type', document.getElementById('document-type').value);
    formData.append('title', document.getElementById('title').value);
    formData.append('amount', document.getElementById('amount').value);
    formData.append('description', document.getElementById('description').value);
    formData.append('driver_id', 'system');
    formData.append('driver_name', 'System User');
    formData.append('driver_username', 'system');
    
    // Add document-specific fields - FIXED VERSION
    const documentType = document.getElementById('document-type').value;
    if (documentType) {
        const response = await fetch(`${API_BASE}/document-fields/${documentType}`);
        const fieldsData = await response.json();
        if (fieldsData.success) {
            fieldsData.fields.forEach(field => {
                const fieldInput = document.querySelector(`input[name="field_${field.id}"]`);
                const fieldValue = fieldInput ? fieldInput.value : '';
                // Append with field.id as the key (without 'field_' prefix)
                formData.append(field.id, fieldValue);
            });
        }
    }
    
    const uploadBtn = document.getElementById('upload-btn');
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Uploading...';
    
    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Document uploaded successfully');
            closeUploadModal();
            loadDocuments();
        } else {
            showNotification(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        console.error('Error uploading document:', error);
        showNotification('Error uploading document', 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = 'Upload Document';
    }
}

async function handleEdit(e) {
    e.preventDefault();
    
    const docId = document.getElementById('edit-doc-id').value;
    const data = {
        title: document.getElementById('edit-title').value,
        amount: document.getElementById('edit-amount').value,
        description: document.getElementById('edit-description').value
    };
    
    const typeSelector = document.getElementById('edit-document-type');
    if (typeSelector) {
        data.document_type = typeSelector.value;
    }
    
    // Add document-specific fields - FIXED VERSION
    if (data.document_type) {
        try {
            const response = await fetch(`${API_BASE}/document-fields/${data.document_type}`);
            const fieldsData = await response.json();
            if (fieldsData.success) {
                fieldsData.fields.forEach(field => {
                    const fieldInput = document.querySelector(`input[name="edit_field_${field.id}"]`);
                    const fieldValue = fieldInput ? fieldInput.value : '';
                    // Use field.id as the key
                    data[field.id] = fieldValue;
                });
            }
        } catch (error) {
            console.error('Error getting document fields:', error);
        }
    }
    
    try {
        const response = await fetch(`${API_BASE}/update/${docId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Document updated successfully');
            closeEditModal();
            loadDocuments();
        } else {
            showNotification(result.error || 'Update failed', 'error');
        }
    } catch (error) {
        console.error('Error updating document:', error);
        showNotification('Error updating document', 'error');
    }
}

async function downloadDocument(id) {
    try {
        window.location.href = `${API_BASE}/download/${id}`;
    } catch (error) {
        console.error('Error downloading document:', error);
        showNotification('Error downloading document', 'error');
    }
}

async function deleteDocument(id) {
    if (!confirm('Are you sure you want to delete this document?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/delete/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Document deleted successfully');
            loadDocuments();
        } else {
            showNotification(data.error || 'Delete failed', 'error');
        }
    } catch (error) {
        console.error('Error deleting document:', error);
        showNotification('Error deleting document', 'error');
    }
}

// Display functions
function displayDocuments(documents) {
    const grid = document.getElementById('documents-grid');
    const emptyState = document.getElementById('empty-state');
    
    if (!documents || documents.length === 0) {
        grid.innerHTML = '';
        emptyState.classList.remove('hidden');
        return;
    }
    
    emptyState.classList.add('hidden');
    
    grid.innerHTML = documents.map(doc => createDocumentCard(doc)).join('');
}

function createDocumentCard(doc) {
    // Ensure doc is a valid object
    if (!doc || typeof doc !== 'object') {
        return '';
    }
    
    const type = documentTypes.find(t => t.id === doc.document_type) || { color: '#3b82f6', icon: 'fa-file', name: doc.document_type || 'Unknown' };
    const tagChip = `<span class="tag-chip" style="background:${type.color}20; color:${type.color}; border:1px solid ${type.color}40"><i class="fas ${type.icon} mr-1"></i>${type.name}</span>`;
    const fileSize = formatFileSize(doc.file_size || 0);
    const uploadDate = doc.upload_date ? new Date(doc.upload_date).toLocaleDateString() : 'Unknown';
    
    // Show key fields based on type - ENHANCED VERSION
    let details = '';
    if (doc.document_type === 'rc') {
        details = `
            <div class="text-sm text-gray-600">
                Load: ${doc.load_number || ''} · Dispatcher: ${doc.dispatcher || ''}<br>
                ${doc.pickup_address ? `Pickup: ${doc.pickup_address}` : ''}<br>
                Miles: ${doc.miles || '0'} · $${parseFloat(doc.amount || 0).toFixed(2)}
            </div>`;
    } else if (doc.document_type === 'bol') {
        details = `
            <div class="text-sm text-gray-600">
                BOL: ${doc.bol_number || ''} · RC: ${doc.rc_number || ''}<br>
                ${doc.pickup_address ? `From: ${doc.pickup_address}` : ''}<br>
                ${doc.dropoff_address ? `To: ${doc.dropoff_address}` : ''}
            </div>`;
    } else if (doc.document_type === 'pod') {
        details = `
            <div class="text-sm text-gray-600">
                RC: ${doc.rc_number || ''} · Load: ${doc.load_number || ''}<br>
                Miles: ${doc.miles || ''} · ${doc.pickup_address || ''}
            </div>`;
    } else if (doc.document_type === 'dispatcher') {
        details = `
            <div class="text-sm text-gray-600">
                ${doc.dispatcher_company || ''} · ${doc.phone_number || ''}<br>
                RC $${parseFloat(doc.rc_amount || 0).toFixed(2)} · Disp $${parseFloat(doc.dispatcher_amount || 0).toFixed(2)}
            </div>`;
    } else if (doc.document_type === 'fuel') {
        details = `
            <div class="text-sm text-gray-600">
                Receipt #${doc.receipt_number || ''} · ${doc.receipt_date || ''}<br>
                Amount: $${parseFloat(doc.amount || 0).toFixed(2)} · RC: ${doc.rc_number || ''}
            </div>`;
    } else if (doc.document_type === 'invoice') {
        details = `
            <div class="text-sm text-gray-600">
                Inv #${doc.invoice_number || ''} · RC: ${doc.rc_number || ''}<br>
                RC Amt: $${parseFloat(doc.amount || 0).toFixed(2)} · Rec: $${parseFloat(doc.amount_received || 0).toFixed(2)}
            </div>`;
    } else if (doc.document_type === 'rlp') {
        details = `
            <div class="text-sm text-gray-600">
                RLP #${doc.rlp_number || ''} · Rec'd: ${doc.date_received || ''}<br>
                RC Amt: $${parseFloat(doc.amount || 0).toFixed(2)} · Rec: $${parseFloat(doc.amount_received || 0).toFixed(2)}
            </div>`;
    }
    
    return `
        <div class="document-card" onclick="viewDocument('${doc.id || ''}')">
            <div class="flex justify-between items-start mb-3">
                <h3 class="text-lg font-semibold text-gray-900">${doc.title || doc.original_name || 'Untitled'}</h3>
                <span class="text-lg font-bold text-green-600">$${parseFloat(doc.amount || 0).toFixed(2)}</span>
            </div>
            <p class="text-gray-600 text-sm mb-3">${doc.description || ''}</p>
            <div class="flex flex-wrap gap-2 mb-3">${tagChip}</div>
            <div class="text-gray-700 mb-2">${details}</div>
            <div class="text-xs text-gray-500 mb-2">${fileSize} • ${uploadDate}</div>
            <div class="flex justify-between items-center mt-3">
                <div class="text-xs text-gray-400">${doc.driver_name || 'System'} • ${doc.download_count || 0} downloads</div>
                <div class="flex space-x-2">
                    <button onclick='event.stopPropagation(); viewDocument("${doc.id || ''}")' 
                            class="text-blue-600 hover:text-blue-800 transition-colors"
                            title="View Document">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick='event.stopPropagation(); openEditModal(${JSON.stringify(doc).replace(/'/g, "\\'")})' 
                            class="text-gray-400 hover:text-blue-600 transition-colors"
                            title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick='event.stopPropagation(); downloadDocument("${doc.id || ''}")' 
                            class="text-gray-400 hover:text-green-600 transition-colors"
                            title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    <button onclick='event.stopPropagation(); deleteDocument("${doc.id || ''}")' 
                            class="text-gray-400 hover:text-red-600 transition-colors"
                            title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

function viewDocument(docId) {
    const doc = documents.find(d => d.id === docId);
    if (!doc) return;
    
    const type = documentTypes.find(t => t.id === doc.document_type) || { 
        name: doc.document_type || 'Unknown', 
        color: '#3b82f6', 
        icon: 'fa-file' 
    };
    
    // Get all fields that have values (excluding standard fields)
    const standardFields = ['id', 'filename', 'original_name', 'upload_date', 'file_size', 
                           'file_type', 'document_type', 'title', 'amount', 'description', 
                           'driver_id', 'driver_name', 'driver_username', 'created_at', 
                           'download_count'];
    
    const customFields = [];
    for (const [key, value] of Object.entries(doc)) {
        if (!standardFields.includes(key) && value && value !== '') {
            customFields.push({ key, value });
        }
    }
    
    let viewHtml = `
        <div class="modal" onclick="if(event.target === this) this.remove()">
            <div class="modal-content w-full max-w-6xl mx-auto max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold" style="color: ${type.color}">
                        <i class="fas ${type.icon} mr-2"></i>${doc.title || doc.original_name || 'Untitled'} - ${type.name} View
                    </h2>
                    <div class="flex gap-2">
                        <button onclick="exportDocumentPDF('${doc.id}')" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all">
                            <i class="fas fa-file-pdf mr-2"></i>Export PDF
                        </button>
                        <button onclick="this.closest('.modal').remove()" class="text-gray-500 hover:text-gray-700 text-2xl">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Basic Information -->
                    <div class="bg-gray-50 p-6 rounded-xl">
                        <h3 class="text-lg font-bold mb-4 text-gray-800">Basic Information</h3>
                        <div class="space-y-3">
                            <div>
                                <div class="text-xs uppercase text-gray-500">Title</div>
                                <div class="font-semibold">${doc.title || ''}</div>
                            </div>
                            <div>
                                <div class="text-xs uppercase text-gray-500">Amount</div>
                                <div class="font-semibold text-green-600">$${parseFloat(doc.amount || 0).toFixed(2)}</div>
                            </div>
                            <div>
                                <div class="text-xs uppercase text-gray-500">Description</div>
                                <div class="font-semibold">${doc.description || 'No description'}</div>
                            </div>
                            <div>
                                <div class="text-xs uppercase text-gray-500">Driver</div>
                                <div class="font-semibold">${doc.driver_name || 'System'}</div>
                            </div>
                            <div>
                                <div class="text-xs uppercase text-gray-500">Created Date</div>
                                <div class="font-semibold">${doc.created_at ? new Date(doc.created_at).toLocaleString() : (doc.upload_date ? new Date(doc.upload_date).toLocaleString() : 'Unknown')}</div>
                            </div>
                            <div>
                                <div class="text-xs uppercase text-gray-500">File Name</div>
                                <div class="font-semibold">${doc.original_name || ''}</div>
                            </div>
                            <div>
                                <div class="text-xs uppercase text-gray-500">File Size</div>
                                <div class="font-semibold">${formatFileSize(doc.file_size || 0)}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Document Specific Fields -->
                    <div class="bg-gray-50 p-6 rounded-xl">
                        <h3 class="text-lg font-bold mb-4 text-gray-800">${type.name} Fields</h3>
                        <div class="space-y-3" id="document-fields-view">
    `;
    
    // Add custom fields dynamically
    const fieldLabels = {
        'load_number': 'Load Number',
        'dispatcher': 'Dispatcher',
        'broker_shipper': 'Broker/Shipper',
        'pickup_address': 'Pickup Address',
        'pickup_datetime': 'Pickup Date/Time',
        'dropoff_address': 'Dropoff Address',
        'dropoff_datetime': 'Dropoff Date/Time',
        'miles': 'Miles',
        'dh_miles': 'DH Miles',
        'total_miles': 'Total Miles',
        'rate_per_mile': 'Rate/Mile',
        'bol_number': 'BOL Number',
        'rc_number': 'RC Number',
        'receipt_number': 'Receipt Number',
        'receipt_date': 'Receipt Date',
        'invoice_number': 'Invoice Number',
        'quickpay_percentage': 'Quick Pay %',
        'amount_received': 'Amount Received',
        'rlp_number': 'RLP Number',
        'date_received': 'Date Received',
        'dispatcher_company': 'Dispatcher Company',
        'phone_number': 'Phone Number',
        'email': 'Email',
        'rc_amount': 'RC Amount',
        'dispatcher_percentage': 'Dispatcher %',
        'dispatcher_amount': 'Dispatcher Amount',
        'document_name': 'Document Name'
    };
    
    customFields.forEach(field => {
        const label = fieldLabels[field.key] || field.key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        let displayValue = field.value;
        
        // Format currency fields
        if (field.key.includes('amount') || field.key.includes('Amount') || 
            field.key === 'rate_per_mile' || field.key === 'rc_amount' || 
            field.key === 'dispatcher_amount' || field.key === 'amount_received') {
            displayValue = `$${parseFloat(field.value || 0).toFixed(2)}`;
        }
        
        viewHtml += `
            <div>
                <div class="text-xs uppercase text-gray-500">${label}</div>
                <div class="font-semibold">${displayValue}</div>
            </div>
        `;
    });
    
    viewHtml += `
                        </div>
                    </div>
                </div>
                
                <div class="flex justify-end mt-6 gap-3">
                    <button onclick='openEditModal(${JSON.stringify(doc).replace(/'/g, "\\'")})' class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all">
                        <i class="fas fa-edit mr-2"></i>Edit Document
                    </button>
                    <button onclick="downloadDocument('${doc.id}')" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all">
                        <i class="fas fa-download mr-2"></i>Download File
                    </button>
                    <button onclick="this.closest('.modal').remove()" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-all">
                        Close
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', viewHtml);
}

function exportToPDF() {
    try {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF({ orientation: 'landscape' });
        
        // Group documents by type
        const documentsByType = {};
        currentFilteredDocuments.forEach(doc => {
            const type = doc.document_type || 'unknown';
            if (!documentsByType[type]) {
                documentsByType[type] = [];
            }
            documentsByType[type].push(doc);
        });
        
        let yPosition = 20;
        
        // Title
        pdf.setFontSize(16);
        pdf.setTextColor(16, 185, 129);
        pdf.text('Truck DMS - Exported Documents', 14, yPosition);
        yPosition += 15;
        
        pdf.setFontSize(10);
        pdf.setTextColor(100, 116, 139);
        pdf.text(`Generated: ${new Date().toLocaleDateString()} · ${currentFilteredDocuments.length} document(s)`, 14, yPosition);
        yPosition += 10;
        
        // Calculate total amount
        const totalAmount = currentFilteredDocuments.reduce((sum, doc) => sum + (parseFloat(doc.amount) || 0), 0);
        pdf.text(`Total Amount: $${totalAmount.toFixed(2)}`, 14, yPosition);
        yPosition += 15;
        
        // Process each document type
        Object.keys(documentsByType).forEach(docType => {
            if (yPosition > 180) {
                pdf.addPage();
                yPosition = 20;
            }
            
            const type = documentTypes.find(t => t.id === docType) || { name: docType, color: '#3b82f6' };
            const docs = documentsByType[docType];
            
            // Section title
            pdf.setFontSize(12);
            pdf.setTextColor(type.color.replace('#', '0x'));
            pdf.text(`${type.name.toUpperCase()} (${docs.length})`, 14, yPosition);
            yPosition += 10;
            
            // Get headers for this document type
            const headers = getPDFHeadersForType(docType);
            
            // Create table data
            const rows = docs.map(doc => getPDFRowsForDocument(doc));
            
            // Create table
            pdf.autoTable({
                startY: yPosition,
                head: [headers],
                body: rows,
                theme: 'grid',
                headStyles: { 
                    fillColor: [type.color.replace('#', '0x'), 100], 
                    textColor: [255, 255, 255], 
                    fontStyle: 'bold', 
                    fontSize: 8 
                },
                styles: { fontSize: 7, cellPadding: 1 },
                margin: { left: 14, right: 14 },
                columnStyles: { 0: { cellWidth: 25 } }
            });
            
            yPosition = pdf.lastAutoTable.finalY + 10;
        });
        
        // Save PDF
        const filename = `truck_dms_export_${new Date().toISOString().slice(0,10)}.pdf`;
        pdf.save(filename);
        
        showNotification('PDF exported successfully');
    } catch (error) {
        console.error('Error exporting PDF:', error);
        showNotification('Error exporting PDF', 'error');
    }
}

function exportToExcel() {
    try {
        // Group documents by type
        const documentsByType = {};
        currentFilteredDocuments.forEach(doc => {
            const type = doc.document_type || 'unknown';
            if (!documentsByType[type]) {
                documentsByType[type] = [];
            }
            documentsByType[type].push(doc);
        });
        
        // Create workbook
        const wb = XLSX.utils.book_new();
        
        // Process each document type
        Object.keys(documentsByType).forEach(docType => {
            const type = documentTypes.find(t => t.id === docType) || { name: docType };
            const docs = documentsByType[docType];
            
            // Create worksheet data
            const wsData = [];
            
            // Add headers
            const headers = getExcelHeadersForType(docType);
            wsData.push(headers);
            
            // Add document data
            docs.forEach(doc => {
                const row = getExcelRowForDocument(doc, docType);
                wsData.push(row);
            });
            
            // Create worksheet
            const ws = XLSX.utils.aoa_to_sheet(wsData);
            
            // Set column widths
            const colWidths = headers.map(() => ({ wch: 15 }));
            ws['!cols'] = colWidths;
            
            // Add worksheet to workbook
            XLSX.utils.book_append_sheet(wb, ws, type.name);
        });
        
        // Add summary sheet
        const summaryData = [
            ['Document Type', 'Count', 'Total Amount'],
            ...Object.keys(documentsByType).map(docType => {
                const type = documentTypes.find(t => t.id === docType) || { name: docType };
                const docs = documentsByType[docType];
                const totalAmount = docs.reduce((sum, doc) => sum + (parseFloat(doc.amount) || 0), 0);
                return [type.name, docs.length, `$${totalAmount.toFixed(2)}`];
            }),
            ['TOTAL', currentFilteredDocuments.length, `$${currentFilteredDocuments.reduce((sum, doc) => sum + (parseFloat(doc.amount) || 0), 0).toFixed(2)}`]
        ];
        
        const summaryWs = XLSX.utils.aoa_to_sheet(summaryData);
        summaryWs['!cols'] = [{ wch: 20 }, { wch: 10 }, { wch: 15 }];
        XLSX.utils.book_append_sheet(wb, summaryWs, 'Summary');
        
        // Save file
        const filename = `truck_dms_export_${new Date().toISOString().slice(0,10)}.xlsx`;
        XLSX.writeFile(wb, filename);
        
        showNotification('Excel exported successfully');
    } catch (error) {
        console.error('Error exporting Excel:', error);
        showNotification('Error exporting Excel', 'error');
    }
}

function getExcelHeadersForType(documentType) {
    const headers = {
        'rc': ['Date', 'Load Number', 'Dispatcher', 'Broker/Shipper', 'Pickup Address', 'Pickup Date/Time', 'Dropoff Address', 'Dropoff Date/Time', 'Miles', 'DH Miles', 'Total Miles', 'Rate/Mile', 'Amount', 'Document Name'],
        'bol': ['Date', 'BOL Number', 'RC Number', 'Load Number', 'Dispatcher', 'Broker/Shipper', 'Pickup Address', 'Pickup Date/Time', 'Dropoff Address', 'Dropoff Date/Time', 'Miles', 'DH Miles', 'Document Name'],
        'pod': ['Date', 'RC Number', 'Load Number', 'Dispatcher', 'Broker/Shipper', 'Pickup Address', 'Pickup Date/Time', 'Dropoff Address', 'Dropoff Date/Time', 'Miles', 'Document Name'],
        'dispatcher': ['Date', 'Dispatcher Company', 'Phone Number', 'Email', 'RC Number', 'Load Number', 'Broker/Shipper', 'Pickup Address', 'Pickup Date/Time', 'Dropoff Address', 'Dropoff Date/Time', 'RC Amount', 'Dispatcher %', 'Dispatcher Amount'],
        'fuel': ['Date', 'Receipt Number', 'Receipt Date', 'Amount', 'RC Number', 'Load Number', 'Pickup Address', 'Pickup Date/Time', 'Dropoff Address', 'Dropoff Date/Time', 'RC Amount'],
        'invoice': ['Date', 'Invoice Number', 'RC Number', 'Load Number', 'Dispatcher', 'Broker/Shipper', 'Pickup', 'Dropoff', 'Miles', 'DH Miles', 'Total Miles', 'Amount RC', 'Quick Pay %', 'Amount Received'],
        'rlp': ['Date', 'RLP Number', 'Date Received', 'Invoice Number', 'RC Number', 'Load Number', 'Dispatcher', 'Broker/Shipper', 'Total Miles', 'Amount RC', 'Quick Pay %', 'Amount Received']
    };
    
    return headers[documentType] || ['Date', 'Title', 'Amount', 'Driver Name'];
}

function getExcelRowForDocument(doc, documentType) {
    const date = doc.created_at ? new Date(doc.created_at).toLocaleDateString() : (doc.upload_date ? new Date(doc.upload_date).toLocaleDateString() : '');
    
    const formatValue = (value) => value || '';
    
    if (documentType === 'rc') {
        return [date, 
                formatValue(doc.load_number), 
                formatValue(doc.dispatcher), 
                formatValue(doc.broker_shipper), 
                formatValue(doc.pickup_address), 
                formatValue(doc.pickup_datetime), 
                formatValue(doc.dropoff_address), 
                formatValue(doc.dropoff_datetime), 
                formatValue(doc.miles), 
                formatValue(doc.dh_miles), 
                formatValue(doc.total_miles), 
                formatValue(doc.rate_per_mile), 
                parseFloat(doc.amount || 0), 
                formatValue(doc.document_name)];
    }
    
    if (documentType === 'bol') {
        return [date, 
                formatValue(doc.bol_number), 
                formatValue(doc.rc_number), 
                formatValue(doc.load_number), 
                formatValue(doc.dispatcher), 
                formatValue(doc.broker_shipper), 
                formatValue(doc.pickup_address), 
                formatValue(doc.pickup_datetime), 
                formatValue(doc.dropoff_address), 
                formatValue(doc.dropoff_datetime), 
                formatValue(doc.miles), 
                formatValue(doc.dh_miles),
                formatValue(doc.document_name)];
    }
    
    if (documentType === 'pod') {
        return [date, 
                formatValue(doc.rc_number), 
                formatValue(doc.load_number), 
                formatValue(doc.dispatcher), 
                formatValue(doc.broker_shipper), 
                formatValue(doc.pickup_address), 
                formatValue(doc.pickup_datetime), 
                formatValue(doc.dropoff_address), 
                formatValue(doc.dropoff_datetime), 
                formatValue(doc.miles),
                formatValue(doc.document_name)];
    }
    
    if (documentType === 'dispatcher') {
        return [date, 
                formatValue(doc.dispatcher_company), 
                formatValue(doc.phone_number), 
                formatValue(doc.email), 
                formatValue(doc.rc_number), 
                formatValue(doc.load_number), 
                formatValue(doc.broker_shipper), 
                formatValue(doc.pickup_address), 
                formatValue(doc.pickup_datetime), 
                formatValue(doc.dropoff_address), 
                formatValue(doc.dropoff_datetime), 
                parseFloat(doc.rc_amount || 0), 
                formatValue(doc.dispatcher_percentage), 
                parseFloat(doc.dispatcher_amount || 0)];
    }
    
    if (documentType === 'fuel') {
        return [date, 
                formatValue(doc.receipt_number), 
                formatValue(doc.receipt_date), 
                parseFloat(doc.amount || 0), 
                formatValue(doc.rc_number), 
                formatValue(doc.load_number), 
                formatValue(doc.pickup_address), 
                formatValue(doc.pickup_datetime), 
                formatValue(doc.dropoff_address), 
                formatValue(doc.dropoff_datetime), 
                parseFloat(doc.rc_amount || 0)];
    }
    
    if (documentType === 'invoice') {
        return [date, 
                formatValue(doc.invoice_number), 
                formatValue(doc.rc_number), 
                formatValue(doc.load_number), 
                formatValue(doc.dispatcher), 
                formatValue(doc.broker_shipper), 
                formatValue(doc.pickup_address), 
                formatValue(doc.dropoff_address), 
                formatValue(doc.miles), 
                formatValue(doc.dh_miles), 
                formatValue(doc.total_miles), 
                parseFloat(doc.amount || 0), 
                formatValue(doc.quickpay_percentage), 
                parseFloat(doc.amount_received || 0)];
    }
    
    if (documentType === 'rlp') {
        return [date, 
                formatValue(doc.rlp_number), 
                formatValue(doc.date_received), 
                formatValue(doc.invoice_number), 
                formatValue(doc.rc_number), 
                formatValue(doc.load_number), 
                formatValue(doc.dispatcher), 
                formatValue(doc.broker_shipper), 
                formatValue(doc.total_miles), 
                parseFloat(doc.amount || 0), 
                formatValue(doc.quickpay_percentage), 
                parseFloat(doc.amount_received || 0)];
    }
    
    // Default fallback
    return [date, doc.title || '', doc.driver_name || '', parseFloat(doc.amount || 0)];
}

function getPDFHeadersForType(documentType) {
    const headers = {
        'rc': ['Date', 'Load Number', 'Dispatcher', 'Broker/Shipper', 'Pickup Address', 'Pickup Date/Time', 'Dropoff Address', 'Dropoff Date/Time', 'Miles', 'DH Miles', 'Total Miles', 'Rate/Mile', 'Amount', 'Document Name'],
        'bol': ['Date', 'BOL Number', 'RC Number', 'Load Number', 'Dispatcher', 'Broker/Shipper', 'Pickup Address', 'Pickup Date/Time', 'Dropoff Address', 'Dropoff Date/Time', 'Miles', 'DH Miles', 'Document Name'],
        'pod': ['Date', 'RC Number', 'Load Number', 'Dispatcher', 'Broker/Shipper', 'Pickup Address', 'Pickup Date/Time', 'Dropoff Address', 'Dropoff Date/Time', 'Miles', 'Document Name'],
        'dispatcher': ['Date', 'Dispatcher Company', 'Phone Number', 'Email', 'RC Number', 'Load Number', 'Broker/Shipper', 'Pickup Address', 'Pickup Date/Time', 'Dropoff Address', 'Dropoff Date/Time', 'RC Amount', 'Dispatcher %', 'Dispatcher Amount'],
        'fuel': ['Date', 'Receipt Number', 'Receipt Date', 'Amount', 'RC Number', 'Load Number', 'Pickup Address', 'Pickup Date/Time', 'Dropoff Address', 'Dropoff Date/Time', 'RC Amount'],
        'invoice': ['Date', 'Invoice Number', 'RC Number', 'Load Number', 'Dispatcher', 'Broker/Shipper', 'Pickup', 'Dropoff', 'Miles', 'DH Miles', 'Total Miles', 'Amount RC', 'Quick Pay %', 'Amount Received'],
        'rlp': ['Date', 'RLP Number', 'Date Received', 'Invoice Number', 'RC Number', 'Load Number', 'Dispatcher', 'Broker/Shipper', 'Total Miles', 'Amount RC', 'Quick Pay %', 'Amount Received']
    };
    
    return headers[documentType] || ['Date', 'Title', 'Amount', 'Driver Name'];
}

function getPDFRowsForDocument(doc) {
    const date = doc.created_at ? new Date(doc.created_at).toLocaleDateString() : (doc.upload_date ? new Date(doc.upload_date).toLocaleDateString() : '');
    
    const formatValue = (value) => value || '';
    
    if (doc.document_type === 'rc') {
        return [date, 
                formatValue(doc.load_number), 
                formatValue(doc.dispatcher), 
                formatValue(doc.broker_shipper), 
                formatValue(doc.pickup_address), 
                formatValue(doc.pickup_datetime), 
                formatValue(doc.dropoff_address), 
                formatValue(doc.dropoff_datetime), 
                formatValue(doc.miles), 
                formatValue(doc.dh_miles), 
                formatValue(doc.total_miles), 
                formatValue(doc.rate_per_mile), 
                `$${parseFloat(doc.amount || 0).toFixed(2)}`, 
                formatValue(doc.document_name)];
    }
    
    if (doc.document_type === 'bol') {
        return [date, 
                formatValue(doc.bol_number), 
                formatValue(doc.rc_number), 
                formatValue(doc.load_number), 
                formatValue(doc.dispatcher), 
                formatValue(doc.broker_shipper), 
                formatValue(doc.pickup_address), 
                formatValue(doc.pickup_datetime), 
                formatValue(doc.dropoff_address), 
                formatValue(doc.dropoff_datetime), 
                formatValue(doc.miles), 
                formatValue(doc.dh_miles),
                formatValue(doc.document_name)];
    }
    
    if (doc.document_type === 'pod') {
        return [date, 
                formatValue(doc.rc_number), 
                formatValue(doc.load_number), 
                formatValue(doc.dispatcher), 
                formatValue(doc.broker_shipper), 
                formatValue(doc.pickup_address), 
                formatValue(doc.pickup_datetime), 
                formatValue(doc.dropoff_address), 
                formatValue(doc.dropoff_datetime), 
                formatValue(doc.miles),
                formatValue(doc.document_name)];
    }
    
    if (doc.document_type === 'dispatcher') {
        return [date, 
                formatValue(doc.dispatcher_company), 
                formatValue(doc.phone_number), 
                formatValue(doc.email), 
                formatValue(doc.rc_number), 
                formatValue(doc.load_number), 
                formatValue(doc.broker_shipper), 
                formatValue(doc.pickup_address), 
                formatValue(doc.pickup_datetime), 
                formatValue(doc.dropoff_address), 
                formatValue(doc.dropoff_datetime), 
                `$${parseFloat(doc.rc_amount || 0).toFixed(2)}`, 
                formatValue(doc.dispatcher_percentage), 
                `$${parseFloat(doc.dispatcher_amount || 0).toFixed(2)}`];
    }
    
    if (doc.document_type === 'fuel') {
        return [date, 
                formatValue(doc.receipt_number), 
                formatValue(doc.receipt_date), 
                `$${parseFloat(doc.amount || 0).toFixed(2)}`, 
                formatValue(doc.rc_number), 
                formatValue(doc.load_number), 
                formatValue(doc.pickup_address), 
                formatValue(doc.pickup_datetime), 
                formatValue(doc.dropoff_address), 
                formatValue(doc.dropoff_datetime), 
                `$${parseFloat(doc.rc_amount || 0).toFixed(2)}`];
    }
    
    if (doc.document_type === 'invoice') {
        return [date, 
                formatValue(doc.invoice_number), 
                formatValue(doc.rc_number), 
                formatValue(doc.load_number), 
                formatValue(doc.dispatcher), 
                formatValue(doc.broker_shipper), 
                formatValue(doc.pickup_address), 
                formatValue(doc.dropoff_address), 
                formatValue(doc.miles), 
                formatValue(doc.dh_miles), 
                formatValue(doc.total_miles), 
                `$${parseFloat(doc.amount || 0).toFixed(2)}`, 
                formatValue(doc.quickpay_percentage), 
                `$${parseFloat(doc.amount_received || 0).toFixed(2)}`];
    }
    
    if (doc.document_type === 'rlp') {
        return [date, 
                formatValue(doc.rlp_number), 
                formatValue(doc.date_received), 
                formatValue(doc.invoice_number), 
                formatValue(doc.rc_number), 
                formatValue(doc.load_number), 
                formatValue(doc.dispatcher), 
                formatValue(doc.broker_shipper), 
                formatValue(doc.total_miles), 
                `$${parseFloat(doc.amount || 0).toFixed(2)}`, 
                formatValue(doc.quickpay_percentage), 
                `$${parseFloat(doc.amount_received || 0).toFixed(2)}`];
    }
    
    // Default fallback
    return [date, doc.title || '', doc.driver_name || '', `$${parseFloat(doc.amount || 0).toFixed(2)}`];
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function updateDocumentCount(count) {
    const countElement = document.getElementById('document-count');
    if (countElement) {
        countElement.textContent = `${count} document${count !== 1 ? 's' : ''}`;
    }
}

function updateTotalAmount(documents) {
    const total = documents.reduce((sum, doc) => sum + (parseFloat(doc.amount) || 0), 0);
    const totalElement = document.getElementById('total-display');
    if (totalElement) {
        totalElement.textContent = `Total: $${total.toFixed(2)}`;
    }
}

function exportDocumentPDF(docId) {
    const doc = documents.find(d => d.id === docId);
    if (!doc) return;
    
    const type = documentTypes.find(t => t.id === doc.document_type) || { name: doc.document_type || 'Unknown', color: '#3b82f6', icon: 'fa-file' };
    
    // Create PDF content following documate-pro approach
    const { jsPDF } = window.jspdf;
    const pdf_doc = new jsPDF({ orientation: 'landscape' });
    
    // Title and metadata
    pdf_doc.setFontSize(16);
    pdf_doc.setTextColor(16, 185, 129);
    pdf_doc.text(`${type.name} Document`, 14, 22);
    
    pdf_doc.setFontSize(9);
    pdf_doc.setTextColor(100, 116, 139);
    pdf_doc.text(`Generated: ${new Date().toLocaleDateString()} · 1 document(s)`, 14, 32);
    
    // Calculate total amount
    const totalAmount = parseFloat(doc.amount || 0);
    pdf_doc.text(`Total Amount: $${totalAmount.toFixed(2)}`, 14, 40);
    
    // Prepare headers and data based on document type
    const headers = getPDFHeadersForType(doc.document_type);
    const rows = getPDFRowsForDocument(doc);
    
    // Create table using autoTable
    pdf_doc.autoTable({
        startY: 50,
        head: [headers],
        body: rows,
        theme: 'grid',
        headStyles: { fillColor: [16, 185, 129], textColor: [255, 255, 255], fontStyle: 'bold', fontSize: 7 },
        styles: { fontSize: 6, cellPadding: 1.5, overflow: 'linebreak' },
        margin: { top: 50 },
        columnStyles: { 0: { cellWidth: 20 } } // date column fixed width
    });
    
    // Generate filename
    const filename = `${doc.document_type}_${new Date().toISOString().slice(0,10)}.pdf`;
    pdf_doc.save(filename);
}
