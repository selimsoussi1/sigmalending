document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('lendingForm');
  const submitBtn = document.getElementById('submitBtn');
  const btnText = document.querySelector('.btn-text');
  const btnLoader = document.querySelector('.btn-loader');
  const successMessage = document.getElementById('successMessage');
  const errorMessage = document.getElementById('errorMessage');
  const statusPage = document.getElementById('statusPage');
  const introSection = document.getElementById('introSection');
  
  // Check if we should show status page
  const urlParams = new URLSearchParams(window.location.search);
  const appId = urlParams.get('app');
  if (appId) {
    showStatusPage(appId);
  }
  
  // Form validation rules
  const validationRules = {
    companyName: {
      required: true,
      minLength: 2,
      message: 'Company name is required'
    },
    companyNumber: {
      required: true,
      minLength: 2,
      message: 'Company registration number is required'
    },
    firstName: {
      required: true,
      minLength: 2,
      pattern: /^[a-zA-Z\s'-]+$/,
      message: 'First name must contain only letters, spaces, hyphens, and apostrophes'
    },
    lastName: {
      required: true,
      minLength: 2,
      pattern: /^[a-zA-Z\s'-]+$/,
      message: 'Last name must contain only letters, spaces, hyphens, and apostrophes'
    },
    email: {
      required: true,
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      message: 'Please enter a valid email address'
    },
    phone: {
      required: true,
      pattern: /^[\+]?[0-9\s\-\(\)]{10,}$/,
      message: 'Please enter a valid phone number'
    },
    address: {
      required: true,
      minLength: 10,
      message: 'Please enter a complete business address'
    },
    amount: {
      required: true,
      min: 1000,
      max: 10000000,
      message: 'Amount must be between $1,000 and $10,000,000'
    },
    annualRevenue: {
      required: true,
      min: 0,
      message: 'Please enter annual revenue'
    },
    yearsInBusiness: {
      required: true,
      min: 0,
      max: 50,
      message: 'Please enter years in business'
    },
    consent: {
      required: true,
      message: 'You must agree to the Privacy and Cookie Policy'
    }
  };

  // Real-time validation
  Object.keys(validationRules).forEach(fieldName => {
    const field = document.getElementById(fieldName);
    if (field) {
      field.addEventListener('blur', () => validateField(fieldName));
      field.addEventListener('input', () => clearError(fieldName));
    }
  });

  // Form submission
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Validate all fields
    let isValid = true;
    Object.keys(validationRules).forEach(fieldName => {
      if (!validateField(fieldName)) {
        isValid = false;
      }
    });

    if (!isValid) {
      showError('Please correct the errors above');
      return;
    }

    // Show loading state
    setLoadingState(true);
    hideMessages();

    try {
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());
      
      // Get uploaded files
      const fileInput = document.getElementById('fileInput');
      const files = Array.from(fileInput.files);
      
      // Create FormData for file upload
      const uploadData = new FormData();
      uploadData.append('applicationData', JSON.stringify(data));
      
      // Append files
      files.forEach(file => {
        uploadData.append('documents', file);
      });

      const response = await fetch('/submit', {
        method: 'POST',
        body: uploadData
      });

      const result = await response.json();

      if (result.success) {
        showSuccess(result);
        form.reset();
        clearFileList();
        
        // Track successful submission
        console.log('Application submitted successfully:', result.applicationId);
      } else {
        showError(result.message || 'Submission failed. Please try again.');
      }
    } catch (error) {
      console.error('Submission error:', error);
      showError('Network error. Please check your connection and try again.');
    } finally {
      setLoadingState(false);
    }
  });

  // Validation functions
  function validateField(fieldName) {
    const field = document.getElementById(fieldName);
    const rules = validationRules[fieldName];
    
    if (!field || !rules) return true;

    let isValid = true;
    let errorMessage = '';

    const value = field.type === 'checkbox' ? field.checked : field.value.trim();

    // Required validation
    if (rules.required && (!value || (field.type === 'checkbox' && !field.checked))) {
      isValid = false;
      errorMessage = field.type === 'checkbox' ? rules.message : `${fieldName.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())} is required`;
    }
    
    // Pattern validation
    else if (value && rules.pattern && !rules.pattern.test(value)) {
      isValid = false;
      errorMessage = rules.message;
    }
    
    // Length validation
    else if (value && rules.minLength && value.length < rules.minLength) {
      isValid = false;
      errorMessage = `Must be at least ${rules.minLength} characters long`;
    }
    
    // Number validation
    else if (field.type === 'number' && value) {
      const numValue = parseFloat(value);
      if (rules.min && numValue < rules.min) {
        isValid = false;
        errorMessage = `Minimum amount is $${rules.min.toLocaleString()}`;
      } else if (rules.max && numValue > rules.max) {
        isValid = false;
        errorMessage = `Maximum amount is $${rules.max.toLocaleString()}`;
      }
    }

    showFieldError(fieldName, isValid ? '' : errorMessage);
    return isValid;
  }

  function showFieldError(fieldName, message) {
    const errorElement = document.getElementById(fieldName + 'Error');
    const field = document.getElementById(fieldName);
    
    if (errorElement) {
      errorElement.textContent = message;
    }
    
    if (field) {
      if (message) {
        field.style.borderColor = '#ef4444';
        field.style.backgroundColor = '#fef2f2';
      } else {
        field.style.borderColor = '#d1d5db';
        field.style.backgroundColor = 'white';
      }
    }
  }

  function clearError(fieldName) {
    showFieldError(fieldName, '');
  }

  function setLoadingState(isLoading) {
    submitBtn.disabled = isLoading;
    
    if (isLoading) {
      btnText.style.display = 'none';
      btnLoader.style.display = 'inline-block';
    } else {
      btnText.style.display = 'inline';
      btnLoader.style.display = 'none';
    }
  }

  function showSuccess(result) {
    successMessage.style.display = 'block';
    document.getElementById('applicationId').textContent = result.applicationId;
    
    // Hide form and intro
    form.style.display = 'none';
    introSection.style.display = 'none';
    
    // Scroll to success message
    successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function showError(message) {
    errorMessage.style.display = 'block';
    document.getElementById('errorText').textContent = message;
    
    // Scroll to error message
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function hideMessages() {
    successMessage.style.display = 'none';
    errorMessage.style.display = 'none';
  }

  function showStatusPage(applicationId) {
    form.style.display = 'none';
    introSection.style.display = 'none';
    successMessage.style.display = 'none';
    statusPage.style.display = 'block';
    
    document.getElementById('statusAppId').textContent = applicationId;
    document.getElementById('submittedTime').textContent = new Date().toLocaleString();
    
    // Simulate status updates
    simulateStatusProgress();
  }

  function simulateStatusProgress() {
    setTimeout(() => {
      document.getElementById('reviewStep').classList.add('active');
    }, 2000);
    
    setTimeout(() => {
      document.getElementById('aiStep').classList.add('active');
    }, 5000);
    
    setTimeout(() => {
      document.getElementById('decisionStep').classList.add('active');
    }, 8000);
  }

  function checkStatus() {
    // In a real app, this would make an API call
    alert('Status refreshed! We\'ll notify you when there\'s an update.');
  }

  // Phone number formatting
  const phoneInput = document.getElementById('phone');
  if (phoneInput) {
    phoneInput.addEventListener('input', function() {
      let value = this.value.replace(/\D/g, '');
      let formatted = '';
      
      if (value.length > 0) {
        if (value.length <= 3) {
          formatted = `(${value}`;
        } else if (value.length <= 6) {
          formatted = `(${value.slice(0, 3)}) ${value.slice(3)}`;
        } else {
          formatted = `(${value.slice(0, 3)}) ${value.slice(3, 6)}-${value.slice(6, 10)}`;
        }
      }
      
      this.value = formatted;
    });
  }

  // Progress indication based on form completion
  function updateProgress() {
    const requiredFields = Object.keys(validationRules).filter(field => 
      validationRules[field].required && field !== 'consent'
    );
    
    let completedFields = 0;
    requiredFields.forEach(fieldName => {
      const field = document.getElementById(fieldName);
      if (field && field.value.trim()) {
        completedFields++;
      }
    });

    // Add consent check
    const consentField = document.getElementById('consent');
    if (consentField && consentField.checked) {
      completedFields++;
    }

    const progressPercentage = (completedFields / (requiredFields.length + 1)) * 100;
    const progressFill = document.getElementById('progressFill');
    if (progressFill) {
      progressFill.style.width = `${progressPercentage}%`;
    }

    const progressText = document.getElementById('progressText');
    if (progressText) {
      if (progressPercentage === 100) {
        progressText.textContent = 'Ready to submit!';
        progressText.style.color = '#10b981';
      } else {
        progressText.textContent = `${Math.round(progressPercentage)}% completed`;
        progressText.style.color = '#6b7280';
      }
    }
  }

  // Update progress on input changes
  const inputs = document.querySelectorAll('input, select, textarea');
  inputs.forEach(input => {
    input.addEventListener('input', updateProgress);
    input.addEventListener('change', updateProgress);
  });

  // Initial progress update
  updateProgress();
});

function clearFileList() {
  const fileList = document.getElementById('fileList');
  fileList.innerHTML = '';
  const fileInput = document.getElementById('fileInput');
  fileInput.value = '';
}