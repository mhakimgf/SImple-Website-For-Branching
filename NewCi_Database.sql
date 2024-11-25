DROP TABLE IF EXISTS Kecamatan
DROP TABLE IF EXISTS Kelurahan
DROP TABLE IF EXISTS Mesin_Cuci
DROP TABLE IF EXISTS Pelanggan
DROP TABLE IF EXISTS Pengguna
DROP TABLE IF EXISTS Transaksi

--Query untuk membuat tabel yang dibutuhkan
CREATE TABLE Kecamatan (
	id_Kecamatan INT NOT NULL PRIMARY KEY IDENTITY(1,1),
    Nama VARCHAR(100)
);


CREATE TABLE Kelurahan (
    id_Kelurahan INT NOT NULL PRIMARY KEY IDENTITY(1,1),
    Nama VARCHAR(100),
    id_Kecamatan INT --add fk
);


CREATE TABLE Mesin_Cuci (
    id_Mesin_Cuci int NOT NULL PRIMARY KEY IDENTITY(1,1),
    Nama VARCHAR(255),
    Merk VARCHAR(255),
    Kapasitas INT,
    [Status] INT,
    Tarif INT
);


CREATE TABLE Pelanggan (
    id_Pelanggan INT NOT NULL PRIMARY KEY IDENTITY(1,1),
    Nama VARCHAR(100),
    NoHP VARCHAR(20),
    Email VARCHAR(100),
    id_Kelurahan INT --add fk
);


CREATE TABLE Pengguna(
    id_Pengguna INT NOT NULL PRIMARY KEY IDENTITY(1,1),
    TipePengguna VARCHAR(50),
    Username VARCHAR(50),
    Password VARCHAR(50)
);


CREATE TABLE Transaksi (
    IdPelanggan INT,
    IdMesinCuci INT,
    idPengguna INT,
    Waktu_mulai TIME,
    Waktu_selesai TIME,
    Total INT,
    Tanggal DATE,
    FOREIGN KEY (IdPelanggan) REFERENCES Pelanggan(id_Pelanggan),
    FOREIGN KEY (IdMesinCuci) REFERENCES Mesin_Cuci(id_Mesin_Cuci),
    FOREIGN KEY (idPengguna) REFERENCES Pengguna(id_Pengguna)
);

--penambahan constraint foreign key untuk table kelurahan dan kecamatan
ALTER TABLE Kelurahan
	ADD CONSTRAINT [FK_id_Kecamatan]
		FOREIGN KEY (
			id_Kecamatan
		)
		REFERENCES Kecamatan(
			id_Kecamatan
		)

ALTER TABLE Pelanggan
	ADD CONSTRAINT [FK_id_Kelurahan]
		FOREIGN KEY (
			id_Kelurahan
		)
		REFERENCES Kelurahan(
			id_Kelurahan
		)

select * from Kecamatan
select * from Kelurahan
select * from Mesin_Cuci
select * from Pelanggan
select * from Pengguna
select * from Transaksi


--credential pengguna
INSERT INTO Pengguna(TipePengguna, Username, [Password])
VALUES ('Pemilik', 'Dodo', 'DodoGanteng');

--bulk insert Kecamatan
BULK INSERT Kecamatan
FROM "C:\Users\johns\Documents\tugas kuliah\MIBD\Kecamatan_Bandung.csv"
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
)

--bulk insert Kelurahan
BULK INSERT Kelurahan
FROM "C:\Users\johns\Documents\tugas kuliah\MIBD\Kelurahan_Bandung.csv"
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
)


