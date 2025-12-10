# SPDX-FileCopyrightText: 2024 Your Name
#
# SPDX-License-Identifier: MIT

"""
XIAO RP2040とロータリーエンコーダ、スイッチ、I2C OLEDを使ったCircuitPythonサンプルコード

必要なハードウェア:
- Seeed Studio XIAO RP2040
- ロータリーエンコーダ (KY-040など)
- タクトスイッチ
- I2C OLEDディスプレイ (SSD1306, 128x64)

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
"""
import time
import board
import digitalio
import rotaryio
import displayio
import terminalio
import i2cdisplaybus
import usb_hid
import vectorio
from adafruit_display_text import label
from adafruit_displayio_sh1106 import SH1106
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

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
    '~': Keycode.GRAVE_ACCENT
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
    '~': Keycode.EQUALS
}

# USキーボード用Shift必要文字
NEEDS_SHIFT_US = set('!@#$%^&*()_+{}|:"<>?~')

# JISキーボード用Shift必要文字
NEEDS_SHIFT_JIS = set('!"#$%&\'()*+:;<>?[]^_{|}~')

# レイアウトに応じて適切なマッピングを選択
if KEYBOARD_LAYOUT == 'JIS':
    CHAR_TO_KEYCODE = CHAR_TO_KEYCODE_JIS
    NEEDS_SHIFT = NEEDS_SHIFT_JIS
    print("Keyboard Layout: JIS (Japanese)")
else:
    CHAR_TO_KEYCODE = CHAR_TO_KEYCODE_US
    NEEDS_SHIFT = NEEDS_SHIFT_US
    print("Keyboard Layout: US")

# --- スイッチハンドラークラス ---
class SwitchHandler:
    """ダブルクリック検出機能を持つスイッチハンドラー"""
    
    def __init__(self, switch_pin, double_click_threshold=0.3):
        """
        Args:
            switch_pin: スイッチのピン
            double_click_threshold: ダブルクリック判定時間（秒）
        """
        # スイッチ (内部プルアップ抵抗を有効化)
        self.switch = digitalio.DigitalInOut(switch_pin)
        self.switch.direction = digitalio.Direction.INPUT
        self.switch.pull = digitalio.Pull.UP
        
        self.last_state = True  # 押されていない状態で初期化
        self.last_click_time = 0
        self.double_click_threshold = double_click_threshold
        self.waiting_for_double_click = False
        self.pending_callback = None
    
    def update(self):
        """
        スイッチの状態を更新し、クリックイベントを検出
        
        Returns:
            tuple: (event_type, None) 
                event_type: 'single', 'double', 'timeout', None
        """
        current_state = self.switch.value
        current_time = time.monotonic()
        event = None
        
        # タイムアウトチェック
        if self.waiting_for_double_click and (current_time - self.last_click_time) >= self.double_click_threshold:
            self.waiting_for_double_click = False
            event = 'timeout'  # シングルクリックとして処理
        
        # スイッチの状態変化をチェック
        if current_state != self.last_state:
            self.last_state = current_state
            # 押されたとき (プルアップなのでFalseになる)
            if not current_state:
                # ダブルクリック判定
                is_double_click = self.waiting_for_double_click and (current_time - self.last_click_time) < self.double_click_threshold
                
                if is_double_click:
                    self.waiting_for_double_click = False
                    event = 'double'
                else:
                    # 1回目のクリック: 待機状態にする
                    self.waiting_for_double_click = True
                    self.last_click_time = current_time
        
        return event


# --- 初期化 ---

# I2Cとディスプレイ
# ボードに接続されているディスプレイを解放
displayio.release_displays()

try:
    # board.I2C() は board.SCL と board.SDA を使います
    i2c = board.I2C()
    display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=I2C_ADDRESS)
    display = SH1106(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, colstart=2)

except (ValueError, RuntimeError) as e:
    print(f"Error: ディスプレイが見つかりません。接続とI2Cアドレス({hex(I2C_ADDRESS)})を確認してください。")
    print(e)
    # ディスプレイがない場合でも実行を続ける
    display = None


# ロータリーエンコーダ
encoder = rotaryio.IncrementalEncoder(ENCODER_PIN_A, ENCODER_PIN_B)

# スイッチハンドラー
switch_handler = SwitchHandler(SWITCH_PIN)

# USBキーボード
keyboard = Keyboard(usb_hid.devices)

