# SPDX-FileCopyrightText: 2024 Your Name
# SPDX-License-Identifier: MIT

"""
ユーティリティモード
長押しで起動し、BackspaceとSpaceを入力可能
"""

from config import DISPLAY_WIDTH, DISPLAY_HEIGHT
import terminalio
from adafruit_display_text import label
from adafruit_hid.keycode import Keycode
from mode_manager import Mode


class UtilityMode(Mode):
    """
    ユーティリティモード
    左回転: Backspace
    右回転: Space
    逆回転: 前のモードに戻る
    """
    
    def __init__(self, keyboard, display=None, display_group=None):
        super().__init__("Utility", keyboard, display=display, display_group=display_group)
    
    def init_state(self):
        """状態を初期化"""
        return {
            'current_action': None  # 'BS' or 'SP' or None
        }
    
    def init_display(self):
        """ディスプレイレイアウトを初期化"""
        if not self.display or self.display_group is None:
            return {}
        
        labels = {}
        
        # Backspaceラベル（左側）
        labels['bs'] = label.Label(
            terminalio.FONT, 
            text="BS", 
            color=0x888888, 
            scale=2,
            anchor_point=(0.0, 0.5),
            anchored_position=(10, DISPLAY_HEIGHT // 2)
        )
        self.display_group.append(labels['bs'])
        
        # Spaceラベル（右側）
        labels['sp'] = label.Label(
            terminalio.FONT, 
            text="SP", 
            color=0x888888, 
            scale=2,
            anchor_point=(1.0, 0.5),
            anchored_position=(DISPLAY_WIDTH - 10, DISPLAY_HEIGHT // 2)
        )
        self.display_group.append(labels['sp'])
        
        return labels
    
    def update_display_state(self):
        """状態に基づいてディスプレイを更新"""
        if not self.display or not self.display_labels:
            return
        
        current_action = self.get_state('current_action')
        
        # アクティブなアクションをハイライト
        if current_action == 'BS':
            self.display_labels['bs'].color = 0xFFFFFF
            self.display_labels['bs'].scale = 4
            self.display_labels['sp'].color = 0x888888
            self.display_labels['sp'].scale = 2
        elif current_action == 'SP':
            self.display_labels['bs'].color = 0x888888
            self.display_labels['bs'].scale = 2
            self.display_labels['sp'].color = 0xFFFFFF
            self.display_labels['sp'].scale = 4
        else:
            # どちらも非アクティブ（初期状態）
            self.display_labels['bs'].color = 0xFFFFFF
            self.display_labels['bs'].scale = 2
            self.display_labels['sp'].color = 0xFFFFFF
            self.display_labels['sp'].scale = 2
    
    def handle_rotation(self, delta):
        """
        回転処理
        
        Returns:
            str or None: 次のモード名（Noneの場合は変更なし）
        """
        current_action = self.get_state('current_action')
        direction = 'SP' if delta > 0 else 'BS'
        
        if current_action is None:
            # 最初のアクション決定
            self.set_state('current_action', direction)
            self._execute_action(direction)
            return None
            
        elif current_action == direction:
            # 同じ方向なら連続入力
            self._execute_action(direction)
            return None
            
        else:
            # 逆方向なら前のモードに戻る
            pass
            
            return "__PREVIOUS__"
            
    def handle_single_click(self):
        """
        シングルクリック処理
        SP選択時はEnterを入力して前のモードに戻る
        """
        current_action = self.get_state('current_action')
        if current_action == 'SP':
            self.keyboard.send(Keycode.ENTER)
            print("Sent: Enter")
            return "__PREVIOUS__"
        return None
    
    def handle_double_click(self):
        """
        ダブルクリック処理
        前のモードに戻る
        """
        return "__PREVIOUS__"
        
    def _execute_action(self, action):
        """アクションを実行"""
        if action == 'BS':
            self.keyboard.send(Keycode.BACKSPACE)
            print("Sent: Backspace")
        elif action == 'SP':
            self.keyboard.send(Keycode.SPACE)
            print("Sent: Space")
