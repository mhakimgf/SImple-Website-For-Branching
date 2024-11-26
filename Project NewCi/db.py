#Db connection logic
# db.py
import pyodbc

def get_connection():
    server = "LAPTOP-5GNHDDSL\\SQLEXPRESS"
    database = "NewCi"
    connection = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        'Trusted_Connection=yes'
    )
    return connection
