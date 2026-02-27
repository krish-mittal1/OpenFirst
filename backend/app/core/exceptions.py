

class OpenFirstError(Exception):

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(OpenFirstError):
    def __init__(self, resource: str = "Resource", identifier: str = ""):
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} '{identifier}' not found"
        super().__init__(detail, status_code=404)


class GitHubAPIError(OpenFirstError):
    def __init__(self, message: str = "GitHub API error", status_code: int = 502):
        super().__init__(message, status_code=status_code)


class RateLimitExceededError(GitHubAPIError):
    def __init__(self, reset_at: str = ""):
        msg = "GitHub API rate limit exceeded"
        if reset_at:
            msg += f". Resets at {reset_at}"
        super().__init__(msg, status_code=429)
