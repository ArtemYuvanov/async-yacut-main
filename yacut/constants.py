import re
import string


ORIGINAL_MAX_LEN = 2048
SHORT_MAX_LEN = 16
RESERVED_SHORTS = {"files"}
SHORT_ALPHABET = string.ascii_letters + string.digits
SHORT_LENGTH = 6
MAX_GENERATION_ATTEMPTS = 100
ALLOWED_RE = rf"^[{re.escape(SHORT_ALPHABET)}]+$"
REDIRECT_VIEW_NAME = "redirect_short"
