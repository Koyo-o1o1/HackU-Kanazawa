import io
from google.cloud import vision
from google.oauth2 import service_account
# サービスアカウントキー JSON のパス
KEY_PATH = r"C:\Users\ko11s\OneDrive\Desktop\app\danger_photo\key.json"
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
client = vision.ImageAnnotatorClient(credentials=credentials)
def detect_place_and_text(path):
    """ランドマーク、Web、Logo、テキスト情報を統合して場所を推定"""
    with io.open(path, 'rb') as f:
        content = f.read()
    image = vision.Image(content=content)
    # --- Landmark Detection ---
    landmark_response = client.landmark_detection(image=image)
    landmarks = landmark_response.landmark_annotations
    if landmarks:
        landmark = landmarks[0]  # 最も信頼度の高いランドマークを使用
        lat_lng = landmark.locations[0].lat_lng
        print("=== Landmark 推定 ===")
        print(f"名称: {landmark.description}")
        print(f"緯度: {lat_lng.latitude}, 経度: {lat_lng.longitude}")
        print(f"信頼度スコア: {landmark.score:.2f}")
        return
    # --- Web Detection ---
    web_response = client.web_detection(image=image)
    web_entities = web_response.web_detection.web_entities
    web_places = [e.description for e in web_entities if e.description]
    # --- Logo Detection ---
    logo_response = client.logo_detection(image=image)
    logos = [l.description for l in logo_response.logo_annotations if l.description]
    # --- Text Detection (OCR) ---
    text_response = client.text_detection(image=image)
    texts = text_response.text_annotations
    text_strings = []
    if texts:
        # texts[0] は画像全体のテキスト
        full_text = texts[0].description
        text_strings = full_text.split("\n")
    # --- 統合推定 ---
    if web_places or logos or text_strings:
        print("=== 統合推定 (Landmarkなし) ===")
        if web_places:
            print("Web候補:", web_places)
        if logos:
            print("Logo候補:", logos)
        if text_strings:
            print("テキスト候補:", text_strings)
        print("※ランドマークがないため、場所の精度は低めです")
    else:
        print("場所を推定できませんでした")
# 実行
detect_place_and_text(r"C:\Users\ko11s\OneDrive\Desktop\app\danger_photo\sample.jpg")