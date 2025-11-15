# Music Archiver 音楽アーカイブツール

CDからリッピングした音楽ファイルを指定の場所にコピーし、Zip圧縮したうえでS3のDeepArchiveにアップロードする作業を自動化するGUIツールです。

## 機能

* **GUI操作**: フォルダ選択とS3バケット名を指定して「実行」するだけの簡単操作。
* **処理の自動化**: 以下の3ステップを自動で実行します。
    1.  指定ディレクトリ（コピー元）から指定ディレクトリ（コピー先）へファイルをコピー。
    2.  「コピー先」ディレクトリを丸ごとZip圧縮（ファイル名は `{コピー先ディレクトリ名}.zip`）。
    3.  作成したZipファイルを指定のS3バケットへアップロード。
* **設定ファイル**: AWS認証情報やS3ストレージクラスは `config.ini` で一元管理。

## セットアップ（準備）

本プロジェクトは [uv](https://github.com/astral-sh/uv) の使用を前提としています。`uv`がインストールされていない場合は、公式の手順に従いインストールしてください。

1.  **リポジトリのクローン**
    ```bash
    git clone [このリポジトリのURL]
    cd MusicArchiver
    ```

2.  **仮想環境の作成と有効化**
    `uv` を使って仮想環境（`.venv`）を作成し、有効化します。
    ```bash
    uv venv
    source .venv/bin/activate  # macOS/Linux
    .venv\Scripts\activate     # Windows
    ```

3.  **必要なライブラリのインストール**
    `uv` を使って `requirements.txt` からライブラリをインストールします。
    ```bash
    uv pip install -r requirements.txt
    ```

4.  **設定ファイルの作成**
    `config.ini.example` をコピーして `config.ini` という名前のファイルを作成します。
    ```bash
    cp config.ini.example config.ini  # macOS/Linux
    copy config.ini.example config.ini  # Windows
    ```
    作成した `config.ini` を開き、以下の情報を**必ず**設定してください。
    * `aws_access_key_id`
    * `aws_secret_access_key`
    * `aws_region`

## 使い方

1.  **スクリプトの実行**
    （仮想環境が有効化されていることを確認してください）
    ```bash
    python main.py
    ```

2.  **GUIの操作**
    1.  「コピー元」を選択します。
    2.  「コピー先」を選択します（この名前がZipファイル名にもなります）。
    3.  「S3バケット名」を入力します。
    4.  「実行」ボタンを押します。

## 実行ファイル (exe) の作成 (Windows)

このスクリプトを `main.exe` のような単一の実行ファイルに変換することも可能です。

1.  **PyInstallerのインストール**
    `uv` を使って、現在有効化されている仮想環境に `pyinstaller` をインストールします。
    ```bash
    uv pip install pyinstaller
    ```

2.  **実行ファイルのビルド**
    `pyinstaller` コマンドを使ってビルドします。
    ```bash
    pyinstaller --onefile --noconsole main.py
    ```

3.  **実行**
    `dist/` フォルダ内に `main.exe` が作成されます。
    **重要:** `main.exe` を実行するには、**`config.ini` ファイルが `main.exe` と同じフォルダに配置されている**必要があります。
