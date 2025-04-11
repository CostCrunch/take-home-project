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
file-upload-service/
├── app/
│   ├── api/
│   │   └── upload/
│   │       └── route.ts
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   └── UploadDialog.tsx
│   ├── package.json
│   └── README.md
```

### Setup Instructions

1. Install dependencies:

   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

The application will run on `http://localhost:3000` with the API endpoint at `/api/upload`.

### Your Tasks

#### 1. Fix the Bugs

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

#### 2. Write Tests

- Implement unit tests for the API endpoint
- Add integration tests for file upload functionality
- Test error handling and edge cases
- Aim for good test coverage

### Time Allocation

- Expected time: 1-2 hours

### Evaluation Criteria

- Test coverage and quality
- Bug identification and fixes
- Code quality and documentation
- Problem-solving approach
- Ability to work with AI-assisted development tools

## Part 2: Technical Interview

### Format

- 45-60 minute Zoom call

### Structure

1. **Introduction and Background (15 minutes)**

   - Brief introduction
   - Discussion of your experience
   - Questions about your interest in the role

2. **System Design Discussion (45 minutes)**
   - Infrastructure design
   - Database architecture
   - Scalability considerations
   - Security best practices

### Topics to Prepare

- Cloud infrastructure (AWS/GCP/Azure)
- Database design and optimization
- API design and implementation
- Security best practices
- Scalability patterns
- Monitoring and observability

## Technology Stack

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- React Dropzone

## Questions?

If you have any questions about the process, please don't hesitate to reach out to alex@costcrunch.ai

Good luck!
