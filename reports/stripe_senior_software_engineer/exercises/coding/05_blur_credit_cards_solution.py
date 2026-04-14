"""
Blur Credit Card Numbers — Solution
=====================================

Approach: Regex matching + Luhn validation.
"""

import re


def luhn_check(digits: str) -> bool:
    """Validate using Luhn algorithm."""
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:  # every second digit from right
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def blur_cards_basic(text: str) -> str:
    def mask(match: re.Match) -> str:
        num = match.group()
        return "*" * 12 + num[-4:]

    return re.sub(r'\b\d{16}\b', mask, text)


def blur_cards_formatted(text: str) -> str:
    def mask_formatted(match: re.Match) -> str:
        full = match.group()
        # Detect separator
        sep = "-" if "-" in full else " "
        digits = full.replace(sep, "")
        masked = "*" * 12 + digits[-4:]
        # Re-insert separator every 4 chars
        parts = [masked[i:i+4] for i in range(0, 16, 4)]
        return sep.join(parts)

    # Also handle plain 16-digit sequences
    text = re.sub(
        r'\b\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}\b',
        mask_formatted,
        text,
    )
    text = blur_cards_basic(text)
    return text


def blur_cards_with_luhn(text: str) -> str:
    def mask_if_valid(match: re.Match) -> str:
        num = match.group()
        if luhn_check(num):
            return "*" * 12 + num[-4:]
        return num

    return re.sub(r'\b\d{16}\b', mask_if_valid, text)


# ============ Complexity Analysis ============
# Time: O(N) where N = string length
#   - Regex scan is O(N)
#   - Luhn check is O(1) per card (always 16 digits)
# Space: O(N) for the output string

# ============ Common Interviewer Follow-ups ============
# Q: "What about cards with 13, 15, or 19 digits?"
# A: Amex is 15 digits, some cards are 13 or 19. Generalize the regex
#    to r'\b\d{13,19}\b' and mask all but last 4.
#
# Q: "What about card numbers in JSON or structured data?"
# A: Parse the structure first, mask specific fields. Don't regex over JSON.
#
# Q: "What about PCI compliance?"
# A: In production, never log full card numbers. This function should run
#    at the log ingestion layer. Use tokenization instead of masking.

# ============ What Interviewers Look For ============
# 1. Correct regex usage (word boundaries to avoid partial matches)
# 2. Not mutating the original string (use re.sub, not manual replacement)
# 3. Correct Luhn implementation (common off-by-one in doubling direction)
# 4. Handling multiple cards in one string
# 5. Preserving format for dashes/spaces

# ============ Alternative Approaches ============
# Instead of regex, scan char-by-char accumulating digit sequences.
# More manual but avoids regex edge cases. Better for streaming input.


# ============ TESTS ============

def test_basic_single():
    text = "Payment 4111111111111111 processed"
    assert blur_cards_basic(text) == "Payment ************1111 processed"

def test_basic_multiple():
    text = "Cards: 4111111111111111 and 5500000000000004"
    result = blur_cards_basic(text)
    assert "************1111" in result
    assert "************0004" in result

def test_basic_no_cards():
    text = "No cards here, just 12345"
    assert blur_cards_basic(text) == text

def test_formatted_dashes():
    text = "Card 4111-1111-1111-1111 ok"
    assert blur_cards_formatted(text) == "Card ****-****-****-1111 ok"

def test_formatted_spaces():
    text = "Card 4111 1111 1111 1111 ok"
    assert blur_cards_formatted(text) == "Card **** **** **** 1111 ok"

def test_luhn_valid():
    assert luhn_check("4111111111111111") == True

def test_luhn_invalid():
    assert luhn_check("4111111111111112") == False

def test_blur_with_luhn():
    text = "Valid: 4111111111111111 Invalid: 1234567890123456"
    result = blur_cards_with_luhn(text)
    assert "************1111" in result
    assert "1234567890123456" in result


if __name__ == "__main__":
    test_basic_single()
    test_basic_multiple()
    test_basic_no_cards()
    test_formatted_dashes()
    test_formatted_spaces()
    test_luhn_valid()
    test_luhn_invalid()
    test_blur_with_luhn()
    print("All tests passed!")
