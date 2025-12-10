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
            str or None: イベントタイプ ('timeout', 'double', None)
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
