from fastapi import HTTPException, Security, status
from typing import Optional

# This is a placeholder for "Better Auth" integration.
# In a real-world scenario, this would involve JWT validation, API key checks,
# or integration with an OAuth provider.

# For now, we will simulate user authentication by requiring a user_id header.
# In production, this would be replaced by actual authentication logic that
# verifies a token and extracts the user_id securely.

class NotAuthenticatedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user_id(user_id: Optional[str] = Security(lambda user_id: user_id)) -> str:
    """
    Dependency to get the current authenticated user's ID.
    For demonstration, it expects 'user_id' to be passed directly in the request header/query.
    In a real application, this would parse a JWT or similar authentication token.
    """
    if not user_id:
        raise NotAuthenticatedException()
    # Basic validation: ensure user_id is a non-empty string.
    # More robust validation (e.g., UUID check) would be done in a real system.
    if not isinstance(user_id, str) or not user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id provided in authentication."
        )
    return user_id