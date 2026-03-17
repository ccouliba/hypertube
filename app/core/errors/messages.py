ERROR_MESSAGES: dict[str, str] = {
    
    # Authentication errors
    "UNAUTHORIZED": "Unauthorized",
    "INVALID_CREDENTIALS": "Invalid username or password",
    "USERNAME_EXISTS": "Username already exists",
    "EMAIL_EXISTS": "Email already exists",
    "USER_NOT_FOUND": "User not found",
    "UNSUPPORTED_LANGUAGE": "Unsupported language",
    
    # Validation errors - Common
    "MISSING_FIELDS": "Missing required fields",
    
    # Validation errors - Password
    "PASSWORD_TOO_SHORT": "Password must be at least 6 characters long",
    "PASSWORD_NO_LETTER": "Password must contain at least one letter",
    "PASSWORD_NO_UPPERCASE": "Password must contain at least one uppercase letter",
    "PASSWORD_NO_LOWERCASE": "Password must contain at least one lowercase letter",
    "PASSWORD_NO_NUMBER": "Password must contain at least one number",
    "PASSWORD_NO_SPECIAL": "Password must contain at least one special character",
    
    # Validation errors - Username
    "USERNAME_REQUIRED": "Username is required",
    "USERNAME_INVALID_CHARS": "Username can only contain letters, numbers, underscore and dash",
    
    # Validation errors - Email
    "EMAIL_REQUIRED": "Email is required",
    "INVALID_EMAIL": "Invalid email format",
    
    # Search errors
    "QUERY_REQUIRED": "Query parameter is required",
    "QUERY_TOO_SHORT": "Query must be at least 2 characters long",
    "INVALID_PAGINATION": "Page and limit must be valid integers",
    
    # Movie errors
    "MOVIE_NOT_FOUND": "Movie not found",

    # Video errors
    "VIDEO_NOT_FOUND": "Video not found",
    "VIDEO_NOT_STREAMABLE": "Video is not ready for streaming",
    "VIDEO_FILE_NOT_FOUND": "Video file path could not be resolved",
    "VIDEO_FILE_NOT_ON_DISK": "Video file not found on disk",
    "VIDEO_STILL_DOWNLOADING": "Not enough data downloaded yet, please try again shortly",
    "SERVICE_UNAVAILABLE": "Service temporarily unavailable",
}
