# Music Archiver 音楽アーカイブツール

CDからリッピングした音楽ファイルを指定の場所にコピーし、Zip圧縮したうえでS3のDeepArchiveにアップロードする作業を自動化するGUIツールです。

**OSS (Tkinter)** で実装されています。

## ✨ 機能

* **GUI操作**: フォルダ選択とS3バケット名を指定して「実行」するだけの簡単操作。
* **初回設定ウィザード**: 初回起動時に`config.ini`が存在しない場合、自動で設定ウィンドウが開き、AWS認証情報などを設定できます。
* **設定変更**: メイン画面の「設定変更」ボタンから、いつでも`config.ini`の内容を更新できます。
* **非同期処理**: ファイルコピーやアップロード中もGUIが固まりません。
* **処理の自動化**: 以下の3ステップを自動で実行します。
    1.  指定ディレクトリ（コピー元）から指定ディレクトリ（コピー先）へファイルをコピー。
    2.  「コピー先」ディレクトリを丸ごとZip圧縮（ファイル名は `{コピー先ディレクトリ名}.zip`）。
    3.  作成したZipファイルを指定のS3バケットへアップロード。

## 🔧 セットアップ（準備）

本プロジェクトは [uv](https://github.com/astral-sh/uv) の使用を前提としています。`uv`がインストールされていない場合は、公式の手順に従いインストールしてください。

1.  **リポジトリのクローン**
    ```bash
    git clone [このリポジトリのURL]
    cd MusicArchiver
    ```

2.  **仮想環境の作成と有効化**
    ```bash
    uv venv
    source .venv/bin/activate  # macOS/Linux
    .venv\Scripts\activate     # Windows
    ```

3.  **必要なライブラリのインストール**
    （Tkinterは標準ライブラリのため、`boto3`のみインストールします）
    ```bash
    uv pip install -r requirements.txt
    ```

## 🚀 使い方

1.  **スクリプトの実行**
    （仮想環境が有効化されていることを確認してください）
    ```bash
    python main.py
    ```

2.  **初回設定（初回起動時のみ）**
    * 起動時に設定ウィンドウが開きます。
    * 「AWS Access Key ID」「AWS Secret Access Key」などの必須情報を入力し、「保存」を押してください。
    * 設定内容は `config.ini` ファイルとして保存されます。

3.  **GUIの操作**
    1.  「コピー元」を選択します。
    2.  「コピー先」を選択します（この名前がZipファイル名にもなります）。
    3.  「S3バケット名」を入力します。
    4.  「実行」ボタンを押します。

## 📦 実行ファイル (exe) の作成 (Windows)

1.  **PyInstallerのインストール**
    ```bash
    uv pip install pyinstaller
    ```

2.  **実行ファイルのビルド**
    `main.py`は`tkinter`に依存しているため、`--noconsole`（コンソール非表示）オプションが適切です。
    ```bash
    pyinstaller --onefile --noconsole main.py
    ```

3.  **実行**
    `dist/` フォルダ内に `main.exe` が作成されます。`main.exe` を実行すると、`config.ini` が `main.exe` と同じフォルダに作成・保存されます。
