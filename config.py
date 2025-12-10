# SPDX-FileCopyrightText: 2024 Your Name
# SPDX-License-Identifier: MIT

"""
設定ファイル
ピン配置やキーボードレイアウトなどの設定
"""

import board

# --- ピン設定 ---
ENCODER_PIN_A = board.D9
ENCODER_PIN_B = board.D10
SWITCH_PIN = board.D7

# --- キーボード設定 ---
KEYBOARD_LAYOUT = 'JIS'  # 'US' または 'JIS' を選択

# --- ディスプレイ設定 ---
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
I2C_ADDRESS = 0x3C  # 使用するOLEDのアドレスに合わせて変更してください

# --- 文字選択設定 ---
# 選択可能な文字リスト（アルファベット小文字、数字、記号）
# 大文字は後でシフト機能で実装
CHAR_LIST = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/',
    ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~'
]
