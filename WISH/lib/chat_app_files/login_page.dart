import 'dart:io';
import 'dart:developer';
// import 'dart:js_interop';
// import 'dart:math';
// import 'dart:ui';
import 'package:chat_appication/helper/dialog.dart';
import 'package:chat_appication/pages/home_screen.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_sign_in/google_sign_in.dart';

import '../api/apis.dart';
import '../main.dart';
void logMessage(String message) {
  print("Log: $message");
}
class LoginPage extends StatefulWidget {
  const LoginPage({Key? key}) : super(key: key);

  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  bool _isAnimate = false;
  late Size mq;

  @override
  void initState() {
    super.initState();
    Future.delayed(Duration(milliseconds: 500), () {
      setState(() {
        _isAnimate = true;
      });
    });
  }
  _handleGoogleBtnClick(){
    Dialogs.showProgressBar(context);
    _signInWithGoogle().then((user) async{
      Navigator.pop(context);
      if(user!=null){
        logMessage('\nUser: ${user.user}');
        logMessage('\nUserAdditionalInfo: ${user.additionalUserInfo}');
        if((await Apis.userExsits())){
          Navigator.pushReplacement(
            context, MaterialPageRoute(builder: (_) => home_screen()));
        }
        else{
          await Apis.createUser().then((value){
            Navigator.pushReplacement(
                context, MaterialPageRoute(builder: (_) => home_screen()));
          });
        }
      }
    });
  }
  Future<UserCredential?> _signInWithGoogle() async {
   try{
     await InternetAddress.lookup("google.com");
     // Trigger the authentication flow
     final GoogleSignInAccount? googleUser = await GoogleSignIn().signIn();

     // Obtain the auth details from the request
     final GoogleSignInAuthentication? googleAuth = await googleUser?.authentication;

     // Create a new credential
     final credential = GoogleAuthProvider.credential(
       accessToken: googleAuth?.accessToken,
       idToken: googleAuth?.idToken,
     );

     // Once signed in, return the UserCredential
     return await Apis.auth.signInWithCredential(credential);
   }catch(e){
     logMessage("\n_signInWithGoogle: $e ");
     Dialogs.showSnackBar(context, 'something went wrong (check internet!)');
     return null;
   }
  }
  // sign out function
  // _signOut() async{
  //   await FirebaseAuth.instance.signOut();
  //   await GoogleSignIn().signOut();
  // }
  @override
  Widget build(BuildContext context) {
    mq = MediaQuery.of(context).size;
    return Scaffold(
      appBar: AppBar(
        title: Text("Welcome to Login Page"),
      ),
      body: Stack(
        children: [
          AnimatedPositioned(
            right: _isAnimate ? mq.width * 0.425 : -mq.width * 0.15,
            width: mq.width * 0.15,
            top: mq.height * 0.15,
            duration: Duration(seconds: 1),
            child: Image.asset('assets/images/chat_icon.png'),
          ),
          Positioned(
            left: mq.width * 0.05,
            width: mq.width * 0.9,
            height: mq.height * 0.15,
            bottom: mq.height * 0.15,
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.greenAccent,
                shape: StadiumBorder(),
                elevation: 10,
                shadowColor: Colors.red,
              ),
              onPressed: () {
                _handleGoogleBtnClick();
              },
              icon: Image.asset("assets/images/chat_icon.png",height: mq.height * 0.14,),
              label: RichText(
                text: TextSpan(
                  style: TextStyle(
                    color: Colors.black87,
                    fontSize: 19,
                    fontWeight: FontWeight.bold,
                  ),
                  children: [
                    TextSpan(text: 'Sign in with '),
                    TextSpan(text: 'Google'),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
