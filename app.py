from flask import Flask, render_template, request, send_file
import yt_dlp
import io
import uuid
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        format_type = request.form.get('format')
        quality = request.form.get('quality_mp4')

        if not url or not format_type:
            return "URL atau format belum dipilih."

        if format_type != 'mp4':
            return "Hanya format MP4 yang didukung saat ini."

        if not quality:
            return "Kualitas belum dipilih."

        output_id = str(uuid.uuid4())
        extension = 'mp4'
        filename = f"/tmp/{output_id}.{extension}"  # <--- PENTING: gunakan /tmp di Vercel

        try:
            height = int(quality)
            ydl_opts = {
                'format': f"bestvideo[ext=mp4][height<={height}]+bestaudio[ext=m4a]/best[height<={height}]",
                'outtmpl': filename,
                'quiet': True,
                'noplaylist': True,
                'merge_output_format': 'mp4'
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            buffer = io.BytesIO()
            with open(filename, 'rb') as f:
                buffer.write(f.read())
            os.remove(filename)
            buffer.seek(0)

            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"download.{extension}",
                mimetype="video/mp4"
            )

        except Exception as e:
            return f"Terjadi kesalahan saat mengunduh: {str(e)}"

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
