import sqlite3
import pandas as pd
import streamlit as st 

def connect_database():
    # Kết nối SQLite
    conn = sqlite3.connect('model/database.db')
    cursor = conn.cursor()
    return conn, cursor

def get_list_dict_info(query):
    conn, cursor = connect_database()
    
    # Truy vấn và chuyển thẳng về DataFrame
    cursor.execute(query)
    
    # Lấy tên các cột
    columns = [desc[0] for desc in cursor.description]

    # Lấy tất cả các dòng dữ liệu
    rows = cursor.fetchall()

    # Chuyển từng dòng thành dict
    result_list = [dict(zip(columns, row)) for row in rows]

    # Đóng kết nối nếu không dùng nữa
    conn.close()
    
    return result_list
    
def get_df_info(query):
    conn, cursor = connect_database()
    
    # Truy vấn và chuyển thẳng về DataFrame
    df = pd.read_sql_query(query, conn)

    # Đóng kết nối nếu không dùng nữa
    conn.close()
    
    return df