"""
Blur Credit Card Numbers
========================
Source: Stripe onsite coding round (interviewing.io, vervecopilot, 2024-2026)

Problem:
Implement a function that redacts credit card numbers from log strings.

Part 1: Basic masking.
  - A credit card number is a sequence of exactly 16 digits (no spaces).
  - Replace all but the last 4 digits with '*'.
  - Example: "Payment 4111111111111111 processed" -> "Payment ************1111 processed"

Part 2: Handle formatted card numbers.
  - Cards may appear as: "4111-1111-1111-1111" or "4111 1111 1111 1111"
  - Normalize to 16 digits, mask, and output in the SAME format as input.
  - Example: "Card 4111-1111-1111-1111 ok" -> "Card ****-****-****-1111 ok"

Part 3: Validate before masking.
  - Only mask numbers that pass the Luhn algorithm check.
  - If a 16-digit sequence fails Luhn, leave it unmasked.

Complexity targets:
- O(N) where N = length of the input string
- Luhn check: O(1) per card number (always 16 digits)
"""

import re


def blur_cards_basic(text: str) -> str:
    """
    Part 1: Mask 16-digit sequences, keeping last 4 digits.
    """
    # TODO: Implement
    pass


def blur_cards_formatted(text: str) -> str:
    """
    Part 2: Handle cards with dashes or spaces as separators.
    Preserve the original format in output.
    """
    # TODO: Implement
    pass


def blur_cards_with_luhn(text: str) -> str:
    """
    Part 3: Only mask card numbers that pass Luhn validation.
    """
    # TODO: Implement
    pass


def luhn_check(digits: str) -> bool:
    """
    Validate a number string using the Luhn algorithm.
    """
    # TODO: Implement
    pass


# HINT 1: Use regex r'\b\d{16}\b' to find 16-digit sequences.
#         Replace each match: '*' * 12 + match[-4:]

# HINT 2: For formatted cards, match r'\b\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}\b'
#         Extract the separator, strip digits, mask, re-insert separator.

# HINT 3: Luhn: From right, double every second digit. If doubled > 9,
#         subtract 9. Sum all digits. Valid if sum % 10 == 0.


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
    # 4111111111111111 passes Luhn
    assert luhn_check("4111111111111111") == True

def test_luhn_invalid():
    # 4111111111111112 fails Luhn
    assert luhn_check("4111111111111112") == False

def test_blur_with_luhn():
    text = "Valid: 4111111111111111 Invalid: 1234567890123456"
    result = blur_cards_with_luhn(text)
    assert "************1111" in result
    assert "1234567890123456" in result  # left unmasked


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
