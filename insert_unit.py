import streamlit as st
import mysql.connector
from datetime import datetime
from config import DATABASE_CONFIG


def app():
    st.title("添加单元")
    
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
        
    def check_and_create_trigger(connection):
        cursor = connection.cursor()
        # Check if the trigger already exists
        cursor.execute("SHOW TRIGGERS LIKE 'after_unit_insert'")
        if cursor.fetchone() is None:
            # Trigger does not exist, so create it
            trigger_command = """
                            CREATE TRIGGER after_unit_insert
                            AFTER INSERT ON Unit_test
                            FOR EACH ROW
                            BEGIN
                                DECLARE bedroom_count INT;
                                DECLARE total_division INT;
                                DECLARE base_rent_per_room FLOAT;
                                DECLARE i INT DEFAULT 1;
                            
                                IF NEW.unit_type = 'Studio' THEN
                                    INSERT INTO sub_unit_test (unit_ID, room_type, sub_rent_price, use_livingroom)
                                    VALUES (NEW.Unit_ID, 'Studio', NEW.rent_price, FALSE);
                                ELSE
                                    SET bedroom_count = CAST(SUBSTRING(NEW.unit_type, 1, 1) AS UNSIGNED);
                                    SET total_division = IF(NEW.unit_type = '1b1b', 2, bedroom_count + 1);
                            
                                    IF NEW.unit_type = '1b1b' THEN
                                        INSERT INTO sub_unit_test (unit_ID, room_type, sub_rent_price, use_livingroom)
                                        VALUES (NEW.Unit_ID, 'bedroom1', NEW.rent_price / 2 + 200, TRUE),
                                               (NEW.Unit_ID, 'living_room', NEW.rent_price / 2 - 200, TRUE),
                                               (NEW.Unit_ID, 'bedroom1', NEW.rent_price, FALSE);
                                    ELSE
                                        SET base_rent_per_room = NEW.rent_price / total_division;
                            
                                        WHILE i <= bedroom_count DO
                                            INSERT INTO sub_unit_test (unit_ID, room_type, sub_rent_price, use_livingroom)
                                            VALUES (NEW.Unit_ID, CONCAT('bedroom', i), base_rent_per_room + IF(i = 1, 200, 0), TRUE);
                                            SET i = i + 1;
                                        END WHILE;
                            
                                        INSERT INTO sub_unit_test (unit_ID, room_type, sub_rent_price, use_livingroom)
                                        VALUES (NEW.Unit_ID, 'living_room', base_rent_per_room - 200, TRUE);
                            
                                        SET i = 1;
                                        SET base_rent_per_room = NEW.rent_price / bedroom_count;
                            
                                        WHILE i <= bedroom_count DO
                                            INSERT INTO sub_unit_test (unit_ID, room_type, sub_rent_price, use_livingroom)
                                            VALUES (NEW.Unit_ID, CONCAT('bedroom', i), base_rent_per_room, FALSE);
                                            SET i = i + 1;
                                        END WHILE;
                                    END IF;
                                END IF;
                            END;
                            """
            cursor.execute(trigger_command)
            connection.commit()
        cursor.close()

    
    # Function to add a unit
    def add_unit():
        if 'unit_data' not in st.session_state:
            st.session_state['unit_data'] = None
        with st.form("add_unit_form"):
            col1, col2 = st.columns(2)

            with col1:
                # Column 1 fields
                building_name_options = get_builidng_name()
                building_name = st.selectbox("公寓名称", building_name_options)
                unit_number = st.text_input("单元号")
                rent_price = st.number_input("租金", min_value=0)
                unit_type = st.selectbox("户型", ['Studio', '1b1b', '2b2b', '2b1b', '3b2b', '3b3b', '4b3b', 'other'])
                available_date = st.date_input("起租日期")
                description = st.text_area("单元描述")
                

            with col2:
                # Column 2 fields
                floor_plan_image = st.text_input("户型图url")
                unit_image = st.text_input("单元图片url")
                unit_video = st.text_input("单元视频url")
                broker_fee = st.number_input("中介费", min_value=0)
                interest_pp_num = st.number_input("感兴趣人数", min_value=0)
                washer_dryer = st.selectbox("室内洗烘",["Any","Yes", "No"])

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

            if not building:
                st.warning("请先添加公寓信息")
        
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
                check_and_create_trigger(connection)
    
                st.success("单元已成功添加!")
                
        
    # Call the function to render the form
    add_unit()

if __name__ == "__main__":
    app()

