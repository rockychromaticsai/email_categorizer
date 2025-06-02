from typing import List, Dict
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Available tags for classification
AVAILABLE_TAGS = [
    "Bug Report",
    "Billing Issue",
    "Praise",
    "Complaint",
    "Feature Request",
    "Technical Support",
    "Sales Inquiry",
    "Security Concern",
    "Spam/Irrelevant",
    "Refund Request",
    "Shipping/Delivery",
    "Other"
]

class EmailClassifier:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
    async def classify_email(self, email_content: str) -> Dict[str, List[str]]:
        prompt = f"""You are an AI assistant specialized in email classification. Your task is to classify customer messages into one or more of the following categories:

{', '.join(AVAILABLE_TAGS)}

Guidelines for classification:
- Bug Report: Issues with software, errors, crashes, or technical problems
- Billing Issue: Problems with charges, invoices, or payment
- Praise: Positive feedback, compliments, or appreciation
- Complaint: Negative feedback, dissatisfaction, or criticism
- Feature Request: Suggestions for new features or improvements
- Technical Support: Questions about using the product or service
- Sales Inquiry: Questions about pricing, products, or purchasing
- Security Concern: Issues related to security, privacy, or data protection
- Spam/Irrelevant: Unwanted messages or irrelevant content
- Refund Request: Requests for money back or cancellation
- Shipping/Delivery: Issues with delivery, shipping, or order status
- Other: Messages that don't fit any of the above categories

Examples:
1. "I can't log into my account, getting error 404" -> ["Bug Report", "Technical Support"]
2. "The new update is amazing! Great work!" -> ["Praise"]
3. "I've been charged twice for the same service" -> ["Billing Issue", "Complaint"]
4. "When will my order arrive? It's been 2 weeks" -> ["Shipping/Delivery", "Complaint"]
5. "I want to suggest adding a dark mode feature" -> ["Feature Request"]

Now, classify this message:
{email_content}

IMPORTANT: You must respond with ONLY a JSON object in this exact format: {{"tags": ["tag1", "tag2"]}}
Do not include any other text or explanation. Use ONLY the tags from the provided list above.
"""
        
        try:
            print(f"\nProcessing email: {email_content}")
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}?key={self.api_key}"
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }]
                }
                
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"API Error: {error_text}")
                        return {"tags": ["Other"]}
                    
                    result = await response.json()
                    print(f"\nRaw API response: {result}")
                    
                    # Extract the generated text from the response
                    try:
                        generated_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
                        print(f"Generated text: {generated_text}")
                        
                        # Parse the JSON response
                        parsed_result = json.loads(generated_text)
                        print(f"Parsed JSON result: {parsed_result}")
                        
                        # Validate that all tags are from AVAILABLE_TAGS
                        validated_tags = [tag for tag in parsed_result["tags"] if tag in AVAILABLE_TAGS]
                        print(f"Validated tags: {validated_tags}")
                        
                        if not validated_tags:
                            print("No valid tags found, defaulting to Other")
                            validated_tags = ["Other"]
                        
                        final_result = {"tags": validated_tags}
                        print(f"Final result: {final_result}")
                        return final_result
                        
                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        print(f"Error parsing response: {str(e)}")
                        return {"tags": ["Other"]}
                    
        except Exception as e:
            print(f"Error in classification: {str(e)}")
            return {"tags": ["Other"]}
    
    async def classify_emails(self, emails: List[str]) -> List[Dict[str, List[str]]]:
        """Classify multiple emails in parallel"""
        import asyncio
        tasks = [self.classify_email(email) for email in emails]
        return await asyncio.gather(*tasks)
