import pymysql

pymysql.install_as_MySQLdb()

def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='SotfwareUser',
        db='library',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
