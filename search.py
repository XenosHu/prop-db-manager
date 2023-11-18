import streamlit as st
import mysql.connector
import pandas as pd
from config import DATABASE_CONFIG

def app():
    st.title("Property Management Dashboard")

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

    # Function to execute read query
    def execute_read_query(query):
        connection = get_db_connection()
        df = pd.read_sql(query, connection)
        connection.close()
        return df

    # Function to execute write query (update, delete)
    def execute_write_query(query):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()

    # Display sub_unit and its corresponding unit, building, and user information
    query = """
SELECT 
    sub_unit.sub_unit_id AS sub_unit_id,
    sub_unit.unit_ID AS sub_unit_unit_ID,
    sub_unit.room_type AS sub_unit_room_type,
    sub_unit.sub_rent_price AS sub_unit_sub_rent_price,
    sub_unit.use_livingroom AS sub_unit_use_livingroom,
    sub_unit.interest_pp_id AS sub_unit_interest_pp_id,
    Unit.Unit_ID AS Unit_Unit_ID,
    Unit.building_id AS Unit_building_id,
    Unit.unit_number AS Unit_unit_number,
    Unit.rent_price AS Unit_rent_price,
    Unit.unit_type AS Unit_unit_type,
    Unit.floor_plan_image AS Unit_floor_plan_image,
    Unit.unit_image AS Unit_unit_image,
    Unit.unit_video AS Unit_unit_video,
    Unit.description AS Unit_description,
    Unit.broker_fee AS Unit_broker_fee,
    Unit.available_date AS Unit_available_date,
    Unit.washer_dryer AS Unit_washer_dryer,
    Unit.interest_pp_num AS Unit_interest_pp_num,
    Building.Building_ID AS Building_Building_ID,
    Building.Building_name AS Building_Building_name,
    Building.website AS Building_website,
    Building.location AS Building_location,
    Building.address AS Building_address,
    Building.description AS Building_description,
    Building.building_image AS Building_building_image,
    Building.building_location_image AS Building_building_location_image,
    Building.postcode AS Building_postcode,
    Building.pet AS Building_pet,
    Building.application_material AS Building_application_material,
    Building.amenity_image AS Building_amenity_image,
    Building.washer_dryer_image AS Building_washer_dryer_image,
    user.user_id AS user_user_id,
    user.preference AS user_preference,
    user.roommate_preference AS user_roommate_preference,
    user.sex AS user_sex
FROM 
    sub_unit
JOIN 
    Unit ON sub_unit.unit_ID = Unit.Unit_ID
JOIN 
    Building ON Unit.building_id = Building.Building_ID
JOIN 
    user ON sub_unit.interest_pp_id = user.user_id;

    """
    df = execute_read_query(query)
    st.write("Sub-unit Information", df)

    # Update and Delete Section
    st.subheader("Update or Delete Data")
    record_to_update = st.text_input("Enter Record ID for Update/Delete")
    update_field = st.selectbox("Select Field to Update", ["sub_rent_price", "use_livingroom"])
    new_value = st.text_input("Enter New Value for Update")
    update_button = st.button("Update Record")
    delete_button = st.button("Delete Record")

    # Handle Update
    if update_button:
        update_query = f"UPDATE sub_unit SET {update_field} = '{new_value}' WHERE sub_unit_id = {record_to_update}"
        execute_write_query(update_query)
        st.success("Record Updated")

    # Handle Delete
    if delete_button:
        delete_query = f"DELETE FROM sub_unit WHERE sub_unit_id = {record_to_update}"
        execute_write_query(delete_query)
        st.success("Record Deleted")

if __name__ == "__main__":
    app()
