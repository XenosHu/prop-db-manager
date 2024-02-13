import streamlit as st
import mysql.connector
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from config import DATABASE_CONFIG

def app():
    st.title("更新User")

    # Function to get database connection
    def get_db_connection():
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        return connection

    # Function to execute read query
     def execute_read_query(query=None):
        # st.write(query)
        connection = get_db_connection()
        if query is None:
            # Adjust this default query as per your requirements
            query = """
            SELECT Unit.*, Building.building_name, Building.location
            FROM Unit
            JOIN Building ON Unit.building_id = Building.building_id
            """
        df = pd.read_sql(query, connection)
        connection.close()
        return df
         
    def execute_write_query(query, params=None):
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
            st.write(query,params)
        except mysql.connector.Error as error:
            print(f"Failed to execute query: {error}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()
        return None


    def get_chatbot_wx_ids():
        query = "SELECT DISTINCT chatbot_wx_id FROM user WHERE chatbot_wx_id IS NOT NULL"
        df = execute_read_query(query)
        return df['chatbot_wx_id'].tolist()
        
    with st.form("search_form"):
        chatbot_wx_ids = get_chatbot_wx_ids()
        chatbot_wx_id = st.selectbox("Chatbot 微信ID", ['Any'] + chatbot_wx_ids)
        sche_listing_options = ["Any", "Yes", "No"]
        sche_listing = st.selectbox("是否推房", options=sche_listing_options)
        search_user = st.form_submit_button("显示表格")

    # Handle Search
    if search_user:
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
        st.session_state['search_results'] = df

    # Display Search Results
    if 'search_results' in st.session_state:
        df = st.session_state['search_results']

        # Set up AgGrid options for editable grid
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=True, minWidth=150)
        gb.configure_selection('multiple', use_checkbox=True)
        grid_options = gb.build()

        # Display the grid
        grid_response = AgGrid(
            df, 
            gridOptions=grid_options,
            height=600, 
            width='100%',
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED',
            fit_columns_on_grid_load=True
        )

        if 'data' in grid_response:
            updated_df = grid_response['data']
            if not updated_df.equals(df):
                if st.button('更新'):

                    for i in updated_df.index:
                        set_clauses = []
                        params = []
                        for col in updated_df.columns:
                            if col != 'user_id':  # 排除 user_id 作为更新的一部分，但将其用作 WHERE 条件
                                set_clauses.append(f"{col} = %s")
                                params.append(updated_df.at[i, col])
                        user_update_query = f"UPDATE user SET {', '.join(set_clauses)} WHERE user_id = %s"
                        params.append(updated_df.at[i, 'user_id'])  # 将 user_id 添加到参数列表的末尾，用于 WHERE 条件
                        execute_write_query(user_update_query, params)
                    
                    st.success("更新成功！")

        selected = grid_response['selected_rows']
        if selected:
            st.session_state['selected_for_deletion'] = selected
            
            if st.button('删除'):
                for row in st.session_state['selected_for_deletion']:
                    user_delete_query = f"DELETE FROM user WHERE user_id = {row['user_id']}"
                    execute_write_query(user_delete_query)
                st.success("删除成功！")


       

if __name__ == "__main__":
    app()
