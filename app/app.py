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

