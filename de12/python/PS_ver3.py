"成功(LabとCで判断、一番正確に近い)"

from flask import Flask, request, render_template_string
from openai import OpenAI
from PIL import Image
import numpy as np
import io
import base64
import os
from skimage import color  # ★ 追加：Lab変換に使用

# === OpenAIクライアント設定 ===
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY") or "ここに自分のOpenAIキーを貼る")

app = Flask(__name__)

# === HTMLテンプレート ===
HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>パーソナルカラー診断（肌の写真）</title>
</head>
<body>
    <h1>パーソナルカラー診断</h1>
    <p>あなたの『 肌のみ 』が映った写真を『 .png 』形式のファイルをアップロードしてください。<br>
    ⚠️注意⚠️<br>
    ・顔などの個人情報が載らないようにしてください<br>
    ・光(自然光、白い電気)に当たった写真を使用することでより正確になります</p>
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
        image = image.convert("RGB").resize((100, 100))
        pixels = np.array(image).reshape(-1, 3) / 255.0  # 正規化（0〜1）

        # === RGB → Lab変換 ===
        lab_pixels = color.rgb2lab(pixels.reshape(100, 100, 3))
        avg_lab = lab_pixels.reshape(-1, 3).mean(axis=0)
        L, a, b = avg_lab

        # === GPTへのプロンプト ===
        prompt = f"""
あなたはプロのパーソナルカラー診断士です。
次のLab値は L={L:.1f}, a={a:.1f}, b={b:.1f} です。
以下の条件にのみ従って、パーソナルカラーを診断してください。
絶対最初にパーソナルカラーを簡潔に書いてください。もし中途半端な結果であればどちらも記入してください。

条件:
1. 彩度C* = √(a² + b²)
2. イエベ/ブルベ判定は (b - a) による。
   - b - a > 10 → イエベ
   - b - a < 5 → ブルベ
3. 明るさ判定
   - L > 70 → 明るめ
   - L < 60 → 深め
4. 彩度判定
   - C > 35 → ビビッド
   - C < 25 → ソフト
5. これらを組み合わせて4シーズンを決定：
   - Spring: b - a > 10, L > 70, C > 35　です。
   - Summer: b - a < 5,  L > 70, C < 30　です。
   - Autumn: b - a > 10, L < 60, C < 30　です。
   - Winter: b - a < 5,  L < 60, C > 35　です。

この条件に従って、あなたが推測するパーソナルカラータイプを出し、
理由と似合う色、避けたほうがよい色を説明してください。
"""

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
    