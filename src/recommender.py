def get_charter_advisory(current_spot: float, predicted_14d: float):
    """
    Computes projected rate change and returns a chartering recommendation.
    
    delta = (Predicted_14d - Current_Spot) / Current_Spot
    delta <= -0.05: WAIT / DELAY CHARTERING
    delta >= 0.05: CHARTER IMMEDIATELY
    Otherwise: NEUTRAL / SPOT BOOKING
    """
    if current_spot == 0:
        return {
            "recommendation": "NEUTRAL / SPOT BOOKING",
            "delta": 0.0,
            "projected_savings": 0.0,
            "confidence_score": 0.0
        }
        
    delta = (predicted_14d - current_spot) / current_spot
    
    if delta <= -0.05:
        recommendation = "WAIT / DELAY CHARTERING"
        # Projected savings is the difference if we wait
        projected_savings = current_spot - predicted_14d 
    elif delta >= 0.05:
        recommendation = "CHARTER IMMEDIATELY"
        # Projected savings is the cost avoided by chartering now
        projected_savings = predicted_14d - current_spot
    else:
        recommendation = "NEUTRAL / SPOT BOOKING"
        projected_savings = 0.0
        
    # Confidence score heuristic based on magnitude of delta (capped at 0.95)
    confidence_score = min(0.95, abs(delta) * 10)
    
    return {
        "recommendation": recommendation,
        "delta": float(delta),
        "projected_savings": float(projected_savings),
        "confidence_score": float(confidence_score)
    }
