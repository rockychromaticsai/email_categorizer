# Email Categorizer

An AI-powered email classification system that categorizes customer emails into predefined tags using Google's Gemini AI.

## Features

- Single email classification
- Batch email processing
- CSV export functionality
- Web interface
- REST API endpoints

##Video Preview
https://github.com/user-attachments/assets/a2390a0b-8915-4145-952c-16eb5cdd0473

## Setup


1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory with your Gemini API key:
```
GOOGLE_API_KEY=your_api_key_here
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

The application will be available at:
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Endpoints

- `POST /classify`: Classify a single email
- `POST /classify-batch`: Classify multiple emails
- `POST /export-csv`: Export classification results as CSV

## Example Usage

### Single Email Classification
```python
import requests

response = requests.post(
    "http://localhost:8000/classify",
    json={"content": "I've been charged twice and I need my money back."}
)
print(response.json())
# Output: {"email": "I've been charged twice and I need my money back.", "tags": ["Billing Issue", "Complaint"]}
```

### Batch Classification
```python
emails = [
    "I've been charged twice and I need my money back.",
    "The new feature is amazing!",
    "I can't log into my account."
]
response = requests.post(
    "http://localhost:8000/classify-batch",
    json={"emails": emails}
)
print(response.json())
```

## Available Tags

1. Bug Report
2. Billing Issue
3. Praise
4. Complaint
5. Feature Request
6. Technical Support
7. Sales Inquiry
8. Security Concern
9. Spam/Irrelevant
10. Refund Request
11. Shipping/Delivery
12. Other
