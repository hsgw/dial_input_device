# SPDX-FileCopyrightText: 2024 Your Name
# SPDX-License-Identifier: MIT

"""
モード管理システム
入力モードや削除モードなどを管理するクラス群
各モードがディスプレイの描画も管理
各モードが独自の状態（文字インデックスなど）を管理
"""

from adafruit_hid.keycode import Keycode


class Mode:
    """モードの基底クラス"""
    
    def __init__(self, name, keyboard, char_list, char_to_keycode, needs_shift, display=None, display_group=None):
        self.name = name
        self.keyboard = keyboard
        self.char_list = char_list
        self.char_to_keycode = char_to_keycode
        self.needs_shift = needs_shift
        self.display = display
        self.display_group = display_group
        self.last_rotation_direction = None
        
        # ディスプレイラベル（各モードで管理）
        self.display_labels = {}
        
        # モード固有の状態（サブクラスで初期化）
        self.state = {}
    
    def init_state(self):
        """
        モードの状態を初期化
        サブクラスでオーバーライドして独自の状態を初期化
        
        Returns:
            dict: 状態辞書（例: {'char_index': 0, 'counter': 0, ...}）
        """
        # デフォルト実装: 空の状態
        return {}
    
    def get_state(self, key, default=None):
        """
        状態を取得
        
        Args:
            key: 状態のキー
            default: デフォルト値
            
        Returns:
            状態の値
        """
        return self.state.get(key, default)
    
    def set_state(self, key, value):
        """
        状態を設定
        
        Args:
            key: 状態のキー
            value: 設定する値
        """
        self.state[key] = value
    
    def init_display(self):
        """
        ディスプレイのレイアウトを初期化
        サブクラスでオーバーライドして独自のレイアウトを作成
        
        Returns:
            dict: ラベル辞書 {'prev': label, 'current': label, 'next': label, ...}
        """
        # デフォルト実装: 何もしない（サブクラスで実装）
        return {}
    
    def cleanup_display(self):
        """
        ディスプレイのクリーンアップ
        モードから出るときにラベルを削除
        """
        if self.display_group:
            # すべてのラベルをグループから削除
            for label in self.display_labels.values():
                if label in self.display_group:
                    self.display_group.remove(label)
        self.display_labels = {}
    
    def on_enter(self):
        """モードに入ったときの処理"""
        print(f"Mode: {self.name}")
        self.last_rotation_direction = None
        
        # 状態を初期化
        self.state = self.init_state()
        
        # ディスプレイを初期化
        if self.display and self.display_group is not None:
            self.display_labels = self.init_display()
        
        self.update_display_mode()
    
    def on_exit(self):
        """モードから出るときの処理"""
        # ディスプレイをクリーンアップ
        self.cleanup_display()
    
    def update_display_mode(self):
        """
        モード名や状態をディスプレイに表示
        サブクラスでオーバーライド可能
        """
        pass
    
    def update_display_state(self):
        """
        モードの状態に基づいてディスプレイを更新
        サブクラスでオーバーライド可能
        """
        # デフォルト実装: 何もしない
        pass
    
    def handle_rotation(self, delta):
        """
        エンコーダ回転時の処理
        
        Args:
            delta: 回転量
            
        Returns:
            bool: 何か処理を行ったかどうか
        """
        return False
    
    def handle_single_click(self):
        """
        シングルクリック時の処理
        
        Returns:
            str or None: 次のモード名（Noneの場合は変更なし）
        """
        return None
    
    def handle_double_click(self):
        """
        ダブルクリック時の処理
        
        Returns:
            str or None: 次のモード名（Noneの場合は変更なし）
        """
        return None
    
    def send_key(self, char, use_shift=False):
        """キーを送信するヘルパーメソッド"""
        if char in self.char_to_keycode:
            keycode = self.char_to_keycode[char]
            if use_shift or char in self.needs_shift:
                self.keyboard.send(keycode, Keycode.SHIFT)
            else:
                self.keyboard.send(keycode)
            return True
        return False


class ModeManager:
    """モード管理クラス"""
    
    def __init__(self, display=None, display_group=None):
        self.modes = {}
        self.current_mode = None
        self.display = display
        self.display_group = display_group
    
    def add_mode(self, mode):
        """モードを追加"""
        self.modes[mode.name] = mode
    
    def set_mode(self, mode_name):
        """モードを切り替え"""
        if mode_name in self.modes:
            if self.current_mode:
                self.current_mode.on_exit()
            self.current_mode = self.modes[mode_name]
            self.current_mode.on_enter()
        else:
            print(f"Warning: Mode '{mode_name}' not found")
    
    def handle_rotation(self, delta):
        """現在のモードで回転を処理"""
        if self.current_mode:
            result = self.current_mode.handle_rotation(delta)
            # ディスプレイを更新
            self.current_mode.update_display_state()
            return result
        return False
    
    def handle_single_click(self):
        """現在のモードでシングルクリックを処理"""
        if self.current_mode:
            next_mode = self.current_mode.handle_single_click()
            if next_mode:
                self.set_mode(next_mode)
    
    def handle_double_click(self):
        """現在のモードでダブルクリックを処理"""
        if self.current_mode:
            next_mode = self.current_mode.handle_double_click()
            if next_mode:
                self.set_mode(next_mode)
