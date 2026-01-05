REPORT_PROMPT_TEMPLATE = """
You are a senior financial analyst. Analyze the following data for stock ticker {ticker}.

**Context:**
- Current Price: {current_price}
- Predicted Price (7-day horizon): {predicted_price}
- Model Signal: {signal}
- Confidence Score: {confidence}
- Key Indicators: {indicators}

**Task:**
1. Explain the "Why" behind the signal ({signal}).
2. Highlight any risks or conflicting indicators.
3. Provide a brief summary of the market trend for this stock.

**Constraints:**
- Do NOT provide specific financial advice (e.g., "You must buy this").
- Use cautious language (e.g., "The model suggests...", "Likely to...").
- unexpected low confidence should be noted.

**Output:**
Return a JSON or structured text with fields: "Explanation", "Risks", "Summary".
"""
