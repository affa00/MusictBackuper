# config.py
import configparser
import os

# ホームディレクトリ配下に設定用フォルダを指定
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".MusicArchiver")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")

config = configparser.ConfigParser()

# グローバル変数として設定値を保持
AWS_KEY = None
AWS_SECRET = None
AWS_REGION = None
STORAGE_CLASS = None
ZIP_TEMP_DIR = None

def load_config():
    """設定ファイルを読み込み、グローバル変数を更新する"""
    global AWS_KEY, AWS_SECRET, AWS_REGION, STORAGE_CLASS, ZIP_TEMP_DIR
    
    if not os.path.exists(CONFIG_FILE):
        return False # 読み込み失敗（ファイルなし）

    try:
        config.read(CONFIG_FILE, encoding='utf-8')
        
        AWS_KEY = config.get('AWS', 'aws_access_key_id', fallback=None)
        AWS_SECRET = config.get('AWS', 'aws_secret_access_key', fallback=None)
        AWS_REGION = config.get('AWS', 'aws_region', fallback='ap-northeast-1')
        
        STORAGE_CLASS = config.get('DEFAULT', 's3_storage_class', fallback='DEEP_ARCHIVE')
        ZIP_TEMP_DIR = config.get('DEFAULT', 'zip_temp_dir', fallback='.')
        
        if not all([AWS_KEY, AWS_SECRET]):
            return False # 必須項目が欠落

        return True # 読み込み成功

    except Exception:
        return False # その他の読み込みエラー

def save_config(settings):
    """
    辞書形式で受け取った設定を config.ini に保存し、
    グローバル変数も更新する。
    """
    global AWS_KEY, AWS_SECRET, AWS_REGION, STORAGE_CLASS, ZIP_TEMP_DIR

    config['AWS'] = {
        'aws_access_key_id': settings['aws_key'],
        'aws_secret_access_key': settings['aws_secret'],
        'aws_region': settings['aws_region']
    }
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
        AWS_KEY = settings['aws_key']
        AWS_SECRET = settings['aws_secret']
        AWS_REGION = settings['aws_region']
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
