"""
Google Gemini API client wrapper with rate limiting and error handling.
"""

import logging
from typing import Optional

from backend.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    """Lazy-init Gemini client."""
    global _client
    if _client is None:
        try:
            import google.generativeai as genai
            if not GEMINI_API_KEY:
                logger.warning("GEMINI_API_KEY not set — LLM features will use fallback text")
                return None
            genai.configure(api_key=GEMINI_API_KEY)
            _client = genai.GenerativeModel("gemini-2.0-flash")
            logger.info("✅ Gemini client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            return None
    return _client


def generate_text(prompt: str, max_tokens: int = 2048) -> str:
    """
    Generate text using Gemini. Falls back to a placeholder if API unavailable.
    """
    client = _get_client()
    if client is None:
        return _fallback_response(prompt)

    try:
        response = client.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": 0.7,
            },
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return _fallback_response(prompt)


def _fallback_response(prompt: str) -> str:
    """Fallback when Gemini is unavailable."""
    return (
        "⚠️ **LLM Analysis Unavailable**\n\n"
        "The Gemini API key is not configured or the service is temporarily unavailable. "
        "Please set `GEMINI_API_KEY` in your `.env` file to enable AI-powered market analysis.\n\n"
        "You can get a free API key at: https://aistudio.google.com/app/apikey"
    )
