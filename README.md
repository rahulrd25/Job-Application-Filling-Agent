# JobFill Pro: Agentic Job Application Assistant

JobFill Pro is an intelligent browser extension designed to automate the repetitive aspects of job applications. Utilizing LLMs (Large Language Models) via the Groq API, the system contextually parses job descriptions and generates technical, professional responses tailored to a user's specific experience.

The system features a multi-tenant architecture with agentic CV parsing, allowing users to initialize their profiles by simply uploading a PDF resume.

## Core Features

*   **Agentic CV Onboarding**: Automatic extraction of professional experience, skills, and contact details from PDF resumes using Llama-3-70B.
*   **Contextual Autofill**: Real-time analysis of job boards to identify company names, roles, and application requirements.
*   **Intelligent Response Generation**: Technical, first-person answers for custom application questions, generated without AI artifacts or placeholders.
*   **Privacy-First Architecture**: Localized user data storage with support for multi-user browser environments.
*   **Auto-Consent**: Automated detection and verification of privacy and GDPR compliance checkboxes.

## System Architecture

### Backend (Python/FastAPI)
The backend acts as the orchestration layer between the browser extension and the LLM. It handles:
*   PDF text extraction and structured parsing.
*   User session management.
*   Prompt engineering and model fallback logic (Llama 3.3 70B & 3.1 8B).

### Frontend (React/TypeScript/Vite)
A compact browser extension built with modern UI principles:
*   A Cyber-Yellow high-contrast theme for engineering professionality.
*   Content scripts for DOM manipulation and form discovery.
*   Vite-optimized production builds.

## Installation & Setup

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Groq API Key (Obtainable at [console.groq.com](https://console.groq.com))

### 1. Backend Configuration
Navigate to the backend directory and set up the environment:
```bash
cd backend
uv venv
source .venv/bin/activate  # On macOS/Linux
uv pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:
```env
GROQ_API_KEY=your_api_key_here
```

Start the API server:
```bash
uv run uvicorn app.main:app --reload
```

### 2. Extension Compilation
Navigate to the extension directory and build the production assets:
```bash
cd extension
npm install
npm run build
```

### 3. Chrome Installation
1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable "Developer mode" in the top-right corner.
3. Click "Load unpacked".
4. Select the `extension/dist` folder from this repository.

## Usage Workflow

1.  **Onboarding**: Click the JobFill Pro icon in your toolbar. Upload your PDF resume to initialize your profile.
2.  **Form Discovery**: Navigate to a job application page (e.g., Greenhouse, Lever, etc.).
3.  **Scan Interface**: Click the "Scan Page" button to identify input fields and company context.
4.  **Execute Autofill**: Click "Auto Fill Application". The agent will populate all standard details and generate responses for complex questions.
5.  **Manual Verification**: Review the generated content and manually attach your CV to the application.

## Professional Disclaimer
This tool is intended to assist in the application process. Users should always review AI-generated responses for accuracy and relevance before submitting an application.
