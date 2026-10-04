import os
import json
import base64
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

# Initialize the Gemini client using official Google GenAI SDK
# Make sure GOOGLE_API_KEY is set in your environment variables
client = genai.Client()


def extract_item_attributes(
    text_context: str, 
    image_bytes: Optional[bytes] = None, 
    mime_type: str = "image/jpeg"
) -> Dict[str, Any]:
    """
    Extracts structured JSON attributes from an image and/or user text description.
    Used during ingestion (Found items) and initial query setup (Lost items).
    """
    prompt = f"""
    You are an expert Lost and Found item classifier. 
    Analyze the provided input and extract structured attributes into JSON.
    
    User Context / Description: {text_context}
    
    Extract the following fields accurately:
    - category (e.g., "Backpack", "Electronics", "Wallet", "Keys")
    - primary_color (e.g., "Navy Blue", "Black", "Silver")
    - brand (e.g., "Herschel", "Apple", "Unknown")
    - model (e.g., "iPhone 13", "Little America", null)
    - distinctive_features (list of key visual details like "Red keychain", "Scratched corner", "Sticker")
    - keywords (list of 3-5 tags for search matching)
    """

    contents = [prompt]
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )

    return json.loads(response.text)


def generate_embedding(
    text_context: str, 
    image_bytes: Optional[bytes] = None, 
    mime_type: str = "image/jpeg",
    task_type: str = "RETRIEVAL_DOCUMENT"
) -> List[float]:
    """
    Generates a 768-dimensional multimodal vector combining image and text context.
    
    Args:
        task_type: 
            - "RETRIEVAL_DOCUMENT" when storing an item into TiDB.
            - "RETRIEVAL_QUERY" when searching for a lost item.
    """
    contents = [text_context]
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

    # Calls Gemini's native multimodal embedding model
    response = client.models.embed_content(
        model="text-embedding-004",  # or "gemini-embedding-2-preview"
        contents=contents,
        config=types.EmbedContentConfig(
            task_type=task_type
        )
    )

    return response.embeddings[0].values


def rerank_and_evaluate_matches(
    lost_item_details: Dict[str, Any], 
    db_candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Acts as the Gemini Matcher Agent. Evaluates the top candidates retrieved 
    from TiDB Vector Search and assigns match percentages, justifications, and reasons.
    """
    prompt = f"""
    You are the LostLens AI Matcher Agent.
    
    A user lost this item:
    {json.dumps(lost_item_details, indent=2)}
    
    Here are candidate found items retrieved from TiDB Vector Search:
    {json.dumps(db_candidates, indent=2)}
    
    Compare the lost item against each candidate item. Analyze color, brand, location, category, and features.
    
    Return ONLY a JSON array of evaluated candidate objects sorted from highest match percentage to lowest:
    [
      {{
        "candidate_id": "string",
        "match_percentage": 92,
        "is_probable_match": true,
        "matching_reasons": ["Matching navy blue color", "Herschel brand verified", "Red keychain match"],
        "summary_explanation": "Strong match. Both items are navy Herschel backpacks with distinct red keychains."
      }}
    ]
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    return json.loads(response.text)