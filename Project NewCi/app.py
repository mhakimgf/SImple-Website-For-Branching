# import pyodbc
# # import maskpass
# from prettytable import PrettyTable
import datetime
# import math
from flask import flash, redirect, url_for
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask import Flask, render_template
from db import get_connection

# # Inisialisasi aplikasi Flask
app = Flask(__name__)
app.secret_key = 'dodo'

connection = get_connection()
cursor = connection.cursor()


# Rute untuk halaman utama
@app.route("/home")
def home():
    if 'id_Pengguna' in session:
        return redirect(url_for('dashboard'))
    return render_template("dashboardbefore.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template("dashboardbefore.html")
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validasi user (contoh validasi sederhana)
        cursor.execute('''
            SELECT id_pengguna, Username, Password
            FROM Pengguna
            WHERE Username = ? AND Password = ?
        ''', (username, password))  # Parameter query disertakan sebagai tuple
        user = cursor.fetchone()
        print(user)
        if user:
            session['id_Pengguna'] = user[0]
            session['username'] = user[1]

            return redirect(url_for('dashboard'))
            

    # Jika metode GET, tampilkan halaman login
    return render_template('login.html')


# Route to fetch kelurahan based on selected kecamatan
@app.route('/get_kelurahan', methods=['GET'])
def get_kelurahan():
    id_kecamatan = request.args.get('id_kecamatan')
    
    if not id_kecamatan:
        return jsonify([])  # Return empty list if no kecamatan selected
    
    
    # Query to fetch Kelurahan based on Kecamatan
    cursor.execute('''
        SELECT id_kelurahan, nama
        FROM Kelurahan
        WHERE id_kecamatan = ?
    ''', (id_kecamatan,))
    
    kelurahan_list = cursor.fetchall()
    
    # Convert to list of dictionaries
    kelurahan_data = [{"id_kelurahan": kelurahan.id_kelurahan, "nama": kelurahan.nama} for kelurahan in kelurahan_list]
    
  
    
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

        cursor.execute('''
            INSERT INTO Pelanggan (nama, nohp, email, id_kelurahan)
            VALUES (?, ?, ?, ?)
        ''', (nama, noHP, email, id_kelurahan))
        connection.commit()

       

        # Redirect to dashboard after successful insertion
        return redirect(url_for('dashboard'))

    # Get list of kecamatan to display in the form
    
    cursor.execute('SELECT id_kecamatan, nama FROM Kecamatan')
    kecamatan_list = cursor.fetchall()
    
    

    return render_template('tambah_pengguna.html', kecamatan_list=kecamatan_list)

# Route to display form to add user
@app.route('/pesan', methods=['GET', 'POST'])
def pesan():
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

        cursor.execute('''
            INSERT INTO Pelanggan (nama, nohp, email, id_kelurahan)
            VALUES (?, ?, ?, ?)
        ''', (nama, noHP, email, id_kelurahan))
        connection.commit()

       

        # Redirect to dashboard after successful insertion
        return redirect(url_for('dashboard'))

    # Get list of kecamatan to display in the form
    
    cursor.execute('SELECT id_kecamatan, nama FROM Kecamatan')
    kecamatan_list = cursor.fetchall()
    
    

    return render_template('tambah_pengguna.html', kecamatan_list=kecamatan_list)
    


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Rute untuk halaman mesin cuci
@app.route("/machines")
def list_machines():
    # Connect to the database
    cursor.execute("SELECT id_Mesin_Cuci, Nama, Merk, Kapasitas, Status, Tarif FROM Mesin_Cuci")
    
    # Fetch data and convert rows to dictionaries
    columns = [column[0] for column in cursor.description]  # Get column names
    machines = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convert rows to dicts

   

    # Render the template with the machines data
    return render_template("machines.html", machines=machines)

@app.route('/add-machine', methods=['GET', 'POST'])
def add_machine():
    if request.method == 'POST':
        nama = request.form['nama']
        merk = request.form['merk']
        kapasitas = request.form['kapasitas']
        tarif = request.form['tarif']

        cursor.execute('''
            INSERT INTO Mesin_Cuci (Nama, Merk, Kapasitas, [Status], Tarif)
            VALUES (?, ?, ?, ?, ?)
        ''', (nama, merk, kapasitas, 0, tarif))
        connection.commit()

        

        return redirect(url_for('list_machines'))

    return render_template('add_machine.html')



@app.route('/create-transaction', methods=['GET', 'POST'])
def create_transaction():
    if request.method == 'POST':
        # Use NoHP instead of pelanggan_id
        no_hp = request.form['noHP']  # Get NoHP from the form
        start_time = request.form['start_time']
        tanggal = request.form['tanggal']
        machine_id = int(request.form['machine_id'])
        
        # Fetch the cashier ID from the session
        cashier_id = session.get('id_Pengguna')

        if not cashier_id:
            return "User not logged in. Please login to continue."

        # Ensure start_time has seconds (HH:MM:SS)
        if len(start_time.split(":")) == 2:  # Check if format is HH:MM
            start_time += ":00"  # Append :00 for seconds

        # Validate date format
        try:
            date_obj = datetime.datetime.strptime(tanggal, '%Y-%m-%d').date()
        except ValueError:
            return 'Invalid date format. Please use YYYY-MM-DD.'

        # Fetch the pelanggan_id using NoHP
        cursor.execute('''
            SELECT id_Pelanggan FROM Pelanggan WHERE NoHP = ?
        ''', (no_hp,))
        pelanggan = cursor.fetchone()

        if not pelanggan:
            return "Customer not found. Please check the NoHP and try again."

        # Extract the pelanggan_id
        pelanggan_id = pelanggan[0]

        # Fetch available machines (status = 0)
        cursor.execute('SELECT * FROM Mesin_Cuci WHERE Status = 0')
        unused_machines = cursor.fetchall()

        # Check if there are unused machines
        if len(unused_machines) == 0:
            return "Sorry, all machines are currently in use."

        # Update machine status to 1 (used)
        cursor.execute('''
            UPDATE Mesin_Cuci
            SET Status = 1
            WHERE id_Mesin_Cuci = ?
        ''', (machine_id,))
        connection.commit()

        # Insert transaction record
        cursor.execute('''
            INSERT INTO Transaksi (IdPelanggan, IdMesinCuci, idPengguna, Waktu_mulai, Total, Tanggal)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (pelanggan_id, machine_id, cashier_id, start_time, 0, date_obj))
        connection.commit()

        # Get the transaction ID
        cursor.execute('SELECT @@IDENTITY AS TransaksiID')
        transaksi_id = cursor.fetchone()[0]

        # Redirect to the transaction confirmation page
        return redirect(url_for('dashboard'))

    # If GET request, display the transaction form with available machines
    cursor.execute('SELECT * FROM Mesin_Cuci WHERE Status = 0')
    unused_machines = cursor.fetchall()

    return render_template('create_transaction.html', unused_machines=unused_machines)



@app.route('/finalize-transaction', methods=['GET', 'POST'])
def finalize_transaction():
    if request.method == 'POST':
        machine_id = request.form['machine_id']
        end_time = request.form['end_time']

        # Ensure end_time has seconds (HH:MM:SS)
        if len(end_time.split(":")) == 2:  # Check if format is HH:MM
            end_time += ":00"  # Append :00 for seconds

        # Fetch transaction details based on machine_id (where Waktu_selesai is NULL)
        cursor.execute('SELECT Waktu_mulai FROM Transaksi WHERE IdMesinCuci = ? AND Waktu_selesai IS NULL', (machine_id,))
        transaction_details = cursor.fetchone()

        if not transaction_details:
            flash("Transaction not found or already completed.", "error")
            return redirect(url_for('finalize_transaction'))

        # Get the start time from the transaction
        start_time = transaction_details[0]

        # Fetch the machine's rate (Tarif)
        cursor.execute('SELECT Tarif FROM Mesin_Cuci WHERE id_Mesin_Cuci = ?', (machine_id,))
        tarif = cursor.fetchone()[0]

        # Calculate the duration in 15-minute intervals
        start_datetime = datetime.datetime.strptime(str(start_time), "%H:%M:%S")
        end_datetime = datetime.datetime.strptime(end_time, "%H:%M:%S")

        duration = int((end_datetime - start_datetime).total_seconds() / 900)  # Duration in 15-minute intervals
        total_cost = duration * tarif

        # Update the transaction with end time and total cost
        update_transaction_query = '''
            UPDATE Transaksi
            SET Waktu_selesai = ?, Total = ?
            WHERE IdMesinCuci = ? AND Waktu_selesai IS NULL;
        '''
        cursor.execute(update_transaction_query, (end_time, total_cost, machine_id))
        connection.commit()

        # Update the machine status to available (Status = 0)
        update_machine_query = '''
            UPDATE Mesin_Cuci
            SET Status = 0
            WHERE id_Mesin_Cuci = ?;
        '''
        cursor.execute(update_machine_query, (machine_id,))
        connection.commit()

        # Flash a success message
        flash(f"Transaction for machine {machine_id} finalized with a total cost of {total_cost}", "success")

        # Redirect back to the finalize transaction page to show the notification
        return redirect(url_for('finalize_transaction'))

    return render_template('finalize_transaction.html')




# Jalankan aplikasi
if __name__ == "__main__":
    app.run(debug=False)


# # Method untuk cek mesin cuci yang ada
# def cek_mesincuci():
#     cursor = cnxn.cursor()
#     cursor.execute("SELECT * FROM Mesin_Cuci")
#     all_machine = cursor.fetchall()
#     table = PrettyTable()
#     table.field_names = ["ID", "Nama", "Merk", "Kapasitas (Kg)", "Status", "Tarif"]
#     for machine in all_machine:
#         table.add_row(machine)
#     print("\nDaftar Mesin Cuci:\n")
#     print(table)

# # Method untuk menu login
# def login_page():
#     cursor = cnxn.cursor()
#     cek_mesincuci()  # Display the list of washing machines right after login
#     username = input("Masukkan Username: ")
#     password = maskpass.askpass("Masukkan Password: ")

#     # Cek apakah username ada di tabel
#     cursor.execute("SELECT Password FROM Pengguna WHERE Username = ?", (username,))
#     row = cursor.fetchone()

#     if not row:
#         print("Username tidak ada")
#         return False
#     elif row[0] != password:
#         print("Password salah")
#         return False
#     else:
#         print("Login berhasil")
#         return True

# # Method untuk masukkan mesin cuci
# def insert_washing_machine():
#     cursor = cnxn.cursor()
#     nama = input("Masukkan Nama Mesin Cuci: ")
#     merk = input("Masukkan Merk Mesin Cuci: ")
#     kapasitas = input("Masukkan Kapasitas Mesin Cuci dalam Kg: ")
#     status = 0
#     tarif = input("Masukkan Tarif Mesin Cuci: ")

#     insert_query = '''
#                     INSERT INTO Mesin_Cuci (Nama, Merk, Kapasitas, Status, Tarif)
#                     VALUES (?, ?, ?, ?, ?);
#     '''
#     cursor.execute(insert_query, (nama, merk, kapasitas, status, tarif))
#     cnxn.commit()
#     print("Berhasil menambahkan mesin cuci baru!")

# # Method untuk add customer
# def insert_customer():
#     cursor = cnxn.cursor()
#     nama = input("Masukkan nama pelanggan: ")
#     nohp = input("Masukkan nomor HP pelanggan: ")
#     email = input("Masukkan email pelanggan: ")
#     id_kelurahan = input("Masukkan ID kelurahan pelanggan: ")

#     insert_query = '''
#                     INSERT INTO Pelanggan (Nama, NoHP, Email, id_Kelurahan)
#                     VALUES (?, ?, ?, ?);
#     '''
#     cursor.execute(insert_query, (nama, nohp, email, id_kelurahan))
#     cnxn.commit()

#     cursor.execute('SELECT @@IDENTITY AS PelangganID')
#     pelanggan_id = cursor.fetchone()[0]
#     print(f"Berhasil menambahkan pelanggan baru dengan ID: {pelanggan_id}")
#     return pelanggan_id

# # Method untuk membuat transaksi baru
# def create_transaction():
#     cursor = cnxn.cursor()
#     pelanggan_id = insert_customer()
#     start_time = input("Masukkan waktu mulai menggunakan mesin cuci (format: HH:MM:SS): ")

#     # Ensure proper date format
#     while True:
#         try:
#             date_input = input("Masukkan tanggal transaksi (format: YYYY-MM-DD): ")
#             date = datetime.datetime.strptime(date_input, "%Y-%m-%d").date()
#             break
#         except ValueError:
#             print("Format tanggal salah. Silakan masukkan tanggal dengan format YYYY-MM-DD.")

#     cursor.execute('SELECT * FROM Mesin_Cuci WHERE Status = 0')
#     unused_machines = cursor.fetchall()

#     if len(unused_machines) == 0:
#         print("Maaf, semua mesin cuci sedang digunakan.")
#         return

#     print("\nMesin cuci yang tersedia:")
#     table = PrettyTable()
#     table.field_names = ["ID", "Nama", "Merk", "Kapasitas (Kg)", "Status", "Tarif"]
#     for machine in unused_machines:
#         table.add_row(machine)
#     print(table)

#     machine_id = int(input("Masukkan ID mesin cuci yang ingin digunakan: "))

#     update_query = '''
#                     UPDATE Mesin_Cuci
#                     SET Status = 1
#                     WHERE id_Mesin_Cuci = ?;
#     '''
#     cursor.execute(update_query, (machine_id,))
#     cnxn.commit()

#     # Fetch the cashier's name
#     while True:
#         nama_kasir = input("Masukkan nama kasir: ")
#         cursor.execute("SELECT id_Pengguna FROM Pengguna WHERE Username = ?", (nama_kasir,))
#         id_kasir = cursor.fetchone()
#         if id_kasir:
#             break
#         else:
#             print("Nama kasir tidak valid. Silakan coba lagi.")

#     # Insert transaction
#     insert_query = '''
#                     INSERT INTO Transaksi (IdPelanggan, IdMesinCuci, idPengguna, Waktu_mulai, Total, Tanggal)
#                     VALUES (?, ?, ?, ?, ?, ?);
#                 '''
#     cursor.execute(insert_query, (pelanggan_id, machine_id, id_kasir[0], start_time, 0, date))
#     cnxn.commit()

#     # Fetch the ID of the inserted transaction
#     cursor.execute('SELECT @@IDENTITY AS TransaksiID')
#     transaksi_id = cursor.fetchone()[0]
#     print(f"Transaksi berhasil dibuat dengan ID: {transaksi_id}")

# # Method untuk menyelesaikan transaksi
# def finalize_transaction():
#     cursor = cnxn.cursor()
#     machine_id = input("Masukkan ID mesin cuci: ")
#     end_time = input("Masukkan waktu selesai menggunakan mesin cuci (format: HH:MM:SS): ")

#     cursor.execute('SELECT Waktu_mulai FROM Transaksi WHERE IdMesinCuci = ? AND Waktu_selesai IS NULL', (machine_id,))
#     transaction_details = cursor.fetchone()

#     if not transaction_details:
#         print("Transaksi tidak ditemukan atau sudah diselesaikan.")
#         return

#     start_time = transaction_details[0]

#     cursor.execute('SELECT Tarif FROM Mesin_Cuci WHERE id_Mesin_Cuci = ?', (machine_id,))
#     tarif = cursor.fetchone()[0]

#     start_datetime = datetime.datetime.strptime(str(start_time), "%H:%M:%S")
#     end_datetime = datetime.datetime.strptime(end_time, "%H:%M:%S")
#     duration = int((end_datetime - start_datetime).total_seconds() / 900)  # Satuan 15 menit
#     total_cost = (duration * tarif)

#     update_transaction_query = '''
#                     UPDATE Transaksi
#                     SET Waktu_selesai = ?, Total = ?
#                     WHERE IdMesinCuci = ? AND Waktu_selesai IS NULL;
#     '''
#     cursor.execute(update_transaction_query, (end_time, total_cost, machine_id))
#     cnxn.commit()

#     update_machine_query = '''
#                     UPDATE Mesin_Cuci
#                     SET Status = 0
#                     WHERE id_Mesin_Cuci = ?;
#     '''
#     cursor.execute(update_machine_query, (machine_id,))
#     cnxn.commit()

#     print(f"Transaksi untuk mesin cuci {machine_id} selesai dengan biaya total: {total_cost}")

# # Method untuk mendapatkan laporan keuangan
# def laporan_keuangan():
#     cursor = cnxn.cursor()
#     print("Masukkan range tanggal")
#     tanggal_awal = input("Masukkan tanggal awal: ")
#     tanggal_akhir = input("Masukkan tanggal akhir: ")

#     # Query untuk menampilkan data penghasilan di rentang tanggal tersebut
#     query = '''
#         SELECT IdPelanggan, IdMesinCuci, idPengguna, Waktu_mulai, Waktu_selesai, Total, Tanggal
#         FROM Transaksi
#         WHERE Tanggal BETWEEN ? AND ?
#     '''

#     #Execute Query
#     cursor.execute(query, (tanggal_awal, tanggal_akhir))
#     results = cursor.fetchall()

#     if results:
#         table = PrettyTable()
#         table.field_names = ["IdPelanggan", "IdMesinCuci", "idPengguna", "Waktu_mulai", "Waktu_selesai", "Total", "Tanggal"]
#         for row in results:
#             table.add_row(row)
#         print(table)
#     else:
#         print("Tidak ada data untuk rentang tanggal yang diberikan.")

# # Main menu function
# def main_menu():
#     while True:
#         cek_mesincuci()  # Display the list of washing machines every time the menu is displayed
#         print("\n=== APLIKASI PENGELOLAAN MESIN CUCI ===")
#         print("1. Cek Daftar Mesin Cuci")
#         print("2. Tambah Mesin Cuci Baru")
#         print("3. Tambah Pelanggan Baru dan Transaksi")
#         print("4. Selesaikan Transaksi")
#         print("5. Lihat Laporan Keuangan")
#         print("6. Keluar")

#         try:
#             choice = int(input("Masukkan pilihan: "))

#             if choice == 1:
#                 cek_mesincuci()
#             elif choice == 2:
#                 insert_washing_machine()
#             elif choice == 3:
#                 create_transaction()
#             elif choice == 4:
#                 finalize_transaction()
#             elif choice == 5:
#                 laporan_keuangan()
#             elif choice == 6:
#                 print("Keluar dari program.")
#                 break
#             else:
#                 print("Pilihan tidak valid. Silakan pilih menu yang tersedia.")
#         except ValueError:
#             print("Input tidak valid. Silakan masukkan angka.")

# # Start the program if login successful
# if login_page():
#     main_menu()
