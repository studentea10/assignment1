import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:assignment/ApiKeyScreen.dart';
import 'package:assignment/Login.dart';
import 'package:assignment/RegisterScreen.dart';
import 'package:assignment/firebase_options.dart';
import 'package:firebase_auth/firebase_auth.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
    runApp(MyApp());
  } catch (e) {
    print("Firebase Initialization Error: $e");
  }
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      initialRoute: '/',
      routes: {
        '/': (context) => AuthCheck(),
        '/login': (context) => LoginScreen(),
        '/register': (context) => RegisterScreen(),
        '/apikey': (context) => ApiKeyScreen(),
      },
    );
  }
}

class AuthCheck extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body:  Center(
              child: CircularProgressIndicator(),
            ),
          );
        } else if (snapshot.hasData) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            Navigator.pushReplacementNamed(context, '/apikey'); // Redirect to ApiKeyScreen if the user is authenticated
          });
          return Scaffold(); // Returning a Scaffold while waiting for navigation to complete
        } else {
          // Use WidgetsBinding to perform navigation after build is complete
          WidgetsBinding.instance.addPostFrameCallback((_) {
            Navigator.pushReplacementNamed(context, '/login'); // Redirect to LoginScreen if the user is not authenticated
          });
          return Scaffold(); // Returning a Scaffold while waiting for navigation to complete
        }
      },
    );
  }
}
