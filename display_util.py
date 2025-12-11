def get_display_char(char):
    """表示用の文字を取得（スペース等を可視化）"""
    if char == ' ':
        return 'SP'  # terminalio.FONTはASCII基本セットのみのため'SP'で代用
    elif char == '\n':
        return 'EN'  # Enter/改行を'EN'で表示
    return char