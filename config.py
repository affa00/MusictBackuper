# config.py
import configparser
import sys
import PySimpleGUI as sg

# 設定パーサーの初期化
config = configparser.ConfigParser()

try:
    # config.iniをUTF-8で読み込む
    config.read('config.ini', encoding='utf-8')

    # [AWS] セクション
    AWS_KEY = config['AWS']['aws_access_key_id']
    AWS_SECRET = config['AWS']['aws_secret_access_key']
    AWS_REGION = config['AWS']['aws_region']

    # [DEFAULT] セクション
    STORAGE_CLASS = config['DEFAULT']['s3_storage_class']
    ZIP_TEMP_DIR = config['DEFAULT']['zip_temp_dir']

    # 必須項目が空でないかチェック
    if not all([AWS_KEY, AWS_SECRET, AWS_REGION]):
        raise KeyError("AWSの認証情報がconfig.iniに設定されていません。")

except KeyError as e:
    sg.popup_error(
        f"config.iniの読み込みエラー:\n{e}\n"
        "config.ini.exampleをコピーして、\n"
        "config.iniに必要な情報を設定してください。",
        title="設定エラー"
    )
    sys.exit()
except Exception as e:
    sg.popup_error(f"config.iniの読み込み中に予期せぬエラー: {e}", title="設定エラー")
    sys.exit()
