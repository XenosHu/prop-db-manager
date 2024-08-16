import streamlit as st
import mysql.connector
from datetime import datetime
from config import DATABASE_CONFIG

def app():
    st.title("添加公寓")
    
    # Function to get database connection
    def get_db_connection():
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        return connection

    def get_builidng_name():
            connection = get_db_connection()
            cursor = connection.cursor()
            building_name_options = ['other']
            # Check if the building exists
            cursor.execute("SELECT Building_name FROM Building")
            building_names = cursor.fetchall()
            for building_name in building_names:
                building_name_options.append(building_name[0])

            connection.close()
            return building_name_options
    
    # Function to add a unit
    def add_building():
       
        with st.form("building_form"):
            col1, col2 = st.columns(2)
    
            with col1:
                # Column 1 fields
                source = st.text_input('Source')
                building_name = st.text_input("大楼名称")
                address = st.text_input("address")
                location = st.selectbox("区域", ["New Jersey", "Manhattan upper", "Manhattan lower", "LIC", "Brooklyn", "Bronx", "Queens", "Other"])
                amenity = st.text_area("公寓设施")
                
    
            with col2:
                # Column 2 fields
                building_description = st.text_area("大楼介绍")
                building_location_image = st.text_input("大楼位置图片url")
                pet = st.checkbox("宠物友好", value=False)
                op = st.checkbox("OP", value=False)
                movein_range = st.number_input("move_in_range", min_value=0, step=1, format='%d')
                
                tavel_NYU = st.number_input("通勤NYU", min_value=0, step=1, format='%d')
                tavel_CU = st.number_input("通勤哥大", min_value=0, step=1, format='%d')
                tavel_PS = st.number_input("通勤Parsons", min_value=0, step=1, format='%d')
                tavel_SVA = st.number_input("通勤SVA", min_value=0, step=1, format='%d')

                
      
            building_form_submitted = st.form_submit_button("添加公寓")
            
            if building_form_submitted:
                
                try:
                    connection = get_db_connection()
                    cursor = connection.cursor()

                    building_insert_query = """
                        INSERT INTO Building (
                            building_name, location, building_description, building_location_image, pet, 
                            op,movein_range,travel_NYU,travel_ColumbiaUniversity,travel_Parsons,travel_SVA, amenity, address,source
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(building_insert_query, (
                        building_name, location, building_description,building_location_image, pet, 
                       op,movein_range,tavel_NYU,tavel_CU,tavel_PS,tavel_SVA, amenity, address, source
                    ))
    
                    connection.commit()
                    
                    st.success("大楼信息已成功添加！")
                    
                except mysql.connector.Error as e:
                    st.error(f"数据库错误: {e}")
                finally:
                    cursor.close()
                    connection.close()    

        
    # Call the function to render the form
    add_building()

if __name__ == "__main__":
    app()

