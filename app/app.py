from flask import Flask, request,render_template, jsonify
import mysql.connector
import qrcode.constants
from mysql.connector import Error
import pytz
import qrcode
import io
from datetime import datetime
#import uuid
import base64
import json


app = Flask(__name__)

def get_db_connection():

    try:
        connection = mysql.connector.connect(
        host='db',
        user= 'root',
        password='brey',
        database='qr_user_db'
    )
        return connection
    except Error as e:
        print(f"Error connecting to MYSQL: {e}")
        return None



@app.route('/api/product', methods=['POST'])
def create_product():
    data = request.get_json()
    name = data['name']
    price = data['price']
    description = data['description']

    connection = get_db_connection()
    cursor = connection.cursor()

    query = "INSERT INTO product (name, price, description) VALUES (%s, %s, %s)"
    cursor.execute(query,(name, price, description))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({'menssage': 'muy bien'}), 201



@app.route('/api/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data['username']
    email = data['email']
   

    connection = get_db_connection()
    cursor = connection.cursor()

    query = "INSERT INTO user (username, email) VALUES (%s, %s)"
    cursor.execute(query,(username,email))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({'menssage': 'muy bien'}), 201



@app.route('/generate-qr', methods=['GET'])
def generate_qr():

 
    connection = get_db_connection()
    cursor = connection.cursor()

    query = "SELECT id FROM user ORDER BY id DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result is None:
        return jsonify({'error':'No users found'}), 400

    user_id = result[0]
    product_id = result[0]

    qr_data = f"http://localhost:5009/scan_qr?user_id={user_id}&product_id={product_id}"
    qr = qrcode.QRCode(
         version = 1,
         error_correction = qrcode.constants.ERROR_CORRECT_L,
         box_size = 20,
         border = 4, 
    )

    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    image_io = io.BytesIO()
    img.save(image_io, 'PNG')
    img_str = base64.b64encode(image_io.getvalue()).decode()

    return render_template('qr_view.html', qr_code=img_str)




@app.route('/scan_qr', methods=['GET'])
def scan_qr():
    
    user_id = int(request.args.get('user_id'))

    product_id = request.args.get('product_id')
  

    if user_id is None:
        return jsonify({'error': 'User name is required'}),400
    
    if product_id is None:
        return jsonify({'error': 'User name is required'}),400
    

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT id FROM user WHERE id = %s', (user_id,))
        result = cursor.fetchone()

        if result is None:
            return jsonify({'error': 'No user found'}), 400

        user_id = result[0]

        cursor.execute('SELECT id FROM product WHERE id = %s', (product_id,))
        result = cursor.fetchone()

        if result is None:
            return jsonify({'error': 'No user found'}), 400

        product_id = result[0]

        #query2 = 'SELECT id FROM product WHERE id = %s', (product_id)

        #cursor.execute(query2, (product_id))
        #result2 = cursor.fetchone()
        
        #product_id = result2
       
        query = "INSERT INTO carrito (user_id,product_id) VALUES (%s , %s)"
        cursor.execute(query,(user_id,product_id))
        connection.commit()

        response = {'message': 'Scan registered successfully'}
    
    except Error as e:
        response = {f'error':str(e)}

    finally:
        cursor.close()
        connection.close()

    return jsonify(response)



@app.route('/user_scan',  methods=['GET'])
def user_scan():
    connection = get_db_connection()
    cursor = connection.cursor()

    query = "SELECT user.username, carrito.timestamp FROM carrito JOIN user ON carrito.user_id = user.id ORDER BY carrito.timestamp  ASC "
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    return jsonify(results)
    



 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)