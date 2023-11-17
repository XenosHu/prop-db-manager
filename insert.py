import streamlit as st
import mysql.connector
from datetime import datetime

def app():
    st.title("Insert Data")
    # Database configuration
    config = {
        'user': 'propbotics',
        'password': 'Propbotics123',
        'host': 'chatbot.c0xmynwsxhmo.us-east-1.rds.amazonaws.com',
        'database': 'chatbot',
        'port': 3306
    }
    
    # Function to get database connection
    def get_db_connection():
        connection = mysql.connector.connect(**config)
        return connection
    
    # Function to add a unit
    def add_unit():
        if 'unit_data' not in st.session_state:
            st.session_state['unit_data'] = None
        with st.form("add_unit_form"):
            st.write("Add a New Unit")
            
            # Input fields
            unit_number = st.text_input("Unit Number")
            rent_price = st.number_input("Rent Price", min_value=0)
            unit_type = st.text_input("Unit Type")
            floor_plan_image = st.text_input("Floor Plan Image URL")
            unit_image = st.text_input("Unit Image URL")
            unit_video = st.text_input("Unit Video URL")
            description = st.text_area("Description")
            broker_fee = st.number_input("Broker Fee", min_value=0)
            available_date = st.date_input("Available Date")
            washer_dryer = st.checkbox("Washer Dryer")
            interest_pp_num = st.number_input("Interest PP Num", min_value=0)
            building_name = st.text_input("Building Name")
            unit_form_submitted = st.form_submit_button("Submit Unit")
            
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
                st.warning("Building not found in the database. Please enter the Building information.")
                with st.form("building_form"):
                    st.write("Building Information")

                    # Additional Building info fields
                    website = st.text_input("Building Website")
                    location = st.text_input("Building Location")
                    address = st.text_input("Building Address")
                    building_description = st.text_area("Building Description")
                    building_image = st.text_input("Building Image URL")
                    building_location_image = st.text_input("Building Location Image URL")
                    postcode = st.text_input("Postcode")
                    pet = st.checkbox("Pet Friendly")
                    application_material = st.text_area("Application Material")
                    amenity_image = st.text_input("Amenity Image URL")
                    washer_dryer_image = st.text_input("Washer Dryer Image URL")
                    building_form_submitted = st.form_submit_button("Submit Building")
                    
                    if building_form_submitted:
                        building_insert_query = """
                                INSERT INTO Building (
                                    Building_name, website, location, address, description, 
                                    building_image, building_location_image, postcode, pet, 
                                    application_material, amenity_image, washer_dryer_image
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                        cursor.execute(building_insert_query, (
                            building_name, website, location, address, building_description,
                            building_image, building_location_image, postcode, pet,
                            application_material, amenity_image, washer_dryer_image
                        ))
                        building_id = cursor.lastrowid
            
                        # Insert Unit data
                        unit_insert_query = """
                            INSERT INTO Unit (
                                building_id, unit_number, rent_price, unit_type, floor_plan_image, 
                                unit_image, unit_video, description, broker_fee, available_date, 
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
            
                        st.success("Unit and Building added successfully!")
                        # 清除会话状态中的Unit数据
                        del st.session_state['unit_data']
            else:
                building_id = building[0]
                unit_insert_query = """
                    INSERT INTO Unit (
                        building_id, unit_number, rent_price, unit_type, floor_plan_image, 
                        unit_image, unit_video, description, broker_fee, available_date, 
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

        
    # Call the function to render the form
    add_unit()

if __name__ == "__main__":
    app()

