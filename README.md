# Part-Time Engineer Interview Project

## Overview

This is part of a two-stage interview process for a part-time engineering position. The process consists of this take-home project followed by a technical interview.

## Part 1: Take-Home Project

### Getting Started

1. Clone this repository
2. Create a private repository on your GitHub
3. Add @alexrpreston as a contributor
4. Complete the tasks below
5. Submit a PR with your changes
6. Email alex@costcrunch.ai with a link to your PR

### Project Structure

```
costcrunch-interview/
├── backend/
│   ├── routes.py           # FastAPI routes with mock data
│   ├── tests/
│   │   └── test_sample.py  # Sample test file
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── components/
│   │   └── UploadDialog.tsx
│   ├── app/
│   │   └── page.tsx
│   └── package.json
└── README.md
```

### Setup Instructions

#### Backend Setup

1. Create and activate a Python virtual environment:

   ```bash
   # On macOS/Linux:
   python -m venv venv
   source venv/bin/activate

   # On Windows:
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install Python dependencies:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Run the FastAPI server:
   ```bash
   uvicorn routes:app --reload --port 8000
   ```

The backend will run on `http://localhost:8000`. You can view the API documentation at `http://localhost:8000/docs`.

#### Frontend Setup

1. Install Node.js dependencies:

   ```bash
   cd frontend
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will run on `http://localhost:3000`.

### Your Tasks

#### 1. Write API Tests

The backend includes 15 API endpoints that need test coverage. A sample test file (`test_sample.py`) is provided showing how to test the `/vendors/` endpoint. Your task is to:

1. Study the sample test
2. Write similar tests for all other endpoints
3. Follow the testing patterns shown
4. Consider all test cases mentioned in the comments

Required endpoints to test:

- Vendor management (GET /vendors/, GET /vendors/{id})
- Invoice handling (GET /invoices/, GET /invoices/{id})
- Project management (GET /projects/, GET /projects/{id}/invoices)
- Basic analytics (GET /analytics/monthly-spend)

Optional endpoints to test:

- Material tracking (GET /materials/)
- Price history (GET /materials/price-history/{id})
- Payment terms (GET /vendors/{id}/payment-terms)
- Stock management (GET /materials/low-stock)
- Advanced analytics (spend-by-vendor, spend-by-category)

For each endpoint, remember to test:

- Successful responses
- Authentication requirements
- Error cases (404, invalid params, etc.)
- Query parameter variations (required)
- Response data structure and content (required)
- Edge cases and boundary testing (optional)
- Performance testing (optional)

#### 2. Fix Frontend Bugs

The `UploadDialog` component contains several intentional bugs that need to be fixed:

Required fixes:

1. **Critical Issues:**
   - File size checks
   - Error handling for network issues
   - Progress tracking
   - Basic error messages

Optional improvements:

1. **Additional Validation:**

   - File type validation
   - Multiple file handling
   - Duplicate file detection

2. **UI Enhancements:**

   - File removal functionality
   - Progress display
   - Error clearing functionality
   - Disabled state during upload

3. **Advanced Features:**
   - Drag and drop improvements
   - Upload cancellation
   - Retry mechanism
   - Chunked uploads

### Time Allocation

- Expected time: 1-2 hours
  - Required tasks: ~1 hour
  - Optional improvements: ~1 hour

### Evaluation Criteria

- Test coverage and quality
- Bug identification and fixes
- Code quality and documentation
- Problem-solving approach
- Ability to work with AI-assisted development tools
