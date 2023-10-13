from unstructured.cleaners.core import (
    replace_unicode_quotes, 
    bytes_string_to_string,
    clean_bullets, 
    clean_dashes, 
    clean_extra_whitespace, 
    clean_non_ascii_chars, 
    clean_ordered_bullets
)

def clean_unicode_quotes(text): 
    """transform unicode quotes
    the output Philadelphia Eaglesâ\x80\x99 victory 
    automatically gets converted to Philadelphia 
    Eagles' victory
    """
    text = replace_unicode_quotes(text)
    return text

def convert_byte_string_to_string(text, encoding="utf-8"): 
    """Converts a byte string to a string using the specified encoding

    >>> text = "Hello ð\x9f\x98\x80"
    >>> # The output should be "Hello 😀"
    >>> bytes_string_to_string(text, encoding="utf-8")
    We first need to convert to string, then remove unnecessary 
    string if needed, for example, icon
    """
    text = bytes_string_to_string(text, encoding=encoding)
    return text

def remove_bullets(text): 
    """Removes bullets from the beginning of text
    Bullets that do not appear at the beginning of the text are not removed.
    >>> # Returns "An excellent point!"
    >>> clean_bullets("● An excellent point!")

    >>> # Returns "I love Morse Code! ●●●"
    >>> clean_bullets("I love Morse Code! ●●●")
    """
    text = clean_bullets(text)
    return text

def remove_dashes(text):
    """Removes dashes from a section of text
    Also handles special characters such as \u2013.
    
    >>> # Returns "ITEM 1A: RISK FACTORS"
    >>> clean_dashes("ITEM 1A: RISK-FACTORS\u2013")
    """ 
    text = clean_dashes(text)
    return text

def replace_extracwhitespace(text):
    """Removes extra whitespace
    Also handles special characters such as \xa0 and newlines.
    """
    text = clean_extra_whitespace(text)
    return text

def remove_non_ascii_chars(text): 
    """Removes non-ascii characters from a string.
    NOTE: Vietnamese, Japanese, ... are also removed
    """
    text = clean_non_ascii_chars(text)
    return text

def remove_ordered_bullets(text): 
    """Remove alphanumeric bullets 
    from the beginning of text up to 
    three “sub-section” levels.
    """
    text = clean_ordered_bullets(text)
    return text