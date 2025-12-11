# SPDX-FileCopyrightText: 2024 Your Name
# SPDX-License-Identifier: MIT

"""
ユーティリティモード
- 通常時: BackspaceとSpaceを入力可能
- 長押し: モード切り替えメニューを表示
"""

from config import DISPLAY_WIDTH, DISPLAY_HEIGHT
import terminalio
from adafruit_display_text import label
from adafruit_hid.keycode import Keycode
from mode_manager import Mode

class UtilityMode(Mode):
    """
    ユーティリティモード
    - 回転なしでクリック: 前のモードに戻る
    - 回転あり:
      - 左回転: Backspace
      - 右回転: Space
    - 長押し: モード選択メニューを開く
    """
    
    MENU_ITEMS = ["Basic", "Japanese"]

    def __init__(self, keyboard, display=None, display_group=None):
        super().__init__("Utility", keyboard, display=display, display_group=display_group)

    def on_enter(self, reset=True):
        """モードに入ったときの処理"""
        super().on_enter(reset)
        # on_enterで状態をリセット
        self.set_state('rotated_since_enter', False)
        # サブモードを 'action' に設定
        self.set_state('sub_mode', 'action')
        # last_action_directionもリセット
        self.set_state('last_action_direction', None)
        self.update_display_state() # 表示を更新

    def init_state(self):
        """状態を初期化"""
        return {
            'current_action': None,  # 'BS' or 'SP'
            'rotated_since_enter': False,
            'sub_mode': 'action',  # 'action' or 'menu'
            'selected_menu_index': 0,
            'last_action_direction': None, # 新たに追加: 最後に選択したアクションの方向 (BS/SP)
        }

    def init_display(self):
        """ディスプレイレイアウトを初期化"""
        if not self.display or self.display_group is None:
            return {}
        
        labels = {}
        
        # Action Mode Labels
        labels['bs'] = label.Label(terminalio.FONT, text="BS", color=0xFFFFFF, scale=2, anchor_point=(0.0, 0.5), anchored_position=(10, DISPLAY_HEIGHT // 2))
        labels['sp'] = label.Label(terminalio.FONT, text="SP", color=0xFFFFFF, scale=2, anchor_point=(1.0, 0.5), anchored_position=(DISPLAY_WIDTH - 10, DISPLAY_HEIGHT // 2))
        
        # Menu Mode Labels
        labels['menu_title'] = label.Label(terminalio.FONT, text="< Menu >", color=0xFFFFFF, scale=1, anchor_point=(0.5, 0.0), anchored_position=(DISPLAY_WIDTH // 2, 5))
        labels['menu_item'] = label.Label(terminalio.FONT, text="", color=0xFFFFFF, scale=1, anchor_point=(0.5, 0.5), anchored_position=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 + 5))

        for l in labels.values():
            self.display_group.append(l)

        return labels

    def update_display_state(self):
        """状態に基づいてディスプレイを更新"""
        if not self.display or not self.display_labels:
            return

        sub_mode = self.get_state('sub_mode')

        # ラベルの表示/非表示を切り替え
        self.display_labels['bs'].hidden = (sub_mode != 'action')
        self.display_labels['sp'].hidden = (sub_mode != 'action')
        self.display_labels['menu_title'].hidden = (sub_mode != 'menu')
        self.display_labels['menu_item'].hidden = (sub_mode != 'menu')

        if sub_mode == 'action':
            current_action = self.get_state('current_action')
            self.display_labels['bs'].color = 0xFFFFFF if current_action == 'BS' else 0x888888
            self.display_labels['bs'].scale = 4 if current_action == 'BS' else 2
            self.display_labels['sp'].color = 0xFFFFFF if current_action == 'SP' else 0x888888
            self.display_labels['sp'].scale = 4 if current_action == 'SP' else 2
        elif sub_mode == 'menu':
            index = self.get_state('selected_menu_index')
            self.display_labels['menu_item'].text = self.MENU_ITEMS[index]

    def handle_rotation(self, delta):
        """回転処理"""
        self.set_state('rotated_since_enter', True)
        sub_mode = self.get_state('sub_mode')

        if sub_mode == 'action':
            direction = 'SP' if delta > 0 else 'BS'
            last_action_direction = self.get_state('last_action_direction')

            if last_action_direction is not None and last_action_direction != direction:
                # 逆回転が検出されたら前のモードに戻る
                if self.get_state('last_action_direction') == 'SP':
                    self.keyboard.send(Keycode.ENTER)
                    print("Sent: Enter")
                    print("Return to previous mode")
                self.set_state('current_action', None) # 状態をリセット
                self.set_state('last_action_direction', None) # 状態をリセット
                return "__PREVIOUS__"
            
            # 同じ方向なら連続入力、または最初のアクション
            self.set_state('current_action', direction)
            self._execute_action(direction)
            self.set_state('last_action_direction', direction) # 最後に実行したアクションの方向を保存

        elif sub_mode == 'menu':
            index = self.get_state('selected_menu_index')
            index = (index + delta) % len(self.MENU_ITEMS)
            self.set_state('selected_menu_index', index)
        
        return None

    def handle_single_click(self):
        """シングルクリック処理"""
        if not self.get_state('rotated_since_enter'):
            return "__PREVIOUS__"

        sub_mode = self.get_state('sub_mode')
        if sub_mode == 'action':
            current_action = self.get_state('current_action')
            if current_action == 'SP':
                self.keyboard.send(Keycode.ENTER)
                print("Sent: Enter")
            elif current_action == 'BS':
                self.keyboard.send(Keycode.BACKSPACE)
                print("Sent: Backspace")
            return None # アクションモードではクリックでモードを抜けない
        elif sub_mode == 'menu':
            index = self.get_state('selected_menu_index')
            return self.MENU_ITEMS[index]

    def handle_long_press(self):
        """長押しでメニューモードに切り替え"""
        self.set_state('sub_mode', 'menu')
        return None # モードは変更しない

    def handle_double_click(self):
        """ダブルクリックで前のモードに戻る"""
        return "__PREVIOUS__"

    def _execute_action(self, action):
        """アクションを実行"""
        if action == 'BS':
            self.keyboard.send(Keycode.BACKSPACE)
            print("Sent: Backspace")
        elif action == 'SP':
            self.keyboard.send(Keycode.SPACE)
            print("Sent: Space")