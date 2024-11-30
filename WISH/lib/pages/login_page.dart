import 'package:wish/utils/routes.dart';
import 'package:wish/pages/home_page.dart';
import 'package:wish/helpers/login_validator.dart';
import 'package:wish/classes/user.dart';
import 'package:flutter/material.dart';

User initUser(){
  final User user = User();
  user.setTestData();
  return user;
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  String name="";
  String passwd="";
  final _formKey = GlobalKey<FormState>();

  // Creating method
  moveToHome(BuildContext context) async{
    if(_formKey.currentState!.validate()){
      if (validate(this.name,this.passwd)) {
        this.passwd = "";
        User user = initUser();
        await Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => HomePage(userData: user),
            )
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      child: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              SizedBox(height: 30,),
              Image.asset("assets/images/wish-logo.png",
                fit: BoxFit.cover,
              ),
              // Text("Welcome"),
              Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16.0, horizontal: 32.0),
                  child: Column(children: [
                    TextFormField(
                      decoration: InputDecoration(
                        hintText: "Enter Username",
                        labelText: "Username",
                      ),
                      validator: (value){
                        if(value!.isEmpty){
                          return "Username cannot be empty";
                        }
                        return null;
                      },
                      onChanged: (value){
                        name = value;
                      },
                    ),
                    TextFormField(
                      // for password to not visible
                      obscureText: true,
                      decoration: InputDecoration(
                        hintText: "Enter Password",
                        labelText: "Password",
                      ),
                      validator: (value){
                        if(value!.isEmpty){
                          return "Password cannot be empty";
                        }
                        else if(value.length<6){
                          return "Password length should be atleast 6";
                        }
                        return null;
                      },
                      onChanged: (value){
                        passwd = value;
                      },
                    ),
                    SizedBox(
                      height: 40,
                    ),

                    ElevatedButton(
                        onPressed: () => moveToHome(context),
                        child: Text("Login")
                    )
                  ],)
              )
            ],
          ),
        ),
      )

    );
  }
}
