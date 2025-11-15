# main.py
import PySimpleGUI as sg
import os
import sys

# archiver.py から処理関数をインポート
# config.py もここでインポートして、起動時に設定をチェックする
try:
    import config 
    from archiver import perform_archive
except ImportError as e:
    sg.popup_error(f"起動エラー: 必要なファイルが見つかりません。\n{e}", title="起動エラー")
    sys.exit(1)
except SystemExit:
    sys.exit(1) # config.pyでのエラー終了


# --- GUIレイアウト ---
sg.theme('SystemDefault')

layout = [
    [sg.Text("音楽アーカイブツール", font=("Helvetica", 16))],
    [sg.Text("1. 現在の音楽ディレクトリ (コピー元):")],
    [sg.InputText(key='-SOURCE-', readonly=True), sg.FolderBrowse("選択")],
    [sg.Text("2. 移行先のディレクトリ (コピー先 & Zip名):")],
    [sg.InputText(key='-TARGET-', readonly=True), sg.FolderBrowse("選択")],
    [sg.Text("3. アップロード先 S3バケット名:")],
    [sg.InputText(key='-BUCKET-')],
    [sg.HorizontalSeparator()],
    [sg.Button("実行", key="-RUN-", size=(10, 2)), sg.Button("終了", key="-EXIT-")],
    [sg.Text("ステータス: 待機中", key='-STATUS-', size=(60, 1))]
]

window = sg.Window("Music Archiver", layout, finalize=True)

# --- イベントループ ---
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == "-EXIT-":
        break

    if event == "-RUN-":
        # 入力値のバリデーション
        source = values['-SOURCE-']
        target = values['-TARGET-']
        bucket = values['-BUCKET-']

        if not source or not target or not bucket:
            sg.popup_error("すべてのフィールド（コピー元、コピー先、S3バケット）を入力してください。")
            continue
        
        if not os.path.exists(source):
            sg.popup_error("指定された「コピー元」ディレクトリが存在しません。")
            continue

        # 確認ポップアップ
        confirm_text = f"""以下の操作を実行しますか？

1. コピー元: {source}
2. コピー先: {target}
3. Zip作成: {os.path.basename(os.path.normpath(target))}.zip
4. S3アップロード: s3://{bucket}/
"""
        if sg.popup_yes_no(confirm_text, title="実行確認") == "Yes":
            
            # ステータス更新用コールバック関数
            def update_status_display(message):
                window['-STATUS-'].update(message)
                window.refresh() # GUIを強制的に更新

            # 処理中はボタンを無効化
            window['-RUN-'].update(disabled=True)
            
            # メイン処理の呼び出し
            success, message = perform_archive(source, target, bucket, update_status_display)
            
            # 処理完了後ボタンを有効化
            window['-RUN-'].update(disabled=False)

            # エラーがあった場合はポップアップで通知
            if not success:
                sg.popup_error(f"処理中にエラーが発生しました:\n{message}", title="実行エラー")

window.close()