import string

CONSIDERED_CHARS = list(string.ascii_lowercase) + ['\'']

WHITESPACE_CHARS = list(string.whitespace)

# This should be randomised, but is fixed during testing
DEFAULT_SEED: int = 0x73C92AD5
