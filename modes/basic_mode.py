# SPDX-FileCopyrightText: 2024 Your Name
# SPDX-License-Identifier: MIT

"""
基本入力モード
金庫のダイヤル風の入力方式を実装
文字インデックスを内部で管理
"""

from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, KEYBOARD_LAYOUT
import terminalio
from adafruit_display_text import label
from mode_manager import Mode
from keyboard_mapping import get_keycode_mapping
from display_util import get_display_char


class BasicMode(Mode):
    """基本入力モード（金庫のダイヤル風）"""
    
    # 選択可能な文字リスト
    CHAR_LIST = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/',
        ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~'
    ]
    
    def __init__(self, keyboard, display=None, display_group=None):
        # キーボードマッピングを取得
        char_to_keycode, needs_shift = get_keycode_mapping(KEYBOARD_LAYOUT)
        super().__init__("Basic", keyboard, self.CHAR_LIST, char_to_keycode, needs_shift, display, display_group)
    
    def init_state(self):
        """基本モードの状態を初期化"""
        return {
            'char_index': 0  # 現在選択中の文字のインデックス
        }
    
    def init_display(self):
        """基本モードのディスプレイレイアウトを初期化"""
        if not self.display or self.display_group is None:
            return {}
        
        labels = {}
        
        # 現在の状態に基づいて初期表示文字を決定
        char_index = self.get_state('char_index', 0)
        selected_char = self.char_list[char_index]
        prev_index = (char_index - 1) % len(self.char_list)
        next_index = (char_index + 1) % len(self.char_list)
        prev_char = self.char_list[prev_index]
        next_char = self.char_list[next_index]
        
        # 前の文字を小さく表示（左側・左揃え）
        labels['prev'] = label.Label(
            terminalio.FONT, 
            text=prev_char, 
            color=0x888888, 
            scale=2,
            anchor_point=(0.0, 0.5),
            anchored_position=(10, DISPLAY_HEIGHT // 2)
        )
        self.display_group.append(labels['prev'])
        
        # 選択中の文字を大きく表示（中央・中央揃え）
        labels['current'] = label.Label(
            terminalio.FONT, 
            text=selected_char, 
            color=0xFFFFFF, 
            scale=4,
            anchor_point=(0.5, 0.5),
            anchored_position=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 4)
        )
        self.display_group.append(labels['current'])
        
        # 次の文字を小さく表示（右側・右揃え）
        labels['next'] = label.Label(
            terminalio.FONT, 
            text=next_char, 
            color=0x888888, 
            scale=2,
            anchor_point=(1.0, 0.5),
            anchored_position=(DISPLAY_WIDTH - 10, DISPLAY_HEIGHT // 2)
        )
        self.display_group.append(labels['next'])
        
        return labels
    
    def update_display_state(self):
        """状態に基づいてディスプレイを更新"""
        if not self.display or not self.display_labels:
            return
        
        char_index = self.get_state('char_index', 0)
        
        # 選択中の文字と前後の文字を取得
        selected_char = get_display_char(self.char_list[char_index])
        prev_index = (char_index - 1) % len(self.char_list)
        next_index = (char_index + 1) % len(self.char_list)
        prev_char = get_display_char(self.char_list[prev_index])
        next_char = get_display_char(self.char_list[next_index])
        
        # ディスプレイを更新
        if 'prev' in self.display_labels:
            self.display_labels['prev'].text = prev_char
        if 'current' in self.display_labels:
            self.display_labels['current'].text = selected_char
        if 'next' in self.display_labels:
            self.display_labels['next'].text = next_char
        
        print(f"Selected: '{selected_char}'")
    
    def handle_rotation(self, delta):
        """回転処理：文字インデックスを更新し、方向変更で入力"""
        char_index = self.get_state('char_index', 0)
        current_rotation_direction = 1 if delta > 0 else -1
        
        # 回転方向が変わったかチェック
        if self.last_rotation_direction is not None and current_rotation_direction != self.last_rotation_direction:
            # 方向が変わった！文字を入力（インデックス更新前の文字）
            selected_char = self.char_list[char_index]
            
            if self.send_key(selected_char):
                print(f"Sent (Direction Change): '{selected_char}'")
            else:
                print(f"Warning: No keycode mapping for '{selected_char}'")
            
            self.last_rotation_direction = current_rotation_direction
        else:
            self.last_rotation_direction = current_rotation_direction
        
        # 文字インデックスを更新
        char_index = (char_index + delta) % len(self.char_list)
        self.set_state('char_index', char_index)
        
        return None
    
    def handle_single_click(self):
        """シングルクリックで文字を入力"""
        char_index = self.get_state('char_index', 0)
        selected_char = self.char_list[char_index]
        
        if self.send_key(selected_char):
            print(f"Sent (Click): '{selected_char}'")
            # 回転方向をリセット
            self.last_rotation_direction = None
        else:
            print(f"Warning: No keycode mapping for '{selected_char}'")
        
        return None  # モード変更なし
    
    def handle_double_click(self):
        """ダブルクリックでShift+文字を入力"""
        char_index = self.get_state('char_index', 0)
        selected_char = self.char_list[char_index]
        
        if self.send_key(selected_char, use_shift=True):
            print(f"Sent (Double Click): '{selected_char.upper() if selected_char.isalpha() else selected_char}'")
            # 回転方向をリセット
            self.last_rotation_direction = None
        else:
            print(f"Warning: No keycode mapping for '{selected_char}'")
        
        return None  # モード変更なし
