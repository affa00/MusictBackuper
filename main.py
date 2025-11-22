# main.py
import textwrap
import tkinter as tk
from tkinter import ttk  # テーマ付きウィジェット
from tkinter import filedialog, messagebox
import threading
import queue
import os
import sys

try:
    import config
    from archiver import perform_archive
except ImportError as e:
    messagebox.showerror("起動エラー", f"必要なファイルが見つかりません:\n{e}")
    sys.exit(1)

# --- 設定ウィンドウ ---
def show_settings_window(parent):
    """設定入力ウィンドウを表示し、保存する (モーダル)"""
    
    settings_win = tk.Toplevel(parent)
    settings_win.title("設定 (config.ini)")
    
    # --- ウィンドウサイズ指定 (拡大) ---
    settings_win.geometry("900x350") 
    
    settings_win.transient(parent) # 親ウィンドウの上に表示
    settings_win.grab_set() # モーダルにする
    
    frame = ttk.Frame(settings_win, padding="15") # パディングも少し増やす
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # 列の比重設定 (エントリー欄が伸縮するように)
    frame.columnconfigure(1, weight=1)
    
    # --- 変数 ---
    key_var = tk.StringVar(value=config.AWS_KEY or '')
    secret_var = tk.StringVar(value=config.AWS_SECRET or '')
    region_var = tk.StringVar(value=config.AWS_REGION or 'ap-northeast-1')
    storage_var = tk.StringVar(value=config.STORAGE_CLASS or 'DEEP_ARCHIVE')
    zipdir_var = tk.StringVar(value=config.ZIP_TEMP_DIR or '.')
    
    # --- レイアウト ---
    ttk.Label(frame, text="AWS Access Key ID:").grid(row=0, column=0, sticky=tk.W, pady=8)
    ttk.Entry(frame, textvariable=key_var, width=60).grid(row=0, column=1, sticky=(tk.W, tk.E))
    
    ttk.Label(frame, text="AWS Secret Access Key:").grid(row=1, column=0, sticky=tk.W, pady=8)
    ttk.Entry(frame, textvariable=secret_var, width=60, show='*').grid(row=1, column=1, sticky=(tk.W, tk.E))
    
    ttk.Label(frame, text="AWS Region:").grid(row=2, column=0, sticky=tk.W, pady=8)
    ttk.Entry(frame, textvariable=region_var, width=60).grid(row=2, column=1, sticky=(tk.W, tk.E))
    
    ttk.Separator(frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky='ew', pady=15)
    
    ttk.Label(frame, text="S3 Storage Class:").grid(row=4, column=0, sticky=tk.W, pady=8)
    ttk.Entry(frame, textvariable=storage_var, width=60).grid(row=4, column=1, sticky=(tk.W, tk.E))
    
    # --- Zip Temp Dir (フォルダ選択に変更) ---
    ttk.Label(frame, text="Zip Temp Dir:").grid(row=5, column=0, sticky=tk.W, pady=8)
    
    zip_entry_frame = ttk.Frame(frame)
    zip_entry_frame.grid(row=5, column=1, sticky=(tk.W, tk.E))
    zip_entry_frame.columnconfigure(0, weight=1) # エントリーが伸縮
    
    zip_entry = ttk.Entry(zip_entry_frame, textvariable=zipdir_var, state='readonly')
    zip_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
    
    def select_zip_dir():
        # or zipdir_var.get() は、ダイアログをキャンセルした時に元の値を保持するため
        selected_dir = filedialog.askdirectory(title="Zip一時ディレクトリを選択", initialdir=zipdir_var.get())
        if selected_dir: # 空文字でない（選択された）場合のみ更新
            zipdir_var.set(selected_dir)

    ttk.Button(zip_entry_frame, text="選択", command=select_zip_dir).grid(row=0, column=1, padx=(5, 0))
    
    # --- ボタン ---
    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=6, column=0, columnspan=2, pady=15)
    
    result = {"saved": False}
    
    def on_save():
        key = key_var.get().strip()
        secret = secret_var.get().strip()
        
        if not key or not secret:
            messagebox.showerror("入力エラー", "Access Key ID と Secret Access Key は必須です。", parent=settings_win)
            return

        settings = {
            'aws_key': key,
            'aws_secret': secret,
            'aws_region': region_var.get().strip() or 'ap-northeast-1',
            'storage_class': storage_var.get().strip() or 'DEEP_ARCHIVE',
            'zip_temp_dir': zipdir_var.get().strip() or '.'
        }
        
        if config.save_config(settings):
            messagebox.showinfo("成功", "設定を config.ini に保存しました。", parent=settings_win)
            result["saved"] = True
            settings_win.destroy()
        else:
            messagebox.showerror("エラー", "設定の保存に失敗しました。", parent=settings_win)

    def on_cancel():
        settings_win.destroy()

    ttk.Button(btn_frame, text="保存", command=on_save).pack(side=tk.LEFT, padx=5, ipady=5)
    ttk.Button(btn_frame, text="キャンセル", command=on_cancel).pack(side=tk.LEFT, padx=5, ipady=5)
    
    # ウィンドウの伸縮設定
    settings_win.columnconfigure(0, weight=1)
    settings_win.rowconfigure(0, weight=1)

    settings_win.wait_window() # ウィンドウが閉じるまで待機
    return result["saved"]

