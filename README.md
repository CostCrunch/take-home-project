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
│   │   └── route.ts
│   │   └── page.tsx
│   │   └── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   └── UploadDialog.tsx
│   ├── package.json
│   └── README.md
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

The endpoints to test include:

- Vendor management
- Material tracking
- Invoice handling
- Project management
- Analytics endpoints
- Price history
- Payment terms
- Stock management

For each endpoint, remember to test:

- Successful responses
- Authentication requirements
- Error cases (404, invalid params, etc.)
- Query parameter variations
- Response data structure and content

#### 2. Fix Frontend Bugs

The `UploadDialog` component contains several intentional bugs that need to be fixed:

1. **File Validation Issues:**

   - No file type validation
   - No file size checks
   - No file type restrictions in dropzone
   - No multiple file handling configuration

2. **UI/UX Issues:**

   - No file removal functionality
   - No proper progress tracking
   - Inconsistent state updates
   - No cleanup after completion
   - No file list display
   - No progress display
   - No error clearing functionality
   - No disabled state during upload

3. **Error Handling Issues:**
   - No proper error handling for network issues
   - Generic error messages
   - Missing error states

### Evaluation Criteria

- Test coverage and quality
- Bug identification and fixes
- Code quality and documentation
- Problem-solving approach
- Ability to work with AI-assisted development tools
