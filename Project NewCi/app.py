import pyodbc
import maskpass
from prettytable import PrettyTable
import datetime
import math
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask import Flask, render_template
from db import get_connection

# # Inisialisasi aplikasi Flask
app = Flask(__name__)


cnxn = get_connection()


# Rute untuk halaman utama
@app.route("/home")
def home():
    return render_template("dashboardbefore.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validasi user (contoh validasi sederhana)
        if username == "Dodo" and password == "DodoGanteng":
            return redirect(url_for('dashboard'))  # Arahkan ke halaman dashboard setelah login sukses
        else:
            return "Login Failed! Please check your username and password."

    return render_template('login.html')


# Route to fetch kelurahan based on selected kecamatan
@app.route('/get_kelurahan', methods=['GET'])
def get_kelurahan():
    id_kecamatan = request.args.get('id_kecamatan')
    
    if not id_kecamatan:
        return jsonify([])  # Return empty list if no kecamatan selected
    
    connection = get_connection()
    cursor = connection.cursor()
    
    # Query to fetch Kelurahan based on Kecamatan
    cursor.execute('''
        SELECT id_kelurahan, nama
        FROM Kelurahan
        WHERE id_kecamatan = ?
    ''', (id_kecamatan,))
    
    kelurahan_list = cursor.fetchall()
    
    # Convert to list of dictionaries
    kelurahan_data = [{"id_kelurahan": kelurahan.id_kelurahan, "nama": kelurahan.nama} for kelurahan in kelurahan_list]
    
    cursor.close()
    connection.close()
    
    return jsonify(kelurahan_data)

# Route to display form to add user
@app.route('/tambah-pengguna', methods=['GET', 'POST'])
def tambah_pengguna():
    if request.method == 'POST':
        # username = request.form['username']
        # password = request.form['password']
        # nama = request.form['nama']
        # role = request.form['role']
        id_kecamatan = request.form['id_kecamatan']

        nama = request.form['nama']
        noHP = request.form['noHP']
        email = request.form['email']
        id_kelurahan = request.form['id_kelurahan']

        # Insert new user into the Pengguna table
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO Pelanggan (nama, nohp, email, id_kelurahan)
            VALUES (?, ?, ?, ?)
        ''', (nama, noHP, email, id_kelurahan))
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Redirect to dashboard after successful insertion
        return redirect(url_for('dashboard'))

    # Get list of kecamatan to display in the form
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT id_kecamatan, nama FROM Kecamatan')
    kecamatan_list = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return render_template('tambah_pengguna.html', kecamatan_list=kecamatan_list)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Rute untuk halaman mesin cuci
@app.route("/machines")
def list_machines():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Mesin_Cuci where Status = 0")
    machines = cursor.fetchall()
    return render_template("machines.html", machines=machines)


# Jalankan aplikasi
if __name__ == "__main__":
    app.run(debug=True)


# Method untuk cek mesin cuci yang ada
def cek_mesincuci():
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM Mesin_Cuci")
    all_machine = cursor.fetchall()
    table = PrettyTable()
    table.field_names = ["ID", "Nama", "Merk", "Kapasitas (Kg)", "Status", "Tarif"]
    for machine in all_machine:
        table.add_row(machine)
    print("\nDaftar Mesin Cuci:\n")
    print(table)

# Method untuk menu login
def login_page():
    cursor = cnxn.cursor()
    cek_mesincuci()  # Display the list of washing machines right after login
    username = input("Masukkan Username: ")
    password = maskpass.askpass("Masukkan Password: ")

    # Cek apakah username ada di tabel
    cursor.execute("SELECT Password FROM Pengguna WHERE Username = ?", (username,))
    row = cursor.fetchone()

    if not row:
        print("Username tidak ada")
        return False
    elif row[0] != password:
        print("Password salah")
        return False
    else:
        print("Login berhasil")
        return True

# Method untuk masukkan mesin cuci
def insert_washing_machine():
    cursor = cnxn.cursor()
    nama = input("Masukkan Nama Mesin Cuci: ")
    merk = input("Masukkan Merk Mesin Cuci: ")
    kapasitas = input("Masukkan Kapasitas Mesin Cuci dalam Kg: ")
    status = 0
    tarif = input("Masukkan Tarif Mesin Cuci: ")

    insert_query = '''
                    INSERT INTO Mesin_Cuci (Nama, Merk, Kapasitas, Status, Tarif)
                    VALUES (?, ?, ?, ?, ?);
    '''
    cursor.execute(insert_query, (nama, merk, kapasitas, status, tarif))
    cnxn.commit()
    print("Berhasil menambahkan mesin cuci baru!")

# Method untuk add customer
def insert_customer():
    cursor = cnxn.cursor()
    nama = input("Masukkan nama pelanggan: ")
    nohp = input("Masukkan nomor HP pelanggan: ")
    email = input("Masukkan email pelanggan: ")
    id_kelurahan = input("Masukkan ID kelurahan pelanggan: ")

    insert_query = '''
                    INSERT INTO Pelanggan (Nama, NoHP, Email, id_Kelurahan)
                    VALUES (?, ?, ?, ?);
    '''
    cursor.execute(insert_query, (nama, nohp, email, id_kelurahan))
    cnxn.commit()

    cursor.execute('SELECT @@IDENTITY AS PelangganID')
    pelanggan_id = cursor.fetchone()[0]
    print(f"Berhasil menambahkan pelanggan baru dengan ID: {pelanggan_id}")
    return pelanggan_id

# Method untuk membuat transaksi baru
def create_transaction():
    cursor = cnxn.cursor()
    pelanggan_id = insert_customer()
    start_time = input("Masukkan waktu mulai menggunakan mesin cuci (format: HH:MM:SS): ")

    # Ensure proper date format
    while True:
        try:
            date_input = input("Masukkan tanggal transaksi (format: YYYY-MM-DD): ")
            date = datetime.datetime.strptime(date_input, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Format tanggal salah. Silakan masukkan tanggal dengan format YYYY-MM-DD.")

    cursor.execute('SELECT * FROM Mesin_Cuci WHERE Status = 0')
    unused_machines = cursor.fetchall()

    if len(unused_machines) == 0:
        print("Maaf, semua mesin cuci sedang digunakan.")
        return

    print("\nMesin cuci yang tersedia:")
    table = PrettyTable()
    table.field_names = ["ID", "Nama", "Merk", "Kapasitas (Kg)", "Status", "Tarif"]
    for machine in unused_machines:
        table.add_row(machine)
    print(table)

    machine_id = int(input("Masukkan ID mesin cuci yang ingin digunakan: "))

    update_query = '''
                    UPDATE Mesin_Cuci
                    SET Status = 1
                    WHERE id_Mesin_Cuci = ?;
    '''
    cursor.execute(update_query, (machine_id,))
    cnxn.commit()

    # Fetch the cashier's name
    while True:
        nama_kasir = input("Masukkan nama kasir: ")
        cursor.execute("SELECT id_Pengguna FROM Pengguna WHERE Username = ?", (nama_kasir,))
        id_kasir = cursor.fetchone()
        if id_kasir:
            break
        else:
            print("Nama kasir tidak valid. Silakan coba lagi.")

    # Insert transaction
    insert_query = '''
                    INSERT INTO Transaksi (IdPelanggan, IdMesinCuci, idPengguna, Waktu_mulai, Total, Tanggal)
                    VALUES (?, ?, ?, ?, ?, ?);
                '''
    cursor.execute(insert_query, (pelanggan_id, machine_id, id_kasir[0], start_time, 0, date))
    cnxn.commit()

    # Fetch the ID of the inserted transaction
    cursor.execute('SELECT @@IDENTITY AS TransaksiID')
    transaksi_id = cursor.fetchone()[0]
    print(f"Transaksi berhasil dibuat dengan ID: {transaksi_id}")

# Method untuk menyelesaikan transaksi
def finalize_transaction():
    cursor = cnxn.cursor()
    machine_id = input("Masukkan ID mesin cuci: ")
    end_time = input("Masukkan waktu selesai menggunakan mesin cuci (format: HH:MM:SS): ")

    cursor.execute('SELECT Waktu_mulai FROM Transaksi WHERE IdMesinCuci = ? AND Waktu_selesai IS NULL', (machine_id,))
    transaction_details = cursor.fetchone()

    if not transaction_details:
        print("Transaksi tidak ditemukan atau sudah diselesaikan.")
        return

    start_time = transaction_details[0]

    cursor.execute('SELECT Tarif FROM Mesin_Cuci WHERE id_Mesin_Cuci = ?', (machine_id,))
    tarif = cursor.fetchone()[0]

    start_datetime = datetime.datetime.strptime(str(start_time), "%H:%M:%S")
    end_datetime = datetime.datetime.strptime(end_time, "%H:%M:%S")
    duration = int((end_datetime - start_datetime).total_seconds() / 900)  # Satuan 15 menit
    total_cost = (duration * tarif)

    update_transaction_query = '''
                    UPDATE Transaksi
                    SET Waktu_selesai = ?, Total = ?
                    WHERE IdMesinCuci = ? AND Waktu_selesai IS NULL;
    '''
    cursor.execute(update_transaction_query, (end_time, total_cost, machine_id))
    cnxn.commit()

    update_machine_query = '''
                    UPDATE Mesin_Cuci
                    SET Status = 0
                    WHERE id_Mesin_Cuci = ?;
    '''
    cursor.execute(update_machine_query, (machine_id,))
    cnxn.commit()

    print(f"Transaksi untuk mesin cuci {machine_id} selesai dengan biaya total: {total_cost}")

# Method untuk mendapatkan laporan keuangan
def laporan_keuangan():
    cursor = cnxn.cursor()
    print("Masukkan range tanggal")
    tanggal_awal = input("Masukkan tanggal awal: ")
    tanggal_akhir = input("Masukkan tanggal akhir: ")

    # Query untuk menampilkan data penghasilan di rentang tanggal tersebut
    query = '''
        SELECT IdPelanggan, IdMesinCuci, idPengguna, Waktu_mulai, Waktu_selesai, Total, Tanggal
        FROM Transaksi
        WHERE Tanggal BETWEEN ? AND ?
    '''

    #Execute Query
    cursor.execute(query, (tanggal_awal, tanggal_akhir))
    results = cursor.fetchall()

    if results:
        table = PrettyTable()
        table.field_names = ["IdPelanggan", "IdMesinCuci", "idPengguna", "Waktu_mulai", "Waktu_selesai", "Total", "Tanggal"]
        for row in results:
            table.add_row(row)
        print(table)
    else:
        print("Tidak ada data untuk rentang tanggal yang diberikan.")

# Main menu function
def main_menu():
    while True:
        cek_mesincuci()  # Display the list of washing machines every time the menu is displayed
        print("\n=== APLIKASI PENGELOLAAN MESIN CUCI ===")
        print("1. Cek Daftar Mesin Cuci")
        print("2. Tambah Mesin Cuci Baru")
        print("3. Tambah Pelanggan Baru dan Transaksi")
        print("4. Selesaikan Transaksi")
        print("5. Lihat Laporan Keuangan")
        print("6. Keluar")

        try:
            choice = int(input("Masukkan pilihan: "))

            if choice == 1:
                cek_mesincuci()
            elif choice == 2:
                insert_washing_machine()
            elif choice == 3:
                create_transaction()
            elif choice == 4:
                finalize_transaction()
            elif choice == 5:
                laporan_keuangan()
            elif choice == 6:
                print("Keluar dari program.")
                break
            else:
                print("Pilihan tidak valid. Silakan pilih menu yang tersedia.")
        except ValueError:
            print("Input tidak valid. Silakan masukkan angka.")

# Start the program if login successful
if login_page():
    main_menu()
