import os
import smtplib
import pyotp
from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
from firebase_admin import auth, credentials, firestore, initialize_app
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK
cred = credentials.Certificate({

})
initialize_app(cred)
db = firestore.client()


key = Fernet.generate_key()
cipher_suite = Fernet(key)

otp_dict = {}  # Temporary storage for OTPs

def send_email(to_email, subject, body):
    from_email = "vacantassignment@gmail.com"
    from_password = "anjf vofb cpyc qkfx"
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

@app.route('/createApiKey', methods=['POST'])
def createApiKey():
    uid = request.form['uid']
    pin = request.form['pin']

    if not pin:
        return jsonify({"msg": "PIN is required"}), 400

    user_record = auth.get_user(uid)
    
    user_ref = db.collection('users').document(uid)
    user_doc = user_ref.get()
    if user_doc.exists:
        return jsonify({"msg": "API key already generated"}), 400

    api_key = os.urandom(24).hex()
    api_secret = os.urandom(24).hex()
    encrypted_api_key = cipher_suite.encrypt(api_key.encode()).decode()
    encrypted_api_secret = cipher_suite.encrypt(api_secret.encode()).decode()
    
    user_ref.set({
        "api_key": encrypted_api_key,
        "api_secret": encrypted_api_secret,
        "pin": pin
    })
    return jsonify({"apiKey": api_key, "apiSecret": api_secret}), 200


@app.route('/register', methods=['POST'])
def register():
    uid = request.form['uid']
   

 

    user_record = auth.get_user(uid)
    
    user_ref = db.collection('users').document(uid)
    user_doc = user_ref.get()
    if user_doc.exists:
        return jsonify({"msg": "API key already generated"}), 400

    
    return jsonify({"msg": "Account created"}), 200


@app.route('/request-otp', methods=['POST'])
def request_otp():
    id_token = request.form['id_token']
    pin = request.form['pin']

    if not pin:
        return jsonify({"msg": "PIN is required"}), 400

    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token['uid']
    
    user_ref = db.collection('users').document(uid)
    user_doc = user_ref.get()
    if not user_doc.exists:
        return jsonify({"msg": "User not found"}), 404

    user = user_doc.to_dict()
    if user['pin'] != pin:
        return jsonify({"msg": "Incorrect PIN"}), 403
    
    # Generate OTP
    totp = pyotp.TOTP(pyotp.random_base32())
    otp = totp.now()

    # Store OTP in Firestore
    otp_ref = db.collection('otps').document(uid)
    otp_ref.set({
        "otp": otp
    })

    # Send OTP to user's email
    user_record = auth.get_user(uid)
    email = user_record.email
    send_email(email, "Your OTP Code", f"Your OTP code is: {otp}")
    
    return jsonify({"msg": "OTP sent to your email"}), 200

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    id_token = request.form['id_token']
    otp = request.form['otp']

    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token['uid']
    
    otp_ref = db.collection('otps').document(uid)
    otp_doc = otp_ref.get()
    if not otp_doc.exists:
        return jsonify({"msg": "OTP not found or expired"}), 403

    stored_otp = otp_doc.to_dict().get('otp')
    if stored_otp != otp:
        return jsonify({"msg": "Invalid OTP"}), 403
    
    user_ref = db.collection('users').document(uid)
    user_doc = user_ref.get()
    if not user_doc.exists:
        return jsonify({"msg": "User not found"}), 404

    user = user_doc.to_dict()
    decrypted_api_key = cipher_suite.decrypt(user['api_key'].encode()).decode()
    decrypted_api_secret = cipher_suite.decrypt(user['api_secret'].encode()).decode()
    
    # Delete OTP after successful verification
    otp_ref.delete()

    return jsonify({"apiKey": decrypted_api_key, "apiSecret": decrypted_api_secret}), 200



if __name__ == '__main__':
    app.run(debug=True)