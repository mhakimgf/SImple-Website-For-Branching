#Db connection logic
# db.py
import pyodbc

# def get_connection():
#     server = "LAPTOP-5GNHDDSL\\SQLEXPRESS"
#     database = "NewCi"
#     connection = pyodbc.connect(
#         f'DRIVER={{ODBC Driver 17 for SQL Server}};'
#         f'SERVER={server};'
#         f'DATABASE={database};'
#         'Trusted_Connection=yes'
#     )
#     return connection

#koneksi hakim
def get_connection():
    sql_conn_String = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=LAPTOP-9Q8UL4FR\\SQLEXPRESS;'
    'DATABASE=manpro;'
    'UID=AkunTubes;'
    'PWD=mibd04;'
    )
    connection = pyodbc.connect(sql_conn_String)
    return connection