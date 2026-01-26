# JobFill Pro

JobFill Pro is a browser extension and backend system for automating job application forms. It uses keyword matching for standard fields and Llama 3.3 for writing long-form responses like cover letters.

## Features

*   Form Detection: Scans standard inputs and cross-origin iframes (Greenhouse, Lever, Workday) using the Chrome Scripting API.
*   Hybrid Matching: Uses a prioritized keyword engine for factual data (Phone, Email, LinkedIn) and LLM generation for descriptive questions.
*   Plain English AI: Responses are tuned to avoid AI buzzwords and corporate jargon.
*   Airtable Sync: Stores user profile data in Airtable for persistence.
*   Dynamic UI: Resizable extension popup that expands when filling the profile questionnaire.

## Architecture

### Backend (Python/FastAPI)
- Field Matcher: Keyword-based resolution of form field intents.
- Intelligence Agent: Generates text for subjective questions using Groq.
- Airtable Client: Handles data storage and retrieval.

### Extension (React/TypeScript)
- Scripting: Injects scanning logic into all frames on the active tab.
- Dashboard: Interface for scanning and triggers for the autofill process.

## Installation

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Groq API Key
*   Airtable Base and API Key

### 1. Backend
```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Create a `.env` file in the backend directory:
```env
GROQ_API_KEY=your_key
AIRTABLE_API_KEY=your_token
AIRTABLE_BASE_ID=your_id
AIRTABLE_TABLE_NAME=jobfilling_Data
```

### 2. Extension
```bash
cd extension
npm install
npm run build
```

### 3. Load Extension
1. Open `chrome://extensions/`
2. Enable Developer mode.
3. Click "Load unpacked" and select the `extension/dist` folder.

## Usage

1. Setup: Open the extension and complete the profile questionnaire. Provide details in the Pitch section to give the LLM context for writing.
2. Scan: Navigate to a job application and click Scan Application.
3. Fill: Click Fill Application. Factual fields are matched directly; creative fields are generated via Groq.
4. Review: Verify all fields before submitting.
