from unstructured.cleaners.core import (
    replace_unicode_quotes, 
    bytes_string_to_string,
    clean_bullets, 
    clean_dashes, 
    clean_extra_whitespace, 
    clean_non_ascii_chars, 
    clean_ordered_bullets
)

def has_unicode_quotes(text):
    """Checks if the text contains unicode quotes.

    Returns:
        bool: True if unicode quotes are present, False otherwise.
    """
    return bool(replace_unicode_quotes(text) != text)

def has_byte_string(text, encoding="utf-8"):
    """Checks if the text contains byte string characters.

    Returns:
        bool: True if byte string characters are present, False otherwise.
    """
    return bool(bytes_string_to_string(text, encoding=encoding) != text)

def has_bullets(text):
    """Checks if the text starts with bullets.

    Returns:
        bool: True if text starts with bullets, False otherwise.
    """
    return bool(clean_bullets(text) != text)

def has_dashes(text):
    """Checks if the text contains dashes.

    Returns:
        bool: True if dashes are present, False otherwise.
    """
    return bool(clean_dashes(text) != text)

def has_extra_whitespace(text):
    """Checks if the text contains extra whitespace.

    Returns:
        bool: True if extra whitespace is present, False otherwise.
    """
    return bool(clean_extra_whitespace(text) != text)

def has_non_ascii_chars(text):
    """Checks if the text contains non-ascii characters.

    Returns:
        bool: True if non-ascii characters are present, False otherwise.
    """
    return bool(clean_non_ascii_chars(text) != text)

def has_ordered_bullets(text):
    """Checks if the text starts with ordered bullets.

    Returns:
        bool: True if text starts with ordered bullets, False otherwise.
    """
    return bool(clean_ordered_bullets(text) != text)

# def detect_noisy_text_funct(text): 
#     text_has_unicode_quotes = has_unicode_quotes(text)
#     text_has_byte_string = has_byte_string(text)
#     text_has_bullets = has_bullets(text)
#     text_has_dashes = has_dashes(text)
#     text_has_extra_whitespace = has_extra_whitespace(text)
#     text_has_non_ascii_chars = has_non_ascii_chars(text)
#     text_has_ordered_bullets = has_ordered_bullets(text)