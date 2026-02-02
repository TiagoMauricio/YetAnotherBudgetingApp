USER_HAS_NO_ACCOUNT_ACCESS: str = "You are not a member of this account."
CATEGORY_NOT_FOUND: str = "Category not found."
REQUIRED_DATE_RANGE: str = (
    "When setting a date range, both from_date and to_date must be provided."
)
RESOURCE_ACCESS_DENIED: str = "You do not have access to this resource."
ACCOUNT_NOT_FOUND: str = "Account does not exist."
ACCOUNT_ACCESS_DENIED: str = "You don't have access to this account."
ACCOUNT_OWNERSHIP_REQUIRED: str = "You do not own this account."
DEFAULT_CATEGORY_DELETE_FORBIDDEN: str = "You can't delete a default category."
TRANSACTION_NOT_FOUND: str = "Transaction not found."
TRANSACTION_INVALID_CATEGORY: str = "Please provide a valid Category"
USER_NOT_FOUND: str = "User not found"


# Message factory functions for contextual errors
def account_already_exists(account_name: str) -> str:
    """Generate error message for duplicate account with context."""
    return f"You already have an account named: {account_name}"


def category_duplicate(category_name: str) -> str:
    """Generate error message for duplicate category with context."""
    return f"Category {category_name} already exists"


# Keep backwards compatibility with constant name
CATEGORY_DUPLICATE = category_duplicate
