# SPDX-FileCopyrightText: 2025 Takuya Urakawa (@hsgw 5z6p.com)
# SPDX-License-Identifier: MIT

"""
InputModeの基底クラス
基本的なディスプレイレイアウト（前/現在/次）を提供
"""

from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, KEYBOARD_LAYOUT
import terminalio
from adafruit_display_text import label
from mode_manager import Mode
from keyboard_mapping import get_keycode_mapping


class InputMode(Mode):
    """
    テキスト入力モードの共通基底クラス
    前/現在/次の3つのラベルを持つディスプレイレイアウトを初期化する
    """
    
    def __init__(self, name, keyboard, char_list=None, display=None, display_group=None):
        # キーボードマッピングを取得
        char_to_keycode, needs_shift = get_keycode_mapping(KEYBOARD_LAYOUT)
        super().__init__(name, keyboard, char_list, char_to_keycode, needs_shift, display, display_group)

    def init_display(self):
        """
        基本モードのディスプレイレイアウトを初期化
        (prev, current, next)
        """
        if not self.display or self.display_group is None:
            return {}
        
        labels = {}
        
        # 前の文字を小さく表示（左側・左揃え）
        labels['prev'] = label.Label(
            terminalio.FONT, 
            text="", 
            color=0x888888, 
            scale=2,
            anchor_point=(0.0, 0.5),
            anchored_position=(10, DISPLAY_HEIGHT // 2)
        )
        self.display_group.append(labels['prev'])
        
        # 選択中の文字を大きく表示（中央・中央揃え）
        labels['current'] = label.Label(
            terminalio.FONT, 
            text="", 
            color=0xFFFFFF, 
            scale=4,
            anchor_point=(0.5, 0.5),
            anchored_position=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 4)
        )
        self.display_group.append(labels['current'])
        
        # 次の文字を小さく表示（右側・右揃え）
        labels['next'] = label.Label(
            terminalio.FONT, 
            text="", 
            color=0x888888, 
            scale=2,
            anchor_point=(1.0, 0.5),
            anchored_position=(DISPLAY_WIDTH - 10, DISPLAY_HEIGHT // 2)
        )
        self.display_group.append(labels['next'])

        # --- フッター ---
        # 左アクション
        labels['left_action'] = label.Label(
            terminalio.FONT,
            text="",  # 空文字で初期化
            color=0xAAAAAA,
            anchor_point=(0.0, 1.0),  # 左下
            anchored_position=(2, DISPLAY_HEIGHT - 2)
        )
        self.display_group.append(labels['left_action'])

        # 右アクション
        labels['right_action'] = label.Label(
            terminalio.FONT,
            text="",  # 空文字で初期化
            color=0xAAAAAA,
            anchor_point=(1.0, 1.0),  # 右下
            anchored_position=(DISPLAY_WIDTH - 2, DISPLAY_HEIGHT - 2)
        )
        self.display_group.append(labels['right_action'])
        
        return labels

    def update_footer_text(self, left_text, right_text):
        """フッターのテキストを更新する"""
        if 'left_action' in self.display_labels:
            self.display_labels['left_action'].text = left_text
        if 'right_action' in self.display_labels:
            self.display_labels['right_action'].text = right_text

    def handle_long_press(self):
        """長押しでユーティリティモードに切り替え"""
        return "Utility"
