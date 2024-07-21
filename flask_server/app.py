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
  "type": "service_account",
  "project_id": "faassignment-d7dae",
  "private_key_id": "e9361a8e60e9651d3f04eab158fdb7db8d5b5475",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDVzVfLCVxFMMuv\nQV/fjpIpqN0buUrAc2uNn61yynu5TPARapNn5+0zv1Ic7rRbw+yPyRj8ARd5cSCU\nLCY/QHOrZZhkSU5b5phF96CEfOhhIT+wg6p8DjY9Rn9tpCx4z4YtJGBF7rA8PGry\n1JQ24ESSBz6CQ3UcZYUMFRWiqQqFYjcCBFZuU71xzHFEyzrCpHgHsJYV3DShWbdz\nEw1aHryNM9SEUUJkogRkAohCIgma6t77R47pSlf7h5Udmtd+3mbezHs8NPps5IFv\nl0RmjQpen0iXzfHsPdHtwSXD8A0FDHfMicxcqzFLWk1mkyiyJN1ukj7iPu6V+x+I\nJDh6ohLnAgMBAAECggEADcCVFpbGDB9M4ruCRrd9eFeHzWo4QDPMZcIxHnKezbcA\ntCYWUDcvX0Y9qmXCTSrHkyIczMznLSUVMuK6HRRwvEQfLsg2VZv6DHoWpZ8BNYo1\ndg2qECu72mon9S37vFOg7lNqK+VkCaPbPz5kQDlhv8DeiPN823Q+QB41E47rAdRG\n2q0/fgmvgeXkrVYAcCHDSnItE0VcfYUqfuVI76C/j5k6pRvVlwrEcZfT0pr3MqQ+\niXFPT11hKYy5Z2P80IP6PMFNcCzOHNu2RC/qxHeADx220ySgOzDthVENY+PH4d6W\nMqqJd0EKCEsfy3QeaD85nLZvn62dfNiYjSoRklhh0QKBgQDtuE3/R/5lJntqJKjM\nA9cBavMjk7eiQy+tChLgH08mGY0mLSkq/6Nya40i2ergENV/rus+de+Aas7mrLBa\natcN4YaW4fCoh1PmbucgQzfhOeBqE7UP15EuckLC3xNMPNr32x/jWm9LRzgmdU5T\nDl/Ge8lS9uBbNYauFIagc8HKkQKBgQDmPjKznxxwlJdYuvsQZVZwzM73UwWGE9qL\n4QseNGxYo8K5AhPbV320p6Sl2AdxGeQ7dQ7PRV8+QtgkN3F5ndVxqUiNZB7VRb0c\nmlmLoEPKdgtMoAE8ss0VwhX7WxcBW33cicwJ/zJ/o3HKuMv+ZYPv0BNiZLCjzl4x\nRsKvOvQR9wKBgAc5uuUvgwQAD3BCfP72fuqEHa/PJZ3A/Qn9bGVzjixSSoAGj2HH\nM2ie7ENK7GCzIkonPu8/FnCIzpEkXpfg93hsinK7m10EAADZDh1k7aXi5HdU8gPx\nQXBv+KeDsEp47w7pkiaO8SMQnxxMJH1Ryod168Ch0F/1WIqiBRWLbzCBAoGBAL9X\ncUtVL41f72cN/RfjH7MegeGIXU7PsRAONe8kIeaIMYsO7vGaBB3eNDafEZAstD+1\nSFl4jW5wnq96ZBNt17Rduq3GRtl223Kp00D2L2BSOZG0Z1LKRSWP5jS9vqCiKDbf\nTXIBYzYv3qFaci04sCzb/0AF7cYz+pN4+tIlbDCBAoGAVEq46nP4Ls6H60jGSko5\n5UiwK9P28nEBp8dOAXj90CEGpR8tD21QK8Gu4BDx61oa1eQRfTXekPSTDFmg93ez\njfcqylW2vinYhfIo/C4mcWRGf0u/4aqt2HNbSNX5S9qnTXvUoTWzr7iUtacBxt5D\nQZgi1sxFBznkDMLAu1o69VU=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-trnoj@faassignment-d7dae.iam.gserviceaccount.com",
  "client_id": "106948745522940409174",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-trnoj%40faassignment-d7dae.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
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