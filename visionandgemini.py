import io
import base64
import json
import os
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image # Pillowライブラリを追加
import google.generativeai as genai

# --- 設定 ---
# ファイルパスは環境に合わせて設定してください
SERVICE_ACCOUNT_PATH = r"C:\Users\rushi\hackason\key.json"
IMAGE_PATH = r"C:\Users\rushi\hackason\Image\IMG_4661.jpg"

# --- Google Cloud 認証 ---
# サービスアカウントキーのパスを環境変数に設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH)
vision_client = vision.ImageAnnotatorClient(credentials=credentials)

# --- 画像読み込み ---
try:
    # Pillowを使って画像を開く
    img = Image.open(IMAGE_PATH)
    # Vision API用にバイトデータを取得
    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()
    image_for_vision = vision.Image(content=image_bytes)
except FileNotFoundError:
    print(f"エラー: 画像ファイルが見つかりません。パスを確認してください: {IMAGE_PATH}")
    exit()


# --- Vision API解析関数 (内容は変更なし) ---
# --- Vision API解析関数 ---
def analyze_image(image):
    result = {}

    # Web エンティティ
    web_entities = vision_client.web_detection(image=image).web_detection.web_entities
    result["web_entities"] = [
        {"description": e.description, "score": e.score}
        for e in web_entities if e.description
    ]

    # ロゴ検出
    logos = vision_client.logo_detection(image=image).logo_annotations
    result["logos"] = [
        {"description": l.description, "score": l.score}
        for l in logos if l.description
    ]

    # OCR
    texts = vision_client.text_detection(image=image).text_annotations
    result["ocr_texts"] = [texts[0].description] if texts else []

    # ランドマーク検出
    landmarks = vision_client.landmark_detection(image=image).landmark_annotations
    result["landmarks"] = [
        {"description": l.description, "score": l.score}
        for l in landmarks
    ]

    # 顔検出
    faces = vision_client.face_detection(image=image).face_annotations
    result["faces_detected"] = len(faces) > 0  # True/False
    result["faces_count"] = len(faces)         # 顔の数も入れる

    return result

print("Vision APIで画像を解析中...")
vision_result = analyze_image(image_for_vision)
print("解析が完了しました。")

# --- Gemini API 設定 ---
# 【修正点1: セキュリティ】APIキーを環境変数から読み込む
# 事前に `set GOOGLE_API_KEY="YOUR_API_KEY"` のように環境変数を設定しておくことを推奨
try:
    GOOGLE_API_KEY = "hogehoge"
    genai.configure(api_key=GOOGLE_API_KEY)
except TypeError:
    print("エラー: 環境変数 'GOOGLE_API_KEY' が設定されていません。")
    exit()


# 【修正点2: モデルの定義】使用するモデルを明示的に定義
# マルチモーダル（画像＋テキスト）用途には 'gemini-pro-vision' を使用
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Gemini に渡す ---
# プロンプトから画像データ（base64）を削除し、テキストと画像オブジェクトを別々に渡す
prompt_text = f"""
以下のVision APIの解析結果と画像データを基に、画像の場所を特定してください。
最も可能性が高い場所を示してください
信頼度が高いものから順に推定し、その理由も簡潔に説明してください。
場所は日本限定です。

また、顔認識の情報から写真に顔が映っている場合は警告してください

【Vision API解析結果(JSON)】
{json.dumps(vision_result, ensure_ascii=False, indent=2)}
"""

print("Geminiに場所の推定を依頼中...")
# 【修正点3: API呼び出し】テキストと画像をリストで渡す
response = model.generate_content([prompt_text, img])


# --- 結果出力 ---
print("\n=== Gemini 推定結果 ===")
print(response.text)