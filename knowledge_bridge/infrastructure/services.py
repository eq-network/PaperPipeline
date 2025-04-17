from typing import Dict, Any, Optional
import aiohttp
import json

class LLMService:
    """
    Provides a clean interface for interacting with language model APIs.
    Handles authentication, request formatting, and response parsing.
    """
    
    def __init__(self, api_key: str, endpoint: str, model: str = "default"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model
    
    async def generate(self, prompt: str, max_tokens: int = 1000,
                      temperature: float = 0.7) -> Optional[str]:
        """
        Generate text using the configured language model.
        
        Args:
            prompt: Input prompt for generation
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            
        Returns:
            Generated text or None if the request failed
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, 
                                        headers=headers, 
                                        json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("choices", [{}])[0].get("text")
                    else:
                        # Log error details in a production system
                        return None
        except Exception as e:
            # Log exception in a production system
            return None
    
    async def extract_concepts(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract concepts from text using the language model.
        
        Args:
            text: Text to extract concepts from
            
        Returns:
            List of extracted concepts with their properties
        """
        prompt = f"""
        Extract the key concepts from the following text. 
        For each concept, provide:
        1. Name
        2. Brief description
        3. Related concepts
        
        Format the output as a JSON array.
        
        TEXT:
        {text}
        """
        
        result = await self.generate(prompt)
        if not result:
            return []
        
        try:
            # Attempt to parse JSON from the response
            # In a production system, apply more robust parsing logic
            return json.loads(result)
        except json.JSONDecodeError:
            return []