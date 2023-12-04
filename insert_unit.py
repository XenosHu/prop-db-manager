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

    def get_building_name():
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
        
    # def check_and_create_trigger(connection):
        
    #     cursor = connection.cursor()
    #     # Check if the trigger already exists
    #     cursor.execute("SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA = 'chatbot' AND TRIGGER_NAME = 'after_unit_insert'")
    #     if cursor.fetchone() is None:
    #         # Trigger does not exist, so create it
    #         trigger_command = """
    #                         CREATE TRIGGER after_unit_insert
    #                         AFTER INSERT ON Unit
    #                         FOR EACH ROW
    #                         BEGIN
    #                             DECLARE bedroom_count INT;
    #                             DECLARE total_division INT;
    #                             DECLARE base_rent_per_room FLOAT;
    #                             DECLARE i INT DEFAULT 1;
                            
    #                             IF NEW.unit_type = 'Studio' THEN
    #                                 INSERT INTO sub_unit (unit_ID, room_type, sub_rent_price, use_livingroom)
    #                                 VALUES (NEW.Unit_ID, 'Studio', NEW.rent_price, FALSE);
    #                             ELSE
    #                                 SET bedroom_count = CAST(SUBSTRING(NEW.unit_type, 1, 1) AS UNSIGNED);
    #                                 SET total_division = IF(NEW.unit_type = '1b1b', 2, bedroom_count + 1);
                            
    #                                 IF NEW.unit_type = '1b1b' THEN
    #                                     INSERT INTO sub_unit (unit_ID, room_type, sub_rent_price, use_livingroom)
    #                                     VALUES (NEW.Unit_ID, 'bedroom1', NEW.rent_price / 2 + 200, TRUE),
    #                                            (NEW.Unit_ID, 'living_room', NEW.rent_price / 2 - 200, TRUE),
    #                                            (NEW.Unit_ID, 'bedroom1', NEW.rent_price, FALSE);
    #                                 ELSE
    #                                     SET base_rent_per_room = NEW.rent_price / total_division;
                            
    #                                     WHILE i <= bedroom_count DO
    #                                         INSERT INTO sub_unit (unit_ID, room_type, sub_rent_price, use_livingroom)
    #                                         VALUES (NEW.Unit_ID, CONCAT('bedroom', i), base_rent_per_room + IF(i = 1, 200, 0), TRUE);
    #                                         SET i = i + 1;
    #                                     END WHILE;
                            
    #                                     INSERT INTO sub_unit (unit_ID, room_type, sub_rent_price, use_livingroom)
    #                                     VALUES (NEW.Unit_ID, 'living_room', base_rent_per_room - 200, TRUE);
                            
    #                                     SET i = 1;
    #                                     SET base_rent_per_room = NEW.rent_price / bedroom_count;
                            
    #                                     WHILE i <= bedroom_count DO
    #                                         INSERT INTO sub_unit (unit_ID, room_type, sub_rent_price, use_livingroom)
    #                                         VALUES (NEW.Unit_ID, CONCAT('bedroom', i), base_rent_per_room, FALSE);
    #                                         SET i = i + 1;
    #                                     END WHILE;
    #                                 END IF;
    #                             END IF;
    #                         END;
    #                         """
    #         cursor.execute(trigger_command)
    #         connection.commit()
    #     # cursor.close()

    def add_unit():
        if 'unit_data' not in st.session_state:
            st.session_state['unit_data'] = None
        with st.form("add_unit_form"):
            col1, col2 = st.columns(2)
    
            with col1:
                # Column 1 fields
                # building_id_options = get_building_id()  # Assuming this function fetches building IDs
                # building_id = st.selectbox("楼宇编号", building_id_options)
                building_name_options = get_building_name()
                building_name = st.selectbox("公寓名称", building_name_options)
                unit_number = st.text_input("单元号")
                rent_price = st.number_input("租金", min_value=0)
                floorplan = st.selectbox("户型", ['Studio', '1b1b', '2b2b', '2b1b', '3b2b', '3b3b', '4b3b', 'other'])
                available_date = st.date_input("起租日期")
                sqft = st.number_input("单元面积", min_value=0)
                washer_dryer = st.selectbox("室内洗烘", ["Any","Yes", "No"])
                description = st.text_area("单元描述")
    
            with col2:
                # Column 2 fields
                unit_image = st.text_input("单元图片URL")
                unit_video = st.text_input("单元视频URL")
                floorplan_image = st.text_input("户型图像URL")
                direction = st.selectbox("房间朝向", ["N", "S", "E", "W", "NE", "NW", "SE", "SW"])
                concession = st.text_input("优惠")
                broker_fee = st.number_input("中介费", min_value=0)
                interest_pp_num = st.number_input("感兴趣人数", min_value=0)
    
            unit_form_submitted = st.form_submit_button("添加单元")
            
        if unit_form_submitted:         
            # Save Unit data to session state
            st.session_state['unit_data'] = {
                'building_name': building_name,
                'unit_number': unit_number,
                'rent_price': rent_price,
                'floorplan': floorplan,
                'floorplan_image': floorplan_image,
                'unit_image': unit_image,
                'unit_video': unit_video,
                'unit_description': description,
                'broker_fee': broker_fee,
                'sqft': sqft,
                'concession': concession,
                'direction': direction,
                'available_date': available_date,
                'washer_dryer': washer_dryer,
                'interest_pp_num': interest_pp_num
            }
            
            # Assuming you have a function to handle the database connection
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
                        building_name, unit_number, rent_price, floorplan, floorplan_image, 
                        unit_image, unit_video, unit_description, broker_fee, sqft, concession, 
                        direction, available_date, washer_dryer, interest_pp_num
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
                
    
                st.success("单元已成功添加!")
                
        
    # Call the function to render the form
    add_unit()

if __name__ == "__main__":
    app()

