import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/services.dart'; // Import this for Clipboard functionality
import 'dart:convert';

class ApiKeyScreen extends StatefulWidget {
  @override
  _ApiKeyScreenState createState() => _ApiKeyScreenState();
}

class _ApiKeyScreenState extends State<ApiKeyScreen> {
  final TextEditingController _apiKeyController = TextEditingController();
  final TextEditingController _pinController = TextEditingController();
  final TextEditingController _otpController = TextEditingController();
  final FirebaseAuth _auth = FirebaseAuth.instance;
  bool _showPinField = false;
  bool _showOtpField = false;
  String _selectedAction = '';

  Future<void> _generateAndStoreApiKey() async {
    if (_pinController.text.isEmpty) {
      _showErrorDialog('PIN is required to generate API key');
      return;
    }
    try {
      String? uid = _auth.currentUser?.uid;
      if (uid != null) {
        final response = await http.post(
          Uri.parse('http://127.0.0.1:5000/createApiKey'),
          body: {
            'uid': uid,
            'pin': _pinController.text,
          },
        );

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          setState(() {
            _apiKeyController.text = data['apiKey'];
          });
          _showApiKeyDialog(data['apiKey']);
        } else {
          final data = json.decode(response.body);
          _showErrorDialog('Error: ${data["msg"]}');
        }
      }
    } catch (e) {
      _showErrorDialog('Error: $e');
    }
  }

  Future<void> _requestOtp() async {
    if (_pinController.text.isEmpty) {
      _showErrorDialog('PIN is required to retrieve API key');
      return;
    }
    try {
      String? idToken = await _auth.currentUser?.getIdToken();
      if (idToken != null) {
        final response = await http.post(
          Uri.parse('http://127.0.0.1:5000/request-otp'),
          body: {
            'id_token': idToken,
            'pin': _pinController.text,
          },
        );

        if (response.statusCode == 200) {
          setState(() {
            _showOtpField = true;
          });
          _showSuccessDialog('OTP sent to your email');
        } else {
          final data = json.decode(response.body);
          _showErrorDialog('Error: ${data["msg"]}');
        }
      }
    } catch (e) {
      _showErrorDialog('Error: $e');
    }
  }

  Future<void> _verifyOtpAndRetrieveApiKey() async {
    if (_otpController.text.isEmpty) {
      _showErrorDialog('OTP is required to retrieve API key');
      return;
    }
    try {
      String? idToken = await _auth.currentUser?.getIdToken();
      if (idToken != null) {
        final response = await http.post(
          Uri.parse('http://127.0.0.1:5000/verify-otp'),
          body: {
            'id_token': idToken,
            'otp': _otpController.text,
          },
        );

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          setState(() {
            _apiKeyController.text = data['apiKey'];
          });
          _showApiKeyDialog(data['apiKey']);
        } else {
          final data = json.decode(response.body);
          _showErrorDialog('Error: ${data["msg"]}');
        }
      }
    } catch (e) {
      _showErrorDialog('Error: $e');
    }
  }

  void _showApiKeyDialog(String apiKey) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('Your API Key'),
          content: SelectableText(apiKey),
          actions: [
            TextButton(
              onPressed: () {
                Clipboard.setData(ClipboardData(text: apiKey));
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('API Key copied to clipboard')),
                );
              },
              child: Text('Copy'),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: Text('OK'),
            ),
          ],
        );
      },
    );
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('Error'),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: Text('OK'),
            ),
          ],
        );
      },
    );
  }

  void _showSuccessDialog(String message) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('Success'),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: Text('OK'),
            ),
          ],
        );
      },
    );
  }

  void _showPinFieldAndSetAction(String action) {
    setState(() {
      _showPinField = true;
      _selectedAction = action;
    });
  }

  void _performSelectedAction() {
    if (_selectedAction == 'generate') {
      _generateAndStoreApiKey();
    } else if (_selectedAction == 'retrieve') {
      _requestOtp();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text('API Key'),
        elevation: 0,
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'Manage Your API Key',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    ElevatedButton(
                      onPressed: () => _showPinFieldAndSetAction('generate'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _selectedAction == 'generate' ? Colors.grey : Colors.white,
                        padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15),
                        textStyle: TextStyle(fontSize: 18),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(30.0),
                        ),
                      ),
                      child: Text('Generate API Key'),
                    ),
                    SizedBox(width: 10),
                    ElevatedButton(
                      onPressed: () => _showPinFieldAndSetAction('retrieve'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _selectedAction == 'retrieve' ? Colors.grey : Colors.white,
                        padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15),
                        textStyle: TextStyle(fontSize: 18),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(30.0),
                        ),
                      ),
                      child: Text('Retrieve API Key'),
                    ),
                  ],
                ),
                SizedBox(height: 20),
                Visibility(
                  visible: _showPinField,
                  child: Column(
                    children: [
                      TextField(
                        controller: _pinController,
                        decoration: InputDecoration(
                          labelText: 'Enter PIN',
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.lock),
                          filled: true,
                          fillColor: Colors.white,
                        ),
                        obscureText: true,
                      ),
                      SizedBox(height: 10),
                      ElevatedButton(
                        onPressed: _performSelectedAction,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue,
                          padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15),
                          textStyle: TextStyle(fontSize: 18),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(30.0),
                          ),
                        ),
                        child: Text('Submit PIN'),
                      ),
                      Visibility(
                        visible: _showOtpField,
                        child: Column(
                          children: [
                            TextField(
                              controller: _otpController,
                              decoration: InputDecoration(
                                labelText: 'Enter OTP',
                                border: OutlineInputBorder(),
                                prefixIcon: Icon(Icons.lock),
                                filled: true,
                                fillColor: Colors.white,
                              ),
                            ),
                            SizedBox(height: 10),
                            ElevatedButton(
                              onPressed: _verifyOtpAndRetrieveApiKey,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.blue,
                                padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15),
                                textStyle: TextStyle(fontSize: 18),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(30.0),
                                ),
                              ),
                              child: Text('Submit OTP'),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
