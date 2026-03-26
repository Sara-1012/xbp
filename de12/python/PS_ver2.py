"失敗(RGBだけだと正しくない)"

from flask import Flask, request, render_template_string
from openai import OpenAI
from PIL import Image
import numpy as np
import io
import base64
import os

# === OpenAIクライアント設定 ===
# 安全に環境変数から読み込む方法（または直接書いてもOK）
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY") or "ここに自分のOpenAIキーを貼る")

app = Flask(__name__)

# === HTMLテンプレート ===
HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>パーソナルカラー診断（手の写真）</title>
</head>
<body>
    <h1>パーソナルカラー診断</h1>
    <p>あなたの手の写真をアップロードしてください。（個人情報が載らないようにしてください）</p>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" required>
        <input type="submit" value="診断する">
    </form>

    {% if result %}
        <h2>診断結果</h2>
        <p>{{ result|safe }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        file = request.files["image"]
        image_bytes = file.read()

        # === 画像から平均色を抽出 ===
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB").resize((100, 100))  # 小さくして平均化
        pixels = np.array(image).reshape(-1, 3)
        avg_color = pixels.mean(axis=0)
        r, g, b = [int(x) for x in avg_color]

        # === GPTへのプロンプト ===
        prompt = (
            f"次のRGB平均値は R={r}, G={g}, B={b} です。"
            "この色の傾向から、一般的なパーソナルカラー分類（スプリング、サマー、オータム、ウィンター）のうち、"
            "どのタイプに近いかを推測してください。"
            "また、その理由と、似合いやすい色・避けた方が良い色を具体的に説明してください。"
        )

        # === OpenAI API呼び出し ===
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        result = response.choices[0].message.content

    return render_template_string(HTML_PAGE, result=result)


if __name__ == "__main__":
    app.run(debug=True)