require("dotenv").config();
const express = require("express");
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');

const app = express();

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static('public'));

// File upload configuration
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadDir = 'uploads/';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  },
  fileFilter: function (req, file, cb) {
    const allowedTypes = ['.pdf', '.jpg', '.jpeg', '.png'];
    const fileExt = path.extname(file.originalname).toLowerCase();
    if (allowedTypes.includes(fileExt)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only PDF, JPG, JPEG, PNG are allowed.'));
    }
  }
});

// Routes
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get("/status", (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Submit application with file uploads
app.post("/submit", upload.array('documents', 10), async (req, res) => {
  try {
    const applicationData = JSON.parse(req.body.applicationData);
    const files = req.files || [];

    // Generate unique UUID for this application
    const applicationId = uuidv4();
    
    // Add timestamp
    const timestamp = new Date().toISOString();

    console.log(`New application received: ${applicationId}`);
    console.log(`Applicant: ${applicationData.firstName} ${applicationData.lastName}`);
    console.log(`Company: ${applicationData.companyName}`);
    console.log(`Amount: $${applicationData.amount}`);
    console.log(`Files uploaded: ${files.length}`);

    // Prepare data for admin API
    const adminApplicationData = {
      companyName: applicationData.companyName || 'Unknown',
      companyNumber: applicationData.companyNumber || 'Unknown',
      businessType: applicationData.businessType || 'ltd',
      industry: applicationData.industry || 'other',
      firstName: applicationData.firstName || 'Unknown',
      lastName: applicationData.lastName || 'Unknown',
      email: applicationData.email || 'unknown@example.com',
      phone: applicationData.phone || '000-000-0000',
      address: applicationData.address || 'Not provided',
      amount: parseFloat(applicationData.amount) || 0,
      loanPurpose: applicationData.loanPurpose || 'working_capital',
      annualRevenue: parseFloat(applicationData.annualRevenue) || 0,
      yearsInBusiness: parseInt(applicationData.yearsInBusiness) || 0
    };

    console.log('Sending to Admin API:', adminApplicationData);

    // Send to Admin API
    let adminResponse;
    let adminSuccess = false;
    try {
      adminResponse = await axios.post(
        'http://localhost:8005/api/applications', 
        adminApplicationData,
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 10000
        }
      );
      console.log(`Application sent to Admin API:`, adminResponse.data);
      adminSuccess = true;
    } catch (adminError) {
      console.error('Failed to send to Admin API:', adminError.message);
      if (adminError.response) {
        console.error('Admin API response status:', adminError.response.status);
        console.error('Admin API response data:', adminError.response.data);
      } else if (adminError.request) {
        console.error('No response received from Admin API');
      }
    }

    // Store files locally
    const fileDetails = files.map(file => ({
      filename: file.filename,
      originalName: file.originalname,
      path: file.path,
      size: file.size
    }));

    // Send success response
    res.json({
      success: true,
      message: "Application submitted successfully",
      applicationId: applicationId,
      adminApplicationId: adminResponse?.data?.application_id || applicationId,
      submittedAt: timestamp,
      filesReceived: files.length,
      adminAPISuccess: adminSuccess,
      adminAPIUrl: 'http://localhost:8005',
      nextSteps: [
        "Initial review by our team",
        "Document verification", 
        "AI-powered risk assessment",
        "Final decision within 24 hours"
      ]
    });

  } catch (err) {
    console.error("Error in submit endpoint:", err.message);
    res.status(500).json({
      success: false,
      message: "Failed to submit application. Please try again.",
      error: err.message
    });
  }
});

// Application status check API
app.get("/api/application/:id", async (req, res) => {
  try {
    const applicationId = req.params.id;
    
    // In a real application, you would query your database here
    const status = await checkApplicationStatus(applicationId);
    
    res.json({
      applicationId: applicationId,
      status: status.status,
      decision: status.decision,
      progress: status.progress,
      lastUpdated: status.lastUpdated,
      nextSteps: status.nextSteps,
      estimatedCompletion: status.estimatedCompletion
    });
  } catch (err) {
    res.status(404).json({
      success: false,
      message: "Application not found"
    });
  }
});

async function checkApplicationStatus(applicationId) {
  // Mock status check - replace with actual database query
  const statuses = [
    { status: 'submitted', decision: null, progress: 25, message: 'Application received' },
    { status: 'under_review', decision: null, progress: 50, message: 'Under review' },
    { status: 'ai_analysis', decision: null, progress: 75, message: 'AI analysis in progress' },
    { status: 'decision_ready', decision: 'pending_review', progress: 100, message: 'Decision ready' }
  ];
  
  // Simple logic to show progressing status based on application ID
  const startTime = parseInt(applicationId.split('-')[0], 16) || Date.now();
  const elapsed = Date.now() - startTime;
  
  // Change status based on elapsed time (for demo purposes)
  let statusIndex;
  if (elapsed < 5000) {
    statusIndex = 0;
  } else if (elapsed < 15000) {
    statusIndex = 1;
  } else if (elapsed < 25000) {
    statusIndex = 2;
  } else {
    statusIndex = 3;
  }

  const status = statuses[statusIndex];
  const estimatedCompletion = new Date(Date.now() + (30000 - elapsed));
  
  return {
    status: status.status,
    decision: status.decision,
    progress: status.progress,
    message: status.message,
    lastUpdated: new Date().toISOString(),
    nextSteps: getNextSteps(status.status),
    estimatedCompletion: estimatedCompletion.toISOString()
  };
}

function getNextSteps(status) {
  const steps = {
    'submitted': 'Your application has been received and is in the initial review queue.',
    'under_review': 'Our team is currently reviewing your application and documents.',
    'ai_analysis': 'Our AI system is analyzing your business data and financial information.',
    'decision_ready': 'A decision has been made and you will be notified shortly.'
  };
  return steps[status] || 'Your application is being processed.';
}

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({ 
    status: "OK", 
    timestamp: new Date().toISOString(),
    service: "Loan Application Client Dashboard",
    version: "3.0.0"
  });
});

// Test Admin API connection endpoint
app.get("/api/test-admin-connection", async (req, res) => {
  try {
    console.log('Testing connection to Admin API...');
    const response = await axios.get('http://localhost:8005/health', { timeout: 5000 });
    res.json({
      success: true,
      message: "Admin API is reachable",
      adminAPIStatus: response.data
    });
  } catch (error) {
    res.json({
      success: false,
      message: "Admin API is not reachable",
      error: error.message
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        success: false,
        message: 'File too large. Maximum size is 10MB.'
      });
    }
  }
  res.status(500).json({
    success: false,
    message: error.message
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Client Dashboard running at http://localhost:${PORT}`);
  console.log(`Upload directory: ${path.join(__dirname, 'uploads')}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`Admin API connection test: http://localhost:${PORT}/api/test-admin-connection`);
  console.log(`Ready to accept loan applications`);
  console.log(`Applications will be sent to: http://localhost:8005/api/applications`);
});