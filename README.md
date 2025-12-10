# XIAO RP2040 金庫ダイヤル風キーボード

ロータリーエンコーダとスイッチを使った、金庫のダイヤルをモチーフにしたユニークなキーボード入力デバイスです。

## 特徴

- **金庫ダイヤル風入力**: 回転方向を変えることで文字を確定
- **ダブルクリック対応**: Shift+文字の入力が可能
- **モード切り替え**: 複数の入力モードに対応可能な拡張性
- **US/JIS対応**: USキーボードと日本語キーボードの両方に対応

## ハードウェア要件

- Seeed Studio XIAO RP2040
- ロータリーエンコーダ (KY-040など)
- タクトスイッチ
- I2C OLEDディスプレイ (SH1106, 128x64)

## 配線

### ロータリーエンコーダ
- CLK (A) → XIAO D9
- DT (B) → XIAO D10
- GND → XIAO GND
- + → XIAO 3V3

### スイッチ
- 片方の足 → XIAO D7
- もう片方の足 → XIAO GND

### I2C OLEDディスプレイ
- SCL → XIAO SCL (D5)
- SDA → XIAO SDA (D4)
- VCC → XIAO 3V3
- GND → XIAO GND

## 必要なライブラリ

CircuitPythonの`lib`フォルダに以下をコピー:
- `adafruit_displayio_ssd1306.mpy`
- `adafruit_display_text` (フォルダ)
- `adafruit_bus_device` (フォルダ)
- `adafruit_hid` (フォルダ)

## ファイル構成

```
rotary_keyinput_device_rp2040/
├── code.py              # メインプログラム
├── config.py            # 設定ファイル（ピン配置、文字リストなど）
├── keyboard_mapping.py  # キーボードマッピング（US/JIS）
├── switch_handler.py    # スイッチ管理（ダブルクリック検出）
├── mode_manager.py      # モード管理システム（基底クラス）
├── modes/               # モードパッケージ
│   ├── __init__.py     # パッケージ初期化
│   └── basic_mode.py   # 基本入力モード（金庫ダイヤル風）
└── README.md           # このファイル
```

## 使い方

### 基本操作

1. **ロータリーエンコーダを回す**: 文字を選択
2. **回転方向を変える**: 選択中の文字を入力
3. **シングルクリック**: 選択中の文字を入力
4. **ダブルクリック**: Shift+文字を入力（大文字・記号）

### 設定変更

`config.py`で以下を変更できます:

```python
# キーボードレイアウト
KEYBOARD_LAYOUT = 'JIS'  # 'US' または 'JIS'

# ピン配置
ENCODER_PIN_A = board.D9
ENCODER_PIN_B = board.D10
SWITCH_PIN = board.D7

# 文字リスト
CHAR_LIST = [...]  # カスタマイズ可能
```

## 新しいモードの追加方法

`mode_manager.py`に新しいモードクラスを追加:

```python
class DeleteMode(Mode):
    """削除モード"""
    
    def __init__(self, keyboard, char_list, char_to_keycode, needs_shift):
        super().__init__("Delete", keyboard, char_list, char_to_keycode, needs_shift)
    
    def handle_single_click(self, current_char_index):
        # Backspaceを送信
        self.keyboard.send(Keycode.BACKSPACE)
        print("Sent: Backspace")
        return None
```

`code.py`でモードを登録:

```python
delete_mode = DeleteMode(keyboard, CHAR_LIST, CHAR_TO_KEYCODE, NEEDS_SHIFT)
mode_manager.add_mode(delete_mode)
```

## ライセンス

MIT License

## 作者

Your Name
