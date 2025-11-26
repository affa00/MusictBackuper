# config.py
import configparser
import os

# ホームディレクトリ配下に設定用フォルダを指定
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".MusicArchiver")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")

config = configparser.ConfigParser()

# グローバル変数として設定値を保持
STORAGE_CLASS = None
ZIP_TEMP_DIR = None

def load_config():
    """設定ファイルを読み込み、グローバル変数を更新する"""
    global STORAGE_CLASS, ZIP_TEMP_DIR
    
    if not os.path.exists(CONFIG_FILE):
        return False # 読み込み失敗（ファイルなし）

    try:
        config.read(CONFIG_FILE, encoding='utf-8')
                
        STORAGE_CLASS = config.get('DEFAULT', 's3_storage_class', fallback='DEEP_ARCHIVE')
        ZIP_TEMP_DIR = config.get('DEFAULT', 'zip_temp_dir', fallback='.')
        
        return True # 読み込み成功

    except Exception:
        return False # その他の読み込みエラー

def save_config(settings):
    """
    辞書形式で受け取った設定を config.ini に保存し、
    グローバル変数も更新する。
    """
    global STORAGE_CLASS, ZIP_TEMP_DIR

    config['DEFAULT'] = {
        's3_storage_class': settings['storage_class'],
        'zip_temp_dir': settings['zip_temp_dir']
    }
    
    try:
        # 設定ディレクトリが存在しない場合は作成
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        # グローバル変数も即時更新
        STORAGE_CLASS = settings['storage_class']
        ZIP_TEMP_DIR = settings['zip_temp_dir']
        
        return True
    except Exception as e:
        print(f"設定の保存エラー: {e}")
        return False

# -------------------------------------------------
# スクリプト（モジュール）読み込み時に一度ロードを試みる
# -------------------------------------------------
config_loaded = load_config()
