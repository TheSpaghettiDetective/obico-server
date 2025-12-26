from django.utils.translation import get_language


# Mapping from Django language codes to human-readable language names
LANGUAGE_NAMES = {
    'zh-cn': 'Simplified Chinese',
    'zh-tw': 'Traditional Chinese',
    'pt-br': 'Portuguese',
    'es': 'Spanish',
    'de': 'German',
    'fr': 'French',
    'it': 'Italian',
    'ru': 'Russian',
    'en': 'English',
}


def get_response_language_rule(chat):
    """
    Returns a CRITICAL language rule string for LLM system prompts.

    Priority:
    1. If user messages exist -> instruct LLM to match user's most recent message language
    2. If no user messages -> use lang= query param (via Django translation), defaulting to English

    Args:
        chat: Dictionary containing 'messages' array with chat history

    Returns:
        String with explicit language instruction for LLM system prompt
    """
    messages = chat.get('messages', [])
    user_messages = [m for m in messages if m.get('role') == 'user']

    if user_messages:
        # User messages exist - instruct LLM to match user's language
        return "CRITICAL LANGUAGE RULE: Respond in the same language as the user's most recent message. Do not mix languages."

    # No user messages - use lang= query param (set by middleware)
    current_lang = get_language() or 'en'
    # Normalize language code (handle cases like 'en-us' -> 'en')
    lang_code = current_lang.lower().split('-')[0]

    # Map to full language code if needed (e.g., 'zh' -> 'zh-cn')
    # But first check if we have an exact match
    if current_lang.lower() in LANGUAGE_NAMES:
        language_name = LANGUAGE_NAMES[current_lang.lower()]
    elif lang_code in LANGUAGE_NAMES:
        language_name = LANGUAGE_NAMES[lang_code]
    else:
        # Fallback to English if language not supported
        language_name = 'English'

    return f"CRITICAL LANGUAGE RULE: You MUST respond entirely in {language_name}. Do not mix languages."

