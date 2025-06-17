# Gunakan image Python resmi sebagai base image.
# Kita pakai versi 3.9-slim-buster untuk ukuran yang lebih kecil dan stabil.
FROM python:3.9-slim-buster

# Atur direktori kerja di dalam container.
# Semua perintah setelah ini akan dijalankan relatif terhadap direktori ini.
WORKDIR /app

# Salin file requirements.txt ke dalam direktori kerja.
# Ini dilakukan sebelum menyalin kode aplikasi agar layer ini bisa di-cache.
COPY requirements.txt .

# Instal dependensi Python dari requirements.txt.
# --no-cache-dir: Jangan simpan cache pip untuk mengurangi ukuran image.
# -r: Instal dari file requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh isi direktori aplikasi Anda ke dalam container.
# Ini akan menyalin app.py, folder templates/, .env.example, dll.
# (Ingat: kita tidak menyalin .env asli ke dalam image untuk keamanan)
COPY . .

# Expose port 5000, karena aplikasi Flask kita berjalan di port tersebut.
# Ini memberitahu Docker bahwa container ini akan mendengarkan di port 5000.
EXPOSE 5000

# Perintah default untuk menjalankan aplikasi saat container dimulai.
# flask run --host=0.0.0.0 berarti Flask akan mendengarkan di semua interface jaringan
# di dalam container, sehingga bisa diakses dari luar container.
# Pastikan app.py Anda memiliki `if __name__ == '__main__': app.run(debug=True, host='0.0.0.0', port=5000)`
# seperti yang sudah kita buat.
CMD ["python", "app.py"]