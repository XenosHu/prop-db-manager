from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# 数据库配置
config = {
    'user': 'propbotics',
    'password': 'Propbotics123',
    'host': 'chatbot.c0xmynwsxhmo.us-east-1.rds.amazonaws.com',
    'database': 'chatbot',
    'port': 3306
}

def get_db_connection():
    connection = mysql.connector.connect(**config)
    return connection

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_unit', methods=['GET', 'POST'])
def add_unit():
    if request.method == 'POST':
        # 提取表单数据
        unit_data = {
            'unit_number': request.form['unit_number'],
            'rent_price': request.form['rent_price'],
            'unit_type': request.form['unit_type'],
            'floor_plan_image': request.form.get('floor_plan_image', ''),
            'unit_image': request.form.get('unit_image', ''),
            'unit_video': request.form.get('unit_video', ''),
            'description': request.form.get('description', ''),
            'broker_fee': request.form.get('broker_fee', 0),
            'available_date': request.form.get('available_date', None),
            'washer_dryer': bool(request.form.get('washer_dryer')),
            'interest_pp_num': request.form.get('interest_pp_num', 0),
            'building_name': request.form['building_name'],
        }

        # 连接数据库
        connection = get_db_connection()
        cursor = connection.cursor()

        # 检查 Building 是否存在
        cursor.execute("SELECT Building_ID FROM Building WHERE Building_name = %s", (unit_data['building_name'],))
        building = cursor.fetchone()

        if building:
            building_id = building[0]
        else:
            # 插入新的 Building 记录
            building_insert_query = """
                INSERT INTO Building (
                    Building_name, website, location, address, description, 
                    building_image, building_location_image, postcode, pet, 
                    application_material, amenity_image, washer_dryer_image
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(building_insert_query, (
                unit_data['building_name'], 
                request.form.get('website', ''),
                request.form.get('location', ''),
                request.form.get('address', ''),
                request.form.get('building_description', ''),
                request.form.get('building_image', ''),
                request.form.get('building_location_image', ''),
                request.form.get('postcode', 0),
                bool(request.form.get('pet')),
                request.form.get('application_material', ''),
                request.form.get('amenity_image', ''),
                request.form.get('washer_dryer_image', '')
            ))
            building_id = cursor.lastrowid

        # 插入 Unit 数据
        unit_insert_query = """
            INSERT INTO Unit (
                building_id, unit_number, rent_price, unit_type, floor_plan_image, 
                unit_image, unit_video, description, broker_fee, available_date, 
                washer_dryer, interest_pp_num
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(unit_insert_query, (
            building_id,
            unit_data['unit_number'],
            unit_data['rent_price'],
            unit_data['unit_type'],
            unit_data['floor_plan_image'],
            unit_data['unit_image'],
            unit_data['unit_video'],
            unit_data['description'],
            unit_data['broker_fee'],
            unit_data['available_date'],
            unit_data['washer_dryer'],
            unit_data['interest_pp_num']
        ))

        # 提交事务并关闭连接
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('index'))

    return render_template('add_unit.html')


if __name__ == '__main__':
    app.run(debug=True)

