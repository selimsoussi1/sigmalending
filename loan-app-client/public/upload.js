// File upload functionality
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    
    let uploadedFiles = [];
    
    // Drag and drop functionality
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        handleFiles(files);
    });
    
    // File input change
    fileInput.addEventListener('change', function(e) {
        handleFiles(e.target.files);
    });
    
    function handleFiles(files) {
        for (let file of files) {
            if (validateFile(file)) {
                addFileToList(file);
            }
        }
    }
    
    function validateFile(file) {
        const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
        const maxSize = 10 * 1024 * 1024; // 10MB
        
        if (!allowedTypes.includes(file.type)) {
            alert('Please upload only PDF, JPG, or PNG files.');
            return false;
        }
        
        if (file.size > maxSize) {
            alert('File size must be less than 10MB.');
            return false;
        }
        
        return true;
    }
    
    function addFileToList(file) {
        const fileId = Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-name">
                <span>📄</span>
                <span>${file.name}</span>
            </div>
            <div class="file-info">
                <span class="file-size">${formatFileSize(file.size)}</span>
                <button type="button" class="remove-file" onclick="removeFile('${fileId}')">✕</button>
            </div>
        `;
        
        fileItem.dataset.fileId = fileId;
        fileList.appendChild(fileItem);
        
        uploadedFiles.push({
            id: fileId,
            file: file
        });
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Make removeFile function global
    window.removeFile = function(fileId) {
        const fileItem = document.querySelector(`[data-file-id="${fileId}"]`);
        if (fileItem) {
            fileItem.remove();
        }
        
        uploadedFiles = uploadedFiles.filter(file => file.id !== fileId);
    };
});