import streamlit as st
import mysql.connector
from datetime import datetime
from config import DATABASE_CONFIG

def app():
    st.title("添加房源")
    
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
    def add_unit():
        if 'unit_data' not in st.session_state:
            st.session_state['unit_data'] = None
        with st.form("add_unit_form"):
            st.write("添加单元")
            
            # Input fields
            unit_number = st.text_input("单元号")
            rent_price = st.number_input("租金", min_value=0)
            unit_type = st.selectbox("户型", ['Studio', '1b1b', '2b2b', '2b1b', '3b2b', '3b3b', '4b3b', 'other'])
            floor_plan_image = st.text_input("户型图url")
            unit_image = st.text_input("单元图片url")
            unit_video = st.text_input("单元视频url")
            description = st.text_area("单元描述")
            broker_fee = st.number_input("中介费", min_value=0)
            available_date = st.date_input("起租日期")
            washer_dryer = st.checkbox("室内洗烘")
            interest_pp_num = st.number_input("感兴趣人数", min_value=0)
            
            building_name_options = get_builidng_name()
            building_name = st.selectbox("大楼名称", building_name_options)

            unit_form_submitted = st.form_submit_button("添加单元")
            
        if unit_form_submitted:
            
                # 保存Unit数据到会话状态
            st.session_state['unit_data'] = {
                    'unit_number': unit_number,
                    'rent_price': rent_price,
                    'unit_type': unit_type,
                    'floor_plan_image': floor_plan_image,
                    'unit_image': unit_image,
                    'unit_video': unit_video,
                    'description': description,
                    'broker_fee': broker_fee,
                    'available_date': available_date,
                    'washer_dryer': washer_dryer,
                    'interest_pp_num': interest_pp_num,
                    'building_name': building_name
                }
                
            connection = get_db_connection()
            cursor = connection.cursor()

            # Check if the building exists
            cursor.execute("SELECT Building_ID FROM Building WHERE Building_name = %s", (building_name,))
            building = cursor.fetchone()
            st.write(building)

            if not building:
                st.warning("Building not found in the database. Please enter the Building information.")
        
            else:
                building_id = building[0]
                unit_insert_query = """
                    INSERT INTO Unit (
                        building_id, unit_number, rent_price, unit_type, floor_plan_image, 
                        unit_image, unit_video, unit_description, broker_fee, available_date, 
                        washer_dryer, interest_pp_num
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(unit_insert_query, (
                    building_id, unit_number, rent_price, unit_type, floor_plan_image,
                    unit_image, unit_video, description, broker_fee, available_date,
                    washer_dryer, interest_pp_num
                ))
    
                # Commit transaction and close connection
                connection.commit()
                cursor.close()
                connection.close()
    
                st.success("Unit added successfully!")
                
        with st.form("building_form"):
            st.write("添加大楼")

            # Additional Building info fields
            building_name = st.text_input("大楼名称")
            website = st.text_input("网站")
            location = st.selectbox("区域",["New Jersey", "Manhattan upper", "Manhattan mid", "Manhattan lower", "LIC", "Brooklyn",'other'])
            address = st.text_input("详细地址")
            building_description = st.text_area("大楼介绍")
            building_image = st.text_input("大楼图片url")
            building_location_image = st.text_input("大楼位置图片url")
            postcode = st.text_input("邮编")
            pet = st.checkbox("宠物友好")
            application_material = st.text_area("申请材料")
            amenity_image = st.text_input("设施图片url")
            washer_dryer_image = st.text_input("洗烘设备url")
            building_form_submitted = st.form_submit_button("添加大楼")
            
            if building_form_submitted:
                
                try:
                    connection = get_db_connection()
                    cursor = connection.cursor()

                    building_insert_query = """
                        INSERT INTO Building (
                            Building_name, website, location, address, building_description, 
                            building_image, building_location_image, postcode, pet, 
                            application_material, amenity_image, washer_dryer_image
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(building_insert_query, (
                        building_name, website, location, address, building_description,
                        building_image, building_location_image, postcode, pet,
                        application_material, amenity_image, washer_dryer_image
                    ))
    
                    connection.commit()
                    
                    st.success("大楼信息已成功添加！")
                    del st.session_state['unit_data']
                    
                except mysql.connector.Error as e:
                    st.error(f"数据库错误: {e}")
                finally:
                    cursor.close()
                    connection.close()    

        
    # Call the function to render the form
    add_unit()

if __name__ == "__main__":
    app()

