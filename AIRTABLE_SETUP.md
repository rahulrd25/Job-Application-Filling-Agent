# Airtable Table Setup Guide

## Required Columns for `jobfilling_Data` Table

Your Airtable table needs exactly **5 columns** with these exact names:

### Column Configuration

| Column Name | Field Type | Description | Example Value |
|-------------|-----------|-------------|---------------|
| `user_id` | Single line text | Unique identifier for each user | `user_abc123xyz` |
| `category` | Single select | Question category for organization | `personal`, `professional_links`, `education`, etc. |
| `question_key` | Single line text | Normalized key for the question | `first_name`, `email`, `linkedin_url` |
| `question_text` | Long text | Human-readable question | "What is your first name?" |
| `answer` | Long text | User's answer to the question | "Rahul" |

---

## Step-by-Step Setup in Airtable

### 1. Open Your Airtable Base
- Go to: https://airtable.com/
- Open base ID: `appfK3SuGXpPVsZMI`
- Open table: `jobfilling_Data`

### 2. Add/Rename Columns

Click the **+** button or rename existing columns to create these 5 columns:

#### Column 1: `user_id`
- **Type**: Single line text
- **Purpose**: Identifies which user this answer belongs to
- Click column header → "Customize field type" → "Single line text"

#### Column 2: `category`
- **Type**: Single select
- **Purpose**: Groups questions by category
- Click column header → "Customize field type" → "Single select"
- Add these options:
  - `personal`
  - `professional_links`
  - `education`
  - `work_history`
  - `logistics`
  - `legal`
  - `screening`
  - `self_id`
  - `accessibility`

#### Column 3: `question_key`
- **Type**: Single line text
- **Purpose**: Unique identifier for each question (e.g., `first_name`, `email`)

#### Column 4: `question_text`
- **Type**: Long text
- **Purpose**: The actual question asked to the user

#### Column 5: `answer`
- **Type**: Long text
- **Purpose**: User's answer to the question

---

## Example Data After Setup

| user_id | category | question_key | question_text | answer |
|---------|----------|--------------|---------------|--------|
| user_abc123 | personal | first_name | What is your first name? | Rahul |
| user_abc123 | personal | last_name | What is your last name? | Dhanawade |
| user_abc123 | personal | email | What is your email address? | rahul@example.com |
| user_abc123 | professional_links | linkedin_url | What is your LinkedIn profile URL? | https://linkedin.com/in/rahul |

---

## Quick Reference: Required Column Names

```
user_id
category
question_key
question_text
answer
```

---

## Testing the Connection

After setting up columns, test the backend:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "airtable",
  "connection": "ok"
}
```

Test saving data:
```bash
curl -X POST http://localhost:8000/save-answer \
  -H "Content-Type: application/json" \
  -H "x-user-id: test_user_123" \
  -d '{"question_key": "first_name", "answer": "Rahul"}'
```

Then check your Airtable table - you should see the new record!
