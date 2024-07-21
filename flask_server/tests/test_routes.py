import unittest
from flask_testing import TestCase
from unittest.mock import MagicMock, patch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from app import app, db, auth, cipher_suite, send_email

class TestRegisterEndpoint(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    @patch('app.db')
    @patch('app.auth')
    @patch('app.cipher_suite')
    @patch('app.os')
    def test_register_success(self, mock_os, mock_cipher, mock_auth, mock_db):
        mock_os.urandom.return_value.hex.return_value = "fake_key"
        mock_cipher.encrypt.return_value.decode.return_value = "encrypted_key"
        mock_db.collection.return_value.document.return_value.get.return_value.exists = False

        response = self.client.post('/register', data={'uid': 'BSXa34Ly8VM5QkCk3kcraLU3ivX2', 'pin': '1234'})
        self.assertEqual(response.status_code, 200)



    @patch('app.db')
    def test_register_user_exists(self, mock_db):
        mock_db.collection.return_value.document.return_value.get.return_value.exists = True
        response = self.client.post('/register', data={'uid': 'BSXa34Ly8VM5QkCk3kcraLU3ivX2', 'pin': '1234'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('API key already generated', response.json['msg'])

class TestRequestOTPEndpoint(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    @patch('app.db')
    @patch('app.auth')
    @patch('app.send_email')
    @patch('app.pyotp.TOTP')
    def test_request_otp_success(self, mock_totp, mock_email, mock_auth, mock_db):
        mock_totp_instance = MagicMock()
        mock_totp_instance.now.return_value = "123456"
        mock_totp.return_value = mock_totp_instance
        mock_db.collection.return_value.document.return_value.get.return_value.exists = True
        mock_db.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {'pin': '4567'}

        response = self.client.post('/request-otp', data={'id_token': 'token123', 'pin': '4567'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('OTP sent to your email', response.json['msg'])
    
    @patch('app.db')
    @patch('app.auth')
    @patch('app.send_email')
    def test_request_otp_incorrect_pin(self, mock_email, mock_auth, mock_db):
        # Setup mock for database retrieval
        mock_db.collection.return_value.document.return_value.get.return_value.exists = True
        mock_db.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {'pin': '1234'}  # Actual pin in the system

        response = self.client.post('/request-otp', data={'id_token': 'token123', 'pin': '4567'})  # Incorrect pin provided
        self.assertEqual(response.status_code, 403)
        self.assertIn('Incorrect PIN', response.json['msg'])

class TestVerifyOTPEndpoint(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    @patch('app.db')
    @patch('app.auth')
    def test_verify_otp_invalid(self, mock_auth, mock_db):
        # Setup mock database and authentication responses
        mock_auth.verify_id_token.return_value = {'uid': 'BSXa34Ly8VM5QkCk3kcraLU3ivX2'}
        mock_db.collection.return_value.document.return_value.get.return_value.exists = True
        mock_db.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {'otp': 'correct_otp'}
        
        # Perform a POST request to the endpoint with the wrong OTP
        response = self.client.post('/verify-otp', data={'id_token': 'valid_token', 'otp': 'wrong_otp'})
        
        # Check if the response indicates an invalid OTP
        self.assertEqual(response.status_code, 403)
        self.assertIn('Invalid OTP', response.json['msg'])



if __name__ == "__main__":
    unittest.main()
