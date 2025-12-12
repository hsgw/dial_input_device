# SPDX-FileCopyrightText: 2025 Takuya Urakawa (@hsgw 5z6p.com)
# SPDX-License-Identifier: MIT

"""
キーボードマッピング
USキーボードとJISキーボードのキーコードマッピング
"""

from adafruit_hid.keycode import Keycode

# --- キーボードレイアウト別のキーコードマッピング ---

# USキーボード用マッピング
CHAR_TO_KEYCODE_US = {
    'a': Keycode.A, 'b': Keycode.B, 'c': Keycode.C, 'd': Keycode.D, 'e': Keycode.E,
    'f': Keycode.F, 'g': Keycode.G, 'h': Keycode.H, 'i': Keycode.I, 'j': Keycode.J,
    'k': Keycode.K, 'l': Keycode.L, 'm': Keycode.M, 'n': Keycode.N, 'o': Keycode.O,
    'p': Keycode.P, 'q': Keycode.Q, 'r': Keycode.R, 's': Keycode.S, 't': Keycode.T,
    'u': Keycode.U, 'v': Keycode.V, 'w': Keycode.W, 'x': Keycode.X, 'y': Keycode.Y,
    'z': Keycode.Z,
    '0': Keycode.ZERO, '1': Keycode.ONE, '2': Keycode.TWO, '3': Keycode.THREE,
    '4': Keycode.FOUR, '5': Keycode.FIVE, '6': Keycode.SIX, '7': Keycode.SEVEN,
    '8': Keycode.EIGHT, '9': Keycode.NINE,
    ' ': Keycode.SPACE, '!': Keycode.ONE, '"': Keycode.QUOTE, '#': Keycode.THREE,
    '$': Keycode.FOUR, '%': Keycode.FIVE, '&': Keycode.SEVEN, "'": Keycode.QUOTE,
    '(': Keycode.NINE, ')': Keycode.ZERO, '*': Keycode.EIGHT, '+': Keycode.EQUALS,
    ',': Keycode.COMMA, '-': Keycode.MINUS, '.': Keycode.PERIOD, '/': Keycode.FORWARD_SLASH,
    ':': Keycode.SEMICOLON, ';': Keycode.SEMICOLON, '<': Keycode.COMMA, '=': Keycode.EQUALS,
    '>': Keycode.PERIOD, '?': Keycode.FORWARD_SLASH, '@': Keycode.TWO,
    '[': Keycode.LEFT_BRACKET, '\\': Keycode.BACKSLASH, ']': Keycode.RIGHT_BRACKET,
    '^': Keycode.SIX, '_': Keycode.MINUS, '`': Keycode.GRAVE_ACCENT,
    '{': Keycode.LEFT_BRACKET, '|': Keycode.BACKSLASH, '}': Keycode.RIGHT_BRACKET,
    '~': Keycode.GRAVE_ACCENT,
    '\n': Keycode.ENTER  # Enter/改行キー
}

# JIS（日本語）キーボード用マッピング
CHAR_TO_KEYCODE_JIS = {
    'a': Keycode.A, 'b': Keycode.B, 'c': Keycode.C, 'd': Keycode.D, 'e': Keycode.E,
    'f': Keycode.F, 'g': Keycode.G, 'h': Keycode.H, 'i': Keycode.I, 'j': Keycode.J,
    'k': Keycode.K, 'l': Keycode.L, 'm': Keycode.M, 'n': Keycode.N, 'o': Keycode.O,
    'p': Keycode.P, 'q': Keycode.Q, 'r': Keycode.R, 's': Keycode.S, 't': Keycode.T,
    'u': Keycode.U, 'v': Keycode.V, 'w': Keycode.W, 'x': Keycode.X, 'y': Keycode.Y,
    'z': Keycode.Z,
    '0': Keycode.ZERO, '1': Keycode.ONE, '2': Keycode.TWO, '3': Keycode.THREE,
    '4': Keycode.FOUR, '5': Keycode.FIVE, '6': Keycode.SIX, '7': Keycode.SEVEN,
    '8': Keycode.EIGHT, '9': Keycode.NINE,
    ' ': Keycode.SPACE, '!': Keycode.ONE, '"': Keycode.TWO, '#': Keycode.THREE,
    '$': Keycode.FOUR, '%': Keycode.FIVE, '&': Keycode.SIX, "'": Keycode.SEVEN,
    '(': Keycode.EIGHT, ')': Keycode.NINE, '*': Keycode.QUOTE, '+': Keycode.SEMICOLON,
    ',': Keycode.COMMA, '-': Keycode.MINUS, '.': Keycode.PERIOD, '/': Keycode.FORWARD_SLASH,
    ':': Keycode.QUOTE, ';': Keycode.SEMICOLON, '<': Keycode.COMMA, '=': Keycode.MINUS,
    '>': Keycode.PERIOD, '?': Keycode.FORWARD_SLASH, '@': Keycode.LEFT_BRACKET,
    '[': Keycode.RIGHT_BRACKET, '\\': Keycode.BACKSLASH, ']': Keycode.BACKSLASH,
    '^': Keycode.EQUALS, '_': Keycode.BACKSLASH, '`': Keycode.LEFT_BRACKET,
    '{': Keycode.RIGHT_BRACKET, '|': Keycode.BACKSLASH, '}': Keycode.BACKSLASH,
    '~': Keycode.EQUALS,
    '\n': Keycode.ENTER  # Enter/改行キー
}

# USキーボード用Shift必要文字
NEEDS_SHIFT_US = set('!@#$%^&*()_+{}|:"<>?~')

# JISキーボード用Shift必要文字
NEEDS_SHIFT_JIS = set('!"#$%&\'()*+:;<>?[]^_{|}~')


def get_keycode_mapping(layout='US'):
    """
    キーボードレイアウトに応じたマッピングを取得
    
    Args:
        layout: 'US' または 'JIS'
        
    Returns:
        tuple: (CHAR_TO_KEYCODE, NEEDS_SHIFT)
    """
    if layout == 'JIS':
        print("Keyboard Layout: JIS (Japanese)")
        return CHAR_TO_KEYCODE_JIS, NEEDS_SHIFT_JIS
    else:
        print("Keyboard Layout: US")
        return CHAR_TO_KEYCODE_US, NEEDS_SHIFT_US
