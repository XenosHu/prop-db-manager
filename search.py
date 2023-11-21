import streamlit as st
import mysql.connector
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from config import get_database_config


def app():
    st.title("搜索房源")

    # Function to get database connection
    def get_db_connection():
        DATABASE_CONFIG = get_database_config()
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        return connection

    # Function to execute read query
    def execute_read_query(query=None):
        connection = get_db_connection()
        if query is None:
            # Adjust this default query as per your requirements
            query = """
            SELECT Unit.*, Building.Building_name, Building.location
            FROM Unit
            JOIN Building ON Unit.building_id = Building.Building_ID
            """
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
        
    with st.form("search_form"):
        col1, col2 = st.columns(2)

        with col1:
            # 第一列的字段
            building_name = st.text_input("大楼名称")
            min_price = st.number_input("最低价格", min_value=0, step=1, format='%d')
            max_price = st.number_input("最高价格", min_value=0, step=1, format='%d')
            location_options = ["Any", "New Jersey", "Manhattan upper", "Manhattan mid", "Manhattan lower", "LIC", "Brooklyn"]
            location = st.multiselect("位置", options=location_options, default=["Any"])
            washer_dryer = st.selectbox("室内洗烘", ["Any", "Yes", "No"])
        
        with col2:
            # 第二列的字段
            pet = st.selectbox("宠物", ["Any", "Yes", "No"])
            roomtype_options = ["Any", 'Studio', '1b1b', '2b2b', '2b1b', '3b2b', '4b3b', '3b3b']
            roomtype = st.multiselect("户型", options=roomtype_options, default=["Any"])
            roomtype_subunit = st.multiselect("房型", options=["Any", 'bedroom1', 'bedroom2', 'bedroom3', 'living room'], default=["Any"])
            available_start_date = st.date_input("入住时间")
            available_end_date = st.date_input("至")

        search_button = st.form_submit_button("搜索")


    # Handle Search
    if search_button:

        st.session_state['include_building_only'] = False
        st.session_state['include_unit'] = False
        st.session_state['include_subunit'] = False

        include_building = building_name != ""
        include_unit = max_price != 0 or washer_dryer != "Any" or pet != "Any" or location != ["Any"]
        include_subunit = roomtype_subunit != ["Any"]
        
        search_query = "SELECT "
        search_conditions = []
        join_conditions = ""

        if include_subunit:
            # Query to include Sub_Unit, Unit, and Building
            search_query += "Sub_Unit.*, Unit.*, Building.* FROM Sub_Unit "
            join_conditions += "JOIN Unit ON Sub_Unit.unit_ID = Unit.Unit_ID JOIN Building ON Unit.building_id = Building.Building_ID "
            roomtype_conditions = ["Sub_Unit.room_type = '{}'".format(rt) for rt in roomtype_subunit]
            search_conditions.append("({})".format(" OR ".join(roomtype_conditions)))
            if available_start_date:
                search_conditions.append(f"Unit.available_date >= '{available_start_date}'")
            if available_end_date:
                search_conditions.append(f"Unit.available_date <= '{available_end_date}'")
            st.session_state['include_subunit'] = True
            st.write("房型:")
            
        elif include_unit:
            # Query to include Unit and Building
            search_query += "Unit.*, Building.* FROM Unit "
            join_conditions += "JOIN Building ON Unit.building_id = Building.Building_ID "
            if available_start_date:
                search_conditions.append(f"Unit.available_date >= '{available_start_date}'")
            if available_end_date:
                search_conditions.append(f"Unit.available_date <= '{available_end_date}'")
            st.write("单元:")
            st.session_state['include_unit'] = True
        else:
            # Query to include only Building
            search_query += "* FROM Building "
            st.write("公寓:")
            st.session_state['include_building_only'] = True
            
    
        if building_name:
            search_conditions.append(f"Building.Building_name LIKE '%{building_name}%'")
        if min_price and max_price:
            search_conditions.append(f"Unit.rent_price BETWEEN {min_price} AND {max_price}")
        if "Any" not in location:
            location_conditions = ["Building.location LIKE '%{}%'".format(loc) for loc in location]
            search_conditions.append("({})".format(" OR ".join(location_conditions)))
        if washer_dryer != "Any":
            washer_dryer_val = 1 if washer_dryer == "Yes" else 0
            search_conditions.append(f"Unit.washer_dryer = {washer_dryer_val}")
        if pet != "Any":
            pet_val = 1 if pet == "Yes" else 0
            search_conditions.append(f"Building.pet = {pet_val}")
            
        if "Any" not in roomtype:
            roomtype_conditions = ["Unit.unit_type LIKE '%{}%'".format(loc) for loc in roomtype]
            search_conditions.append("({})".format(" OR ".join(roomtype_conditions)))


        final_query = search_query + join_conditions
        if search_conditions:
            final_query += "WHERE " + " AND ".join(search_conditions)

        df = execute_read_query(final_query)
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
            height=300, 
            width='100%',
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED',
            fit_columns_on_grid_load=True
        )

        if 'data' in grid_response:
            updated_df = grid_response['data']
            if not updated_df.equals(df):
                st.session_state['updated_df'] = updated_df

        # Store selected rows for deletion
        selected = grid_response['selected_rows']
        if selected:
            st.session_state['selected_for_deletion'] = selected
            #st.write("Selected rows:", selected)

        # Confirm Update Button
        if st.button('更新/删除'):

            is_building_only = st.session_state.get('include_building_only', False)
            is_unit_included = st.session_state.get('include_unit', False)
            is_subunit_included = st.session_state.get('include_subunit', False)

           #st.write(is_building_only,is_unit_included,is_subunit_included)

            building_columns = [
                "Building_name", "website", "location", "address",
                "building_description", "building_image", "building_location_image",
                "postcode", "pet", "application_material", "amenity_image", "washer_dryer_image"
            ]

            unit_columns = [
                "unit_number", "rent_price", "unit_type",
                "floor_plan_image", "unit_image", "unit_video", "unit_description",
                "broker_fee", "available_date", "washer_dryer", "interest_pp_num"
            ]

            user_columns = [
                "user_id", "preference", "roommate_preference", "sex"
            ]

            sub_unit_columns = [
                 "room_type", "sub_rent_price",
                "use_livingroom", "interest_pp_id"
            ]
            
            if 'updated_df' in st.session_state:
                updated_df = st.session_state['updated_df']

                # Handle updates for Building, Unit, and Sub_Unit
                for i in updated_df.index:
                    if is_subunit_included:
                        # Construct and execute UPDATE query for Sub_Unit
                        sub_unit_update_query = "UPDATE Sub_Unit SET "
                        sub_unit_update_query += ", ".join([f"{col} = '{updated_df.at[i, col]}'" for col in updated_df.columns if col in sub_unit_columns])
                        sub_unit_update_query += f" WHERE sub_unit_id = {updated_df.at[i, 'sub_unit_id']}"
                        execute_write_query(sub_unit_update_query)

                    if is_unit_included and not is_subunit_included:
                        # Construct and execute UPDATE query for Unit
                        unit_update_query = "UPDATE Unit SET "
                        unit_update_query += ", ".join([f"{col} = '{updated_df.at[i, col]}'" for col in updated_df.columns if col in unit_columns])
                        unit_update_query += f" WHERE Unit_ID = {updated_df.at[i, 'Unit_ID']}"
                        execute_write_query(unit_update_query)

                    if is_building_only:
                        # Construct and execute UPDATE query for Building
                        building_update_query = "UPDATE Building SET "
                        building_update_query += ", ".join([f"{col} = '{updated_df.at[i, col]}'" for col in updated_df.columns if col in building_columns])
                        building_update_query += f" WHERE Building_ID = {updated_df.at[i, 'Building_ID']}"
                        execute_write_query(building_update_query)
                del st.session_state['updated_df']  # Clear the updated data from the session state

            # Handle deletions
            if 'selected_for_deletion' in st.session_state:

                for row in st.session_state['selected_for_deletion']:
                    if is_subunit_included:
                        # DELETE FROM Sub_Unit WHERE sub_unit_id = value
                        sub_unit_delete_query = f"DELETE FROM Sub_Unit WHERE sub_unit_id = {row['sub_unit_id']}"
                        execute_write_query(sub_unit_delete_query)

                    elif is_unit_included:
                        # DELETE FROM Unit WHERE unit_id = value
                        unit_delete_query = f"DELETE FROM Unit WHERE Unit_ID = {row['Unit_ID']}"
                        execute_write_query(unit_delete_query)

                    elif is_building_only:
                        # DELETE FROM Building WHERE building_id = value
                        building_delete_query = f"DELETE FROM Building WHERE Building_ID = {row['Building_ID']}"
                        execute_write_query(building_delete_query)
                            
        
                st.success("Database Updated Successfully")


if __name__ == "__main__":
    app()
