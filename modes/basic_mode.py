# SPDX-FileCopyrightText: 2024 Your Name
# SPDX-License-Identifier: MIT

"""
基本入力モード
金庫のダイヤル風の入力方式を実装
文字インデックスを内部で管理
"""

from modes.input_mode import InputMode
from display_util import get_display_char


class BasicMode(InputMode):
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
        super().__init__("Basic", keyboard, self.CHAR_LIST, display, display_group)
    def on_enter(self, reset=True):
        """モードに入ったときの処理"""
        super().on_enter(reset=reset)
        # 回転方向をリセットし、フッターを初期状態に更新
        self._set_rotation_direction(None)

    def _set_rotation_direction(self, direction):
        """回転方向を設定し、フッター表示を更新する"""
        self.last_rotation_direction = direction
        
        if direction is None:
            # ニュートラル状態
            self.update_footer_text("< Prev", "Next >")
        elif direction == 1: # 右回転中
            self.update_footer_text("< Input", "Next >")
        elif direction == -1: # 左回転中
            self.update_footer_text("< Prev", "Input >")

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
        
        self._set_rotation_direction(current_rotation_direction)
        
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
            # 回転方向をリセットし、フッターを更新
            self._set_rotation_direction(None)
        else:
            print(f"Warning: No keycode mapping for '{selected_char}'")
        
        return None  # モード変更なし
    
    def handle_double_click(self):
        """ダブルクリックでShift+文字を入力"""
        char_index = self.get_state('char_index', 0)
        selected_char = self.char_list[char_index]
        
        if self.send_key(selected_char, use_shift=True):
            print(f"Sent (Double Click): '{selected_char.upper() if selected_char.isalpha() else selected_char}'")
            # 回転方向をリセットし、フッターを更新
            self._set_rotation_direction(None)
        else:
            print(f"Warning: No keycode mapping for '{selected_char}'")
        
        return None  # モード変更なし
