import os
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

# Flaskアプリケーションの初期化
app = Flask(__name__)

# 画像をアップロードするフォルダのパスを指定
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# uploadsフォルダがなければ作成する
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ルートURL ('/') にアクセスがあったときにindex.htmlを返す
@app.route('/')
def index():
    return render_template('index.html')

# '/upload' にPOSTリクエストがあったときの処理
@app.route('/upload', methods=['POST'])
def upload_file():
    # 'image'という名前のファイルがリクエストに含まれているかチェック
    if 'image' not in request.files:
        return redirect(request.url)
    
    file = request.files['image']

    # ユーザーがファイルを選択しなかった場合
    if file.filename == '':
        return redirect(request.url)

    # ファイルが選択され、安全なファイル名であれば保存処理を行う
    if file:
        # 安全なファイル名に変換 (例: "My Image.jpg" -> "My_Image.jpg")
        filename = secure_filename(file.filename)
        # ファイルを保存するパスを作成
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # ファイルを保存
        file.save(filepath)
        
        # 保存したファイルパスを次の処理（例: process_image.py）に渡せるように表示
        return f"ファイルがアップロードされました: <br>{filepath}<br><a href='/'>戻る</a>"

    return redirect(url_for('index'))

# このスクリプトが直接実行された場合にサーバーを起動
if __name__ == '__main__':
    app.run(debug=True, port=5000)