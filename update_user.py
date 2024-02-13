import streamlit as st
import mysql.connector
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from config import DATABASE_CONFIG
import numpy as np

def app():
    st.title("更新User")

    def get_db_connection():
        return mysql.connector.connect(**DATABASE_CONFIG)

    def execute_read_query(query):
        connection = get_db_connection()
        df = pd.read_sql(query, connection)
        connection.close()
        return df

    def execute_write_query(query, params):
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
        except mysql.connector.Error as error:
            st.error(f"Failed to execute query: {error}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def get_chatbot_wx_ids():
        query = "SELECT DISTINCT chatbot_wx_id FROM user WHERE chatbot_wx_id IS NOT NULL"
        df = execute_read_query(query)
        return df['chatbot_wx_id'].tolist()

    def find_changes(original_df, updated_df):
        changes = []
        for i in updated_df.index:
            for col in updated_df.columns:
                if updated_df.at[i, col] != original_df.at[i, col]:
                    changes.append({
                        'user_id': updated_df.at[i, 'user_id'],
                        'field_name': col,
                        'new_value': updated_df.at[i, col]
                    })
        return changes

    def update_database(updates):
        for update in updates:
            query = f"UPDATE user SET {update['field_name']} = %s WHERE user_id = %s"
            params = (update['new_value'], update['user_id'])
            execute_write_query(query, params)

    chatbot_wx_ids = get_chatbot_wx_ids()
    chatbot_wx_id = st.selectbox("Chatbot 微信ID", ['Any'] + chatbot_wx_ids)
    sche_listing_options = ["Any", "Yes", "No"]
    sche_listing = st.selectbox("是否推房", options=sche_listing_options)

    if st.button("显示表格"):
        search_query = """
        SELECT user_id, preference, roommate_preference, sex, wechat_id, conversation, chatbot_wx_id, sche_listing
        FROM user
        WHERE 1=1
        """
        if chatbot_wx_id != 'Any':
            search_query += f" AND chatbot_wx_id = '{chatbot_wx_id}'"
        if sche_listing != "Any":
            sche_listing_value = 1 if sche_listing == "Yes" else 0
            search_query += f" AND sche_listing = {sche_listing_value}"
        
        df = execute_read_query(search_query)
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=True)
        gb.configure_selection('multiple', use_checkbox=True)
        grid_options = gb.build()
        grid_response = AgGrid(df, gridOptions=grid_options, update_mode='MODEL_CHANGED', fit_columns_on_grid_load=True)
        
        if 'data' in grid_response:
            updated_df = grid_response['data']
            st.session_state['updated_df'] = updated_df

    if 'updated_df' in st.session_state:
        if st.button('提交更改'):
            original_df = execute_read_query(search_query)  # 重新获取原始数据以查找更改
            changes = find_changes(original_df, st.session_state['updated_df'])
            if changes:
                update_database(changes)
                st.success("所有更改已成功提交到数据库。")
            else:
                st.info("没有检测到更改。")

if __name__ == "__main__":
    app()
