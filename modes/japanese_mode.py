# SPDX-FileCopyrightText: 2024 Your Name
# SPDX-License-Identifier: MIT

"""
日本語入力モード (Japanese Input Mode)
ローマ字入力用。2つのリスト（子音・母音）を回転方向で切り替えて選択する。
"""

from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, KEYBOARD_LAYOUT
import terminalio
from adafruit_display_text import label
from adafruit_hid.keycode import Keycode
from mode_manager import Mode
from keyboard_mapping import get_keycode_mapping


class JapaneseMode(Mode):
    """
    日本語入力モード
    左回転: 母音リスト (A, I, U, E, O)
    右回転: 子音リスト (K, S, T, ...)
    逆回転: 直前の選択を入力し、新しいリスト操作へ切り替え
    クリック: 現在の選択を入力し、操作状態をリセット
    """
    
    # 母音リスト (左回転用)
    VOWELS = ['a', 'i', 'u', 'e', 'o']
    
    # 子音リスト (右回転用)
    CONSONANTS = ['k', 's', 't', 'n', 'h', 'm', 'y', 'r', 'w', 'g', 'z', 'd', 'b', 'p']
    
    # キーコードマッピング（簡易版: a-zのみ対応）
    # 記号などが必要な場合は keyboard_mapping.py を拡張して使うか、ここで定義する
    
    def __init__(self, keyboard, display=None, display_group=None):
        super().__init__("Japanese", keyboard, display=display, display_group=display_group)
        
        # キーボードマッピングを取得
        self.char_to_keycode, self.needs_shift = get_keycode_mapping(KEYBOARD_LAYOUT)
        
        # リストの拡張 (インスタンス属性として上書き)
        # 母音側: 数字 (1-0)
        self.VOWELS = self.VOWELS + ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        
        # 子音側: 記号
        self.CONSONANTS = self.CONSONANTS + ['.', ',', '-', '/', '!', '?', '@', '_', ' ', '\n']
        
    def on_enter(self, reset=False):
        """モードに入ったときの処理"""
        super().on_enter(reset=reset)
        # Utilityモード等から戻った時も、常にニュートラル状態で開始する
        self.set_state('is_neutral', True)
    
    def init_state(self):
        """状態を初期化"""
        return {
            'consonant_index': 0,
            'vowel_index': 0,
            # last_direction states:
            #  1: Active Right (Consonant)
            # -1: Active Left (Vowel)
            #  2: Neutral Right (Last selection was Consonant)
            'active_side': 'vowel', # 'vowel' or 'consonant'
            'is_neutral': True      # True: 選択待機中(リセット直後), False: 選択中
        }
    
    def init_display(self):
        """ディスプレイレイアウトを初期化 (Basic Mode準拠)"""
        if not self.display or self.display_group is None:
            return {}
        
        labels = {}
        
        # 前の文字/左選択候補（左側）
        labels['prev'] = label.Label(
            terminalio.FONT, 
            text="", 
            color=0x888888, 
            scale=2,
            anchor_point=(0.0, 0.5),
            anchored_position=(10, DISPLAY_HEIGHT // 2)
        )
        self.display_group.append(labels['prev'])
        
        # 現在の文字（中央）
        labels['current'] = label.Label(
            terminalio.FONT, 
            text="", 
            color=0xFFFFFF, 
            scale=4,
            anchor_point=(0.5, 0.5),
            anchored_position=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 4)
        )
        self.display_group.append(labels['current'])
        
        # 次の文字/右選択候補（右側）
        labels['next'] = label.Label(
            terminalio.FONT, 
            text="", 
            color=0x888888, 
            scale=2,
            anchor_point=(1.0, 0.5),
            anchored_position=(DISPLAY_WIDTH - 10, DISPLAY_HEIGHT // 2)
        )
        self.display_group.append(labels['next'])
        
        return labels

    def _get_display_char(self, char):
        """表示用の文字を取得（スペース等を可視化）"""
        if char == ' ':
            return 'SP'  # terminalio.FONTはASCII基本セットのみのため'SP'で代用
        elif char == '\n':
            return 'EN'  # Enter/改行を'EN'で表示
        return char

    def update_display_state(self):
        """状態に基づいてディスプレイを更新"""
        if not self.display or not self.display_labels:
            return
        
        c_index = self.get_state('consonant_index')
        v_index = self.get_state('vowel_index')
        active_side = self.get_state('active_side')
        is_neutral = self.get_state('is_neutral')
        
        center_text = ""
        left_text = ""
        right_text = ""
        
        # 中央（現在の選択）
        if active_side == 'vowel':
            center_text = self.VOWELS[v_index]
        else:
            center_text = self.CONSONANTS[c_index]
            
        # 左右の表示
        if is_neutral:
            # ニュートラル状態
            
            # 左（母音）: アクティブなら次の文字、非アクティブ（切り替え）なら現在の文字
            if active_side == 'vowel':
                left_text = self.VOWELS[(v_index + 1) % len(self.VOWELS)]
            else:
                left_text = self.VOWELS[v_index]
                
            # 右（子音）: アクティブなら次の文字、非アクティブ（切り替え）なら現在の文字
            if active_side == 'consonant':
                right_text = self.CONSONANTS[(c_index + 1) % len(self.CONSONANTS)]
            else:
                right_text = self.CONSONANTS[c_index]
            
        elif active_side == 'vowel': # Active Left
            # 母音リスト内での前後 (左回転でindex増)
            left_text = self.VOWELS[(v_index + 1) % len(self.VOWELS)]
            right_text = self.VOWELS[(v_index - 1) % len(self.VOWELS)]
            
        elif active_side == 'consonant': # Active Right
            # 子音リスト内での前後
            left_text = self.CONSONANTS[(c_index - 1) % len(self.CONSONANTS)]
            right_text = self.CONSONANTS[(c_index + 1) % len(self.CONSONANTS)]
            
        # 更新 (表示用文字に変換)
        if 'current' in self.display_labels:
            self.display_labels['current'].text = self._get_display_char(center_text).upper()
        if 'prev' in self.display_labels:
            self.display_labels['prev'].text = self._get_display_char(left_text).upper()
        if 'next' in self.display_labels:
            self.display_labels['next'].text = self._get_display_char(right_text).upper()


    def handle_rotation(self, delta):
        """回転処理"""
        direction = 1 if delta > 0 else -1
        
        # 現在の状態取得
        current_side = self.get_state('active_side')
        is_neutral = self.get_state('is_neutral')
        c_index = self.get_state('consonant_index')
        v_index = self.get_state('vowel_index')
        
        # 回転方向に対応するサイド（ターゲット）
        target_side = 'consonant' if direction == 1 else 'vowel'
        
        # サイド変更があるか（ニュートラルかどうかに関わらず）
        switching_side = (target_side != current_side)
        
        # 1. 入力判定（非ニュートラル かつ サイド変更時）
        if not is_neutral and switching_side:
            # 現在のサイドの文字を入力
            target_char = ""
            if current_side == 'consonant':
                target_char = self.CONSONANTS[c_index]
            else:
                target_char = self.VOWELS[v_index]
            self._send_char(target_char)
            
        # 2. リセット判定（子音から母音への切り替え時）
        # Active中の切り替え、およびNeutral(クリック)後の切り替えの両方で有効
        if current_side == 'consonant' and target_side == 'vowel':
             v_index = 0
             self.set_state('vowel_index', v_index)

        # 3. インデックス更新
        # 「同じリストの場合はすぐに次の文字を選択」 -> switching_side == False なら更新
        # 「リストの変更があった場合は...以前のインデックス（ホールド）」 -> switching_side == True なら更新しない
        if not switching_side:
            if target_side == 'consonant':
                c_index = (c_index + 1) % len(self.CONSONANTS)
                self.set_state('consonant_index', c_index)
            else: # vowel (左回転で順送り)
                v_index = (v_index + 1) % len(self.VOWELS)
                self.set_state('vowel_index', v_index)
        
        # 4. 新しい状態を保存
        self.set_state('active_side', target_side)
        self.set_state('is_neutral', False)
        
        return None

    def handle_single_click(self):
        """クリック処理：現在の選択を入力してリセット"""
        active_side = self.get_state('active_side')
        
        target_char = ""
        if active_side == 'consonant':
            target_char = self.CONSONANTS[self.get_state('consonant_index')]
        else:
            target_char = self.VOWELS[self.get_state('vowel_index')]
        
        if target_char:
            self._send_char(target_char)
        
        # ニュートラル状態へ移行（サイドは維持）
        self.set_state('is_neutral', True)
        return None
    
    def handle_double_click(self):
        """ダブルクリック：エンターキー送信＆初期状態リセット"""
        self.keyboard.send(Keycode.ENTER)
        print("Sent: ENTER (Double Click)")
        
        # 完全リセット
        self.set_state('consonant_index', 0)
        self.set_state('vowel_index', 0)
        self.set_state('active_side', 'vowel')
        self.set_state('is_neutral', True)
        
        return None
    
    def _send_char(self, char_str):
        """文字を送信（マッピング対応）"""
        if not char_str:
            return
            
        char_lower = char_str.lower()
        
        # マッピングからキーコードを取得
        keycode = self.char_to_keycode.get(char_lower)
        
        if keycode:
            # Shiftが必要かチェック
            needs_shift = char_lower in self.needs_shift
            
            # Shift付きで送信
            if needs_shift:
                self.keyboard.send(Keycode.SHIFT, keycode)
            else:
                self.keyboard.send(keycode)
                
            print(f"Sent: {char_str} (Keycode: {keycode}, Shift: {needs_shift})")
        else:
            print(f"Warning: No mapping for character '{char_str}'")
