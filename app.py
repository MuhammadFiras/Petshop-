from flask import Flask, render_template, request, redirect, url_for, flash
import os
import mysql.connector
from dotenv import load_dotenv
import time # Tambahkan baris ini untuk import modul time

load_dotenv() # Memuat variabel lingkungan dari file .env

app = Flask(__name__)
app.secret_key = 'supersecretkey_petshop_app' # Ganti dengan kunci rahasia yang lebih kuat

# Konfigurasi Database dari .env
DB_HOST = os.getenv('DATABASE_HOST')
DB_USER = os.getenv('DATABASE_USER')
DB_PASSWORD = os.getenv('DATABASE_PASSWORD')
DB_NAME = os.getenv('DATABASE_NAME')

def get_db_connection():
    # Tambahkan retry logic di sini
    max_retries = 10 # Jumlah percobaan maksimum
    retry_delay = 5  # Penundaan (detik) antar percobaan
    for i in range(max_retries):
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            print(f"Koneksi database berhasil setelah {i+1} percobaan.")
            return conn
        except mysql.connector.Error as err:
            if i < max_retries - 1:
                print(f"Gagal koneksi ke database (percobaan {i+1}/{max_retries}): {err}. Mencoba lagi dalam {retry_delay} detik...")
                time.sleep(retry_delay)
            else:
                print(f"Gagal koneksi ke database setelah {max_retries} percobaan: {err}")
                return None

# Inisialisasi database (akan dijalankan saat startup pertama kali)
def init_db():
    conn = get_db_connection() # Panggil fungsi koneksi dengan retry logic
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pet_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(100) NOT NULL,
                    stock INT NOT NULL,
                    price DECIMAL(10, 2) NOT NULL
                )
            """)
            conn.commit()
            print("Tabel 'pet_items' berhasil dibuat atau sudah ada.")
        except mysql.connector.Error as err:
            print(f"Error creating table: {err}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("Tidak dapat membuat tabel karena koneksi database gagal.")

# Rute utama - Menampilkan daftar item toko peliharaan
@app.route('/')
def index():
    conn = get_db_connection()
    if conn is None:
        flash("Tidak dapat terhubung ke database.", "error")
        return render_template('index.html', items=[])

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pet_items")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', items=items)

# Rute untuk menambah item baru
@app.route('/add', methods=('GET', 'POST'))
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        item_type = request.form['type']
        stock = request.form['stock']
        price = request.form['price']

        if not name or not item_type or not stock or not price:
            flash('Nama, Tipe, Stok, dan Harga wajib diisi!', 'error')
        else:
            try:
                stock = int(stock)
                price = float(price)
                if stock < 0 or price < 0:
                    flash('Stok dan Harga tidak boleh negatif!', 'error')
                    return render_template('add_item.html')

                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO pet_items (name, type, stock, price) VALUES (%s, %s, %s, %s)",
                                   (name, item_type, stock, price))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    flash('Item berhasil ditambahkan!', 'success')
                    return redirect(url_for('index'))
            except ValueError:
                flash('Stok harus berupa angka bulat dan Harga harus berupa angka desimal!', 'error')
    return render_template('add_item.html')

# Rute untuk mengedit item
@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit_item(id):
    conn = get_db_connection()
    if conn is None:
        flash("Tidak dapat terhubung ke database.", "error")
        return redirect(url_for('index'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pet_items WHERE id = %s", (id,))
    item = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        name = request.form['name']
        item_type = request.form['type']
        stock = request.form['stock']
        price = request.form['price']

        if not name or not item_type or not stock or not price:
            flash('Nama, Tipe, Stok, dan Harga wajib diisi!', 'error')
        else:
            try:
                stock = int(stock)
                price = float(price)
                if stock < 0 or price < 0:
                    flash('Stok dan Harga tidak boleh negatif!', 'error')
                    return render_template('edit_item.html', item=item)

                cursor = conn.cursor()
                cursor.execute("UPDATE pet_items SET name = %s, type = %s, stock = %s, price = %s WHERE id = %s",
                               (name, item_type, stock, price, id))
                conn.commit()
                cursor.close()
                conn.close()
                flash('Item berhasil diperbarui!', 'success')
                return redirect(url_for('index'))
            except ValueError:
                flash('Stok harus berupa angka bulat dan Harga harus berupa angka desimal!', 'error')

    conn.close()
    if item is None:
        flash('Item tidak ditemukan!', 'error')
        return redirect(url_for('index'))
    return render_template('edit_item.html', item=item)

# Rute untuk menghapus item
@app.route('/delete/<int:id>', methods=('POST',))
def delete_item(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pet_items WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Item berhasil dihapus!', 'success')
    else:
        flash("Tidak dapat terhubung ke database untuk menghapus.", "error")
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db() # Pastikan tabel dibuat saat aplikasi dijalankan
    app.run(debug=True, host='0.0.0.0', port=5000)

# Pastikan ini ada di akhir file Anda
if __name__ == '__main__':
    init_db() # Pastikan tabel dibuat saat aplikasi dijalankan
    app.run(debug=True, host='0.0.0.0', port=5000)