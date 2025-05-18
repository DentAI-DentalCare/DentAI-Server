from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from datetime import datetime, timezone

def verify_token():
    """
    Middleware that checks if a request has a valid, non-expired JWT token.
    """
    # Allow non-protected routes to pass through
    open_routes = ["/api/auth/login", "/api/auth/signup", "/api/auth/password/send-code",
                   "/api/auth/password/verify-code", "/api/auth/password/reset","/api/create-dummy-data", "/api/ocr/analyze-id"]
    if request.path in open_routes:
        return

    try:
        verify_jwt_in_request()  # Check if a valid JWT is provided
        claims = get_jwt()  # Extract JWT claims

        # Check token expiration
        exp_timestamp = claims["exp"]
        if datetime.now(timezone.utc).timestamp() > exp_timestamp:
            print("Token has expired")
            return jsonify({"error": "Token has expired"}), 401

    except Exception as e:
        return jsonify({"error": "Unauthorized or invalid token", "details": str(e)}), 401
