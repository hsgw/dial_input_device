# SPDX-FileCopyrightText: 2024 Your Name
# SPDX-License-Identifier: MIT

"""
XIAO RP2040 金庫ダイヤル風キーボード

必要なハードウェア:
- Seeed Studio XIAO RP2040
- ロータリーエンコーダ (KY-040など)
- タクトスイッチ
- I2C OLEDディスプレイ (SH1106, 128x64)

接続:
- ロータリーエンコーダ:
  - CLK (A) -> XIAO D9
  - DT (B)  -> XIAO D10
  - GND     -> XIAO GND
  - +       -> XIAO 3V3
- スイッチ:
  - 片方の足 -> XIAO D7
  - もう片方の足 -> XIAO GND
- I2C OLEDディスプレイ:
  - SCL -> XIAO SCL (D5)
  - SDA -> XIAO SDA (D4)
  - VCC -> XIAO 3V3
  - GND -> XIAO GND

必要なライブラリ (libフォルダにコピー):
- adafruit_displayio_ssd1306.mpy
- adafruit_display_text (フォルダ)
- adafruit_bus_device (フォルダ)
- adafruit_hid (フォルダ)
"""

import time
import board
import rotaryio
import displayio
import i2cdisplaybus
import usb_hid
from adafruit_displayio_sh1106 import SH1106
from adafruit_hid.keyboard import Keyboard

# 自作モジュールのインポート
from config import (
    ENCODER_PIN_A, ENCODER_PIN_B, SWITCH_PIN,
    KEYBOARD_LAYOUT, DISPLAY_WIDTH, DISPLAY_HEIGHT, I2C_ADDRESS
)
from switch_handler import SwitchHandler
from mode_manager import ModeManager
from switch_handler import SwitchHandler
from mode_manager import ModeManager
from modes import BasicMode, UtilityMode, JapaneseMode


# --- 初期化 ---

# I2Cとディスプレイ
displayio.release_displays()

try:
    i2c = board.I2C()
    display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=I2C_ADDRESS)
    display = SH1106(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, colstart=2)
except (ValueError, RuntimeError) as e:
    print(f"Error: ディスプレイが見つかりません。接続とI2Cアドレス({hex(I2C_ADDRESS)})を確認してください。")
    print(e)
    display = None

# ロータリーエンコーダ
encoder = rotaryio.IncrementalEncoder(ENCODER_PIN_A, ENCODER_PIN_B)

# スイッチハンドラー
switch_handler = SwitchHandler(SWITCH_PIN)

# USBキーボード
keyboard = Keyboard(usb_hid.devices)

# --- ディスプレイ表示の準備 ---
main_group = None

if display:
    # 表示グループを作成（各モードがここにラベルを追加）
    main_group = displayio.Group()
    display.root_group = main_group

# --- 変数の準備 ---
last_encoder_pos = 0
encoder.position = 0  # エンコーダ位置を0にリセット

# --- モードマネージャーの初期化 ---
mode_manager = ModeManager(display, main_group)

# 基本入力モードを追加
basic_mode = BasicMode(keyboard, display, main_group)
mode_manager.add_mode(basic_mode)

# ユーティリティモードを追加
utility_mode = UtilityMode(keyboard, display, main_group)
mode_manager.add_mode(utility_mode)

# 日本語入力モードを追加
japanese_mode = JapaneseMode(keyboard, display, main_group)
mode_manager.add_mode(japanese_mode)

# 初期モードを設定（ディスプレイレイアウトと状態も自動初期化）
mode_manager.set_mode("Japanese")

# --- メインループ ---
while True:
    current_encoder_pos = encoder.position

    # エンコーダの値が変化したかチェック
    if current_encoder_pos != last_encoder_pos:
        # エンコーダの変化量を計算
        delta = current_encoder_pos - last_encoder_pos
        last_encoder_pos = current_encoder_pos
        
        # モードに回転を通知（モードが状態を更新）
        mode_manager.handle_rotation(delta)

    # スイッチイベントをチェック
    switch_event = switch_handler.update()
    
    if switch_event == 'timeout':
        # シングルクリック
        mode_manager.handle_single_click()
    
    elif switch_event == 'double':
        # ダブルクリック
        mode_manager.handle_double_click()
    
    elif switch_event == 'long_press':
        # 長押しでユーティリティモードへ
        print("Long press detected: Switching to Utility Mode")
        mode_manager.set_mode("Utility", reset=True)
    
    time.sleep(0.01)  # CPU負荷を軽減