# --- メインアプリケーションクラス ---
class MusicArchiverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Archiver")
        
        # --- ウィンドウサイズ指定 (拡大) ---
        self.root.geometry("900x500") 
        
        # スレッド間通信用キュー
        self.queue = queue.Queue()
        
        # --- メインフレーム ---
        main_frame = ttk.Frame(root, padding="15") # パディングも少し増やす
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # --- 変数 ---
        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()
        self.bucket_var = tk.StringVar()
        self.status_var = tk.StringVar(value="ステータス: 待機中")

        # --- ウィジェット ---
        
        # 1. コピー元
        ttk.Label(main_frame, text="1. 現在の音楽ディレクトリ (コピー元):").grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 2))
        self.source_entry = ttk.Entry(main_frame, textvariable=self.source_var, state='readonly')
        self.source_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), ipady=5) # 高さを増やす
        self.source_btn = ttk.Button(main_frame, text="選択", command=self.select_source)
        self.source_btn.grid(row=1, column=2, padx=(5, 0), ipady=5) # 高さを合わせる

        # 2. コピー先
        ttk.Label(main_frame, text="2. 移行先のディレクトリ (コピー先 & Zip名):").grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 2))
        self.target_entry = ttk.Entry(main_frame, textvariable=self.target_var, state='readonly')
        self.target_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), ipady=5)
        self.target_btn = ttk.Button(main_frame, text="選択", command=self.select_target)
        self.target_btn.grid(row=3, column=2, padx=(5, 0), ipady=5)

        # 3. S3バケット
        ttk.Label(main_frame, text="3. アップロード先 S3バケット名:").grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(10, 2))
        self.bucket_entry = ttk.Entry(main_frame, textvariable=self.bucket_var)
        self.bucket_entry.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), ipady=5)

        ttk.Separator(main_frame, orient='horizontal').grid(row=6, column=0, columnspan=3, sticky='ew', pady=20)
        
        # 4. ボタン
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=7, column=0, columnspan=3, sticky=tk.W)
        
        self.run_btn = ttk.Button(btn_frame, text="実行", command=self.run_archive)
        self.run_btn.pack(side=tk.LEFT, ipady=10, ipadx=10) # ボタンサイズも大きく
        self.settings_btn = ttk.Button(btn_frame, text="設定変更", command=lambda: show_settings_window(self.root))
        self.settings_btn.pack(side=tk.LEFT, padx=10, ipady=10, ipadx=10)
        self.exit_btn = ttk.Button(btn_frame, text="終了", command=self.root.quit)
        self.exit_btn.pack(side=tk.LEFT, padx=10, ipady=10, ipadx=10)

        # 5. ステータスバー
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=5) # パディング追加
        self.status_label.grid(row=8, column=0, columnspan=3, sticky='ew', pady=(20, 0), ipady=5)
        
        # ウィンドウサイズ調整
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1) # エントリー欄が伸縮
        
    def select_source(self):
        dir_name = filedialog.askdirectory(title="コピー元ディレクトリを選択")
        if dir_name:
            self.source_var.set(dir_name)

    def select_target(self):
        dir_name = filedialog.askdirectory(title="コピー先ディレクトリを選択（または作成）")
        if dir_name:
            self.target_var.set(dir_name)

    def run_archive(self):
        source = self.source_var.get()
        target = self.target_var.get()
        bucket = self.bucket_var.get().strip()
        
        if not source or not target or not bucket:
            messagebox.showerror("入力エラー", "すべてのフィールド（コピー元、コピー先、S3バケット）を入力してください。")
            return
            
        if not os.path.exists(source):
            messagebox.showerror("エラー", "指定された「コピー元」ディレクトリが存在しません。")
            return

        confirm_text = textwrap.dedent(f"""
            以下の操作を実行しますか？
            1. コピー元: {source}
            2. コピー先: {target}
            3. Zip作成: {os.path.basename(os.path.normpath(target))}.zip
            4. S3アップロード: s3://{bucket}/
        """)
    
        if not messagebox.askyesno("実行確認", confirm_text):
            return

        # ボタンを無効化
        self.toggle_buttons(False)
        self.status_var.set("ステータス: 処理を開始します...")
        
        # スレッドで処理を実行
        threading.Thread(
            target=self.run_archive_thread,
            args=(source, target, bucket),
            daemon=True
        ).start()
        
        # キューの監視を開始
        self.root.after(100, self.check_queue)
        
    def run_archive_thread(self, source, target, bucket):
        """ワーカースレッドで実行される関数"""
        
        def status_callback(message):
            self.queue.put(message)
            
        success, message = perform_archive(source, target, bucket, status_callback)
        self.queue.put(("__DONE__", success, message))

    def check_queue(self):
        """GUIスレッドでキューをチェックし、ステータスを更新する"""
        try:
            while True:
                message = self.queue.get_nowait()
                
                if isinstance(message, tuple) and message[0] == "__DONE__":
                    success, msg_text = message[1], message[2]
                    if not success:
                        messagebox.showerror("実行エラー", f"処理中にエラーが発生しました:\n{msg_text}")
                    self.toggle_buttons(True)
                    return 
                else:
                    self.status_var.set(f"ステータス: {message}")
                    
        except queue.Empty:
            self.root.after(100, self.check_queue)

    def toggle_buttons(self, enabled):
        state = 'normal' if enabled else 'disabled'
        self.run_btn.config(state=state)
        self.settings_btn.config(state=state)
        self.source_btn.config(state=state)
        self.target_btn.config(state=state)
        self.exit_btn.config(state=state)
        self.bucket_entry.config(state=state)

# --- アプリケーションの起動 ---
if __name__ == "__main__":
    
    root = tk.Tk()
    
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
        style = ttk.Style()
        style.theme_use('vista') 
        style.configure('Accent.TButton', background='#0078D4', foreground='white')
        style.map('Accent.TButton', background=[('active', '#005A9E')])
    except Exception:
        print("Windows以外のOSか、テーマ設定に失敗しました。デフォルトテーマを使用します。")

    # 初回起動チェック
    if not config.config_loaded:
        messagebox.showinfo("初期設定", "設定ファイル (config.ini) が見つからないか、内容が不完全です。\n設定ウィンドウを開きます。")
        if not show_settings_window(root):
            messagebox.showerror("エラー", "設定が完了しなかったため、アプリケーションを終了します。")
            root.destroy()
            sys.exit(0)
    else:
        # 起動時に設定を読み込む
        config.load_config()

    app = MusicArchiverApp(root)
    root.mainloop()
