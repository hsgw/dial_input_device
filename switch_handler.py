# SPDX-FileCopyrightText: 2024 Your Name
# SPDX-License-Identifier: MIT

"""
スイッチハンドラー
ダブルクリック検出機能を持つスイッチ管理クラス
"""

import time
import digitalio


class SwitchHandler:
    """ダブルクリック検出機能を持つスイッチハンドラー"""
    
    def __init__(self, switch_pin, double_click_threshold=0.3, long_press_threshold=0.5):
        """
        Args:
            switch_pin: スイッチのピン
            double_click_threshold: ダブルクリック判定時間（秒）
            long_press_threshold: 長押し判定時間（秒）
        """
        # スイッチ (内部プルアップ抵抗を有効化)
        self.switch = digitalio.DigitalInOut(switch_pin)
        self.switch.direction = digitalio.Direction.INPUT
        self.switch.pull = digitalio.Pull.UP
        
        self.last_state = True  # 押されていない状態で初期化
        self.last_click_time = 0
        self.press_start_time = 0
        self.double_click_threshold = double_click_threshold
        self.long_press_threshold = long_press_threshold
        self.waiting_for_double_click = False
        self.long_press_active = False
    
    def update(self):
        """
        スイッチの状態を更新し、クリックイベントを検出
        
        Returns:
            str or None: イベントタイプ ('timeout', 'double', 'long_press', None)
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
                self.press_start_time = current_time
                self.long_press_active = False # Reset flag on new press
            
            # 離されたとき
            else:
                # 長押し済みでなければクリック処理へ
                if not self.long_press_active:
                    # ダブルクリック判定
                    is_double_click = self.waiting_for_double_click and (current_time - self.last_click_time) < self.double_click_threshold
                    
                    if is_double_click:
                        self.waiting_for_double_click = False
                        event = 'double'
                    else:
                        # 1回目のクリック: 待機状態にする
                        self.waiting_for_double_click = True
                        self.last_click_time = current_time
        
        # 長押しチェック (押されている間)
        if not current_state and not self.long_press_active:
            if (current_time - self.press_start_time) >= self.long_press_threshold:
                self.long_press_active = True
                self.waiting_for_double_click = False # Cancel potential click
                event = 'long_press'
        
        return event
