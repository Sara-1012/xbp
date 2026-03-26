"失敗！肌判断だめ！"

from flask import Flask, request, render_template_string
from openai import OpenAI
import base64

app = Flask(__name__)
client = OpenAI(api_key="ここに自分のOpenAIキーを貼る")  

# HTMLテンプレート
html = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>パーソナルカラー診断AI（手の甲）</title>
</head>
<body style="font-family:sans-serif; text-align:center; margin-top:50px;">
    <h2>パーソナルカラー診断AI（手の甲で診断）🖐️</h2>
    <p>手の甲の写真をアップロードすると、AIがあなたの肌トーンからパーソナルカラーを推定します。</p>
    <form action="/analyze" method="post" enctype="multipart/form-data" style="margin-top:20px;">
        <input type="file" name="image" accept="image/*" required>
        <br><br>
        <button type="submit">診断する</button>
    </form>

    {% if result %}
        <hr>
        <h3>診断結果 🎨</h3>
        <div style="max-width:600px; margin:auto; text-align:left; font-size:18px;">
            {{ result | safe }}
        </div>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(html)

@app.route("/analyze", methods=["POST"])
def analyze():
    image_file = request.files["image"]
    image_bytes = image_file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # OpenAIに画像を送信
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 画像認識対応モデル
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "以下の画像は手の甲です。この画像から肌の色味・明るさ・血色などを分析し、"
                            "4つのパーソナルカラータイプ（スプリング、サマー、オータム、ウィンター）の中から最も近いタイプを推定してください。"
                            "そのうえで：\n"
                            "1. 選ばれたタイプ名（例：スプリングタイプ）\n"
                            "2. 診断理由（肌トーン・血色感などから見た根拠）\n"
                            "3. 似合う色（服・メイク・アクセサリーなど）\n"
                            "4. 避けた方がいい色（理由付き）\n"
                            "を日本語でわかりやすく説明してください。"
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ],
            }
        ],
    )

    result = response.choices[0].message.content
    return render_template_string(html, result=result)

if __name__ == "__main__":
    app.run(debug=True)