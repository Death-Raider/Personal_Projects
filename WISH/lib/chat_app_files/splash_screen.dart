import 'package:chat_appication/api/apis.dart';
import 'package:chat_appication/pages/auth/login_page.dart';
import 'package:chat_appication/pages/home_screen.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../main.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  _SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  bool _isAnimate = false;
  late Size mq;

  @override
  void initState() {
    super.initState();
    Future.delayed(Duration(milliseconds: 1500), () {
      SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
      SystemChrome.setSystemUIOverlayStyle( const SystemUiOverlayStyle(systemNavigationBarColor: Colors.white,statusBarColor: Colors.white));
      if(Apis.auth.currentUser!=null){
        logMessage('\nUser: ${Apis.auth.currentUser}');
        Navigator.pushReplacement(
            context,MaterialPageRoute(builder: (_)=>home_screen())
        );
      }
      else{
        Navigator.pushReplacement(
            context,MaterialPageRoute(builder: (_)=>LoginPage())
        );
      }

    });
  }

  @override
  Widget build(BuildContext context) {
    mq = MediaQuery.of(context).size;
    return Scaffold(
      appBar: AppBar(
        title: Text("Welcome to Login Page"),
      ),
      body: Stack(
        children: [
          Positioned(
            right: mq.width * 0.25 ,
            width: mq.width * 0.5,
            top: mq.height * 0.15,
            child: Image.asset('assets/images/chat_icon.png'),
          ),
          Positioned(
            left: mq.width * 0.05,
            width: mq.width * 0.9,
            height: mq.height * 0.15,
            bottom: mq.height * 0.15,
            child: Text(
              "made in india",
              textAlign: TextAlign.center,
              style: TextStyle(
                  fontSize: 19,
                  fontWeight: FontWeight.bold,
                  letterSpacing: .5,
                  color: Colors.black87),
            )
          )
      ]),
    );
  }
}