# --- ディスプレイ表示の準備 ---
if display:
    # 表示グループを作成
    main_group = displayio.Group()
    display.root_group = main_group

    # 前の文字を小さく表示（左側）
    prev_char_label = label.Label(terminalio.FONT, text="~", color=0x888888, x=10, y=20, scale=2)
    main_group.append(prev_char_label)
    
    # 選択中の文字を大きく表示（中央）
    char_label = label.Label(terminalio.FONT, text="a", color=0xFFFFFF, x=54, y=16, scale=4)
    main_group.append(char_label)
    
    # 次の文字を小さく表示（右側）
    next_char_label = label.Label(terminalio.FONT, text="b", color=0x888888, x=108, y=20, scale=2)
    main_group.append(next_char_label)

# --- 変数の準備 ---
current_char_index = 0  # 現在選択中の文字のインデックス
last_encoder_pos = 0
encoder.position = 0  # エンコーダ位置を0にリセット

# 回転方向追跡用
last_rotation_direction = None  # None: 未初期化, -1: 左回転, 1: 右回転

# --- メインループ ---
while True:
    current_encoder_pos = -encoder.position

    # エンコーダの値が変化したかチェック
    if current_encoder_pos != last_encoder_pos:
        # エンコーダの変化量を計算
        delta = current_encoder_pos - last_encoder_pos
        last_encoder_pos = current_encoder_pos
        
        # 現在の回転方向を判定
        current_rotation_direction = 1 if delta > 0 else -1
        
        # 回転方向が変わったかチェック
        if last_rotation_direction is not None and current_rotation_direction != last_rotation_direction:
            # 方向が変わった！金庫のダイヤルのように文字を入力
            # 方向変更時点での文字（まだインデックス更新前）を入力
            selected_char = CHAR_LIST[current_char_index]
            
            if selected_char in CHAR_TO_KEYCODE:
                keycode = CHAR_TO_KEYCODE[selected_char]
                # 記号でShiftキーが必要な文字かチェック
                if selected_char in NEEDS_SHIFT:
                    keyboard.send(keycode, Keycode.SHIFT)
                else:
                    keyboard.send(keycode)
                print(f"Sent (Direction Change): '{selected_char}'")
            else:
                print(f"Warning: No keycode mapping for '{selected_char}'")
        
        # 文字インデックスを更新（リストの範囲内でループ）
        current_char_index = (current_char_index + delta) % len(CHAR_LIST)
        
        # 回転方向を更新（インデックス更新後に更新）
        last_rotation_direction = current_rotation_direction
        
        # 選択中の文字と前後の文字を取得
        selected_char = CHAR_LIST[current_char_index]
        prev_index = (current_char_index - 1) % len(CHAR_LIST)
        next_index = (current_char_index + 1) % len(CHAR_LIST)
        prev_char = CHAR_LIST[prev_index]
        next_char = CHAR_LIST[next_index]
        
        print(f"Selected: '{selected_char}'")
        
        # ディスプレイを更新
        if display:
            prev_char_label.text = prev_char
            char_label.text = selected_char
            next_char_label.text = next_char

    # スイッチイベントをチェック
    switch_event = switch_handler.update()
    
    if switch_event == 'timeout':
        # タイムアウト: シングルクリックとして処理
        selected_char = CHAR_LIST[current_char_index]
        
        if selected_char in CHAR_TO_KEYCODE:
            keycode = CHAR_TO_KEYCODE[selected_char]
            # 記号でShiftキーが必要な文字かチェック
            if selected_char in NEEDS_SHIFT:
                keyboard.send(keycode, Keycode.SHIFT)
            else:
                keyboard.send(keycode)
            print(f"Sent (Click): '{selected_char}'")
            # 回転方向をリセット（次の回転がどちらでも新しい方向として記録される）
            last_rotation_direction = None
        else:
            print(f"Warning: No keycode mapping for '{selected_char}'")
    
    elif switch_event == 'double':
        # ダブルクリック: Shiftキーと一緒に送信
        selected_char = CHAR_LIST[current_char_index]
        
        if selected_char in CHAR_TO_KEYCODE:
            keycode = CHAR_TO_KEYCODE[selected_char]
            keyboard.send(keycode, Keycode.SHIFT)
            print(f"Sent (Double Click): '{selected_char.upper() if selected_char.isalpha() else selected_char}'")
            # 回転方向をリセット（次の回転がどちらでも新しい方向として記録される）
            last_rotation_direction = None
        else:
            print(f"Warning: No keycode mapping for '{selected_char}'")
    
    time.sleep(0.01)  # CPU負荷を軽減
