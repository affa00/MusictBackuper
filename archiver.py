# archiver.py
import os
import shutil
import zipfile
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# config.py から設定をインポート
try:
    from config import AWS_KEY, AWS_SECRET, AWS_REGION, STORAGE_CLASS, ZIP_TEMP_DIR
except ImportError:
    print("エラー: config.py が見つからないか、設定が不完全です。")
    sys.exit(1)

def perform_archive(source_dir, target_dir, s3_bucket, status_callback):
    """
    メインのアーカイブ処理（コピー、Zip、S3アップロード）を実行する。
    進捗は status_callback 関数を通じてGUIに通知する。
    """
    try:
        # --- 1. ファイルのコピー ---
        status_callback("1/3: ファイルをコピーしています...")
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # source_dirの中身をtarget_dirにコピー
        for item in os.listdir(source_dir):
            s = os.path.join(source_dir, item)
            d = os.path.join(target_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks=False, ignore=None)
            else:
                shutil.copy2(s, d)

        status_callback("1/3: コピー完了。")

        # --- 2. Zipファイルの作成 ---
        status_callback("2/3: Zipファイルを作成しています...")
        
        target_dir_name = os.path.basename(os.path.normpath(target_dir))
        zip_filename = f"{target_dir_name}.zip"
        zip_output_path = os.path.join(ZIP_TEMP_DIR, zip_filename)

        shutil.make_archive(
            base_name=os.path.join(ZIP_TEMP_DIR, target_dir_name),
            format='zip',
            root_dir=os.path.dirname(target_dir),
            base_dir=target_dir_name
        )

        status_callback(f"2/3: Zip作成完了 ({zip_filename})")

        # --- 3. S3へのアップロード ---
        status_callback("3/3: S3にアップロードしています...")

        session = boto3.Session(
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET,
            region_name=AWS_REGION
        )
        s3 = session.client('s3')

        s3.upload_file(
            zip_output_path,
            s3_bucket,
            zip_filename,
            ExtraArgs={'StorageClass': STORAGE_CLASS}
        )

        status_callback(f"完了: {zip_filename} を {s3_bucket} にアップロードしました。")
        return True, "処理が正常に完了しました。"

    except NoCredentialsError:
        error_msg = "S3認証情報が見つかりません。config.iniを確認してください。"
        status_callback(f"エラー: {error_msg}")
        return False, error_msg
    except ClientError as e:
        error_msg = f"S3アップロードエラー: {e}"
        status_callback(f"エラー: {error_msg}")
        return False, error_msg
    except FileNotFoundError as e:
        error_msg = f"ファイルが見つかりません: {e}"
        status_callback(f"エラー: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"予期せぬエラーが発生しました: {e}"
        status_callback(f"エラー: {error_msg}")
        return False, error_msg
