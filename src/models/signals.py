import pandas as pd
import logging

def generate_signals(current_price: float, predicted_price: float, indicators: dict = None) -> dict:
    """
    Generates Buy/Sell/Hold signal based on prediction and signals.
    
    Args:
        current_price (float): Latest known price.
        predicted_price (float): Predicted price (e.g. next day/week).
        indicators (dict): Latest technical indicator values.
        
    Returns:
        dict: Signal info {'action': 'BUY'/'SELL'/'HOLD', 'confidence': 0.0-1.0, 'reason': str}
    """
    
    threshold = 0.01 # 1% change threshold
    
    expected_change = (predicted_price - current_price) / current_price
    
    action = "HOLD"
    confidence = 0.5
    reasons = []
    
    # Prediction logic
    if expected_change > threshold:
        action = "BUY"
        reasons.append(f"Model predicts {expected_change*100:.2f}% upside.")
        confidence += 0.2
    elif expected_change < -threshold:
        action = "SELL"
        reasons.append(f"Model predicts {expected_change*100:.2f}% downside.")
        confidence += 0.2
        
    # Indicator confirmation (Simple Logic)
    if indicators:
        rsi = indicators.get('RSI', 50)
        if rsi < 30 and action == "BUY":
            reasons.append("RSI indicates oversold conditions (Bullish).")
            confidence += 0.1
        elif rsi > 70 and action == "SELL":
            reasons.append("RSI indicates overbought conditions (Bearish).")
            confidence += 0.1
            
        if action == "HOLD":
             if rsi < 30:
                 action = "WATCH" # Potential buy
                 reasons.append("RSI low but model neutral.")
    
    confidence = min(confidence, 1.0)
    
    return {
        "action": action,
        "confidence": round(confidence, 2),
        "reasons": "; ".join(reasons),
        "predicted_price": round(predicted_price, 2),
        "current_price": round(current_price, 2)
    }
