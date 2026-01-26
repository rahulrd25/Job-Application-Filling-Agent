# Airtable Configuration

The system relies on an Airtable base for persistent user profile storage. This document outlines the required schema for the `jobfilling_Data` table.

## Schema Definition

Ensure the table contains exactly the following 5 columns with the specified types.

| Column Name     | Type         | Description                                      |
|-----------------|--------------|--------------------------------------------------|
| `user_id`       | Single line text | Unique identifier for the user session.          |
| `category`      | Single select | Data category (e.g., `personal`, `education`).   |
| `question_key`  | Single line text | The normalized ID used by the matcher.           |
| `question_text` | Long text    | The label/prompt displayed in the UI.            |
| `answer`        | Long text    | The user's input content.                        |

## Configuration Steps

1.  **Select Column Options**: Configure the `category` Single select column with the following options to match the backend constants:
    *   `personal`
    *   `professional_links`
    *   `education`
    *   `work_history`
    *   `logistics`
    *   `legal`
    *   `screening`
    *   `self_id`
    *   `accessibility`
    *   `pitch`

2.  **Verify Keys**: Ensure `question_key` values use snake_case (e.g., `first_name`, `linkedin_url`) as the backend matcher relies on exact string equality.

## Verification

Validate the configuration by running a health check against the local API:

```bash
curl http://localhost:8000/health
```

**Success Response:**
```json
{
  "status": "healthy",
  "database": "airtable",
  "connection": "ok"
}
```
