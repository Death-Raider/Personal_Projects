import 'dart:convert';
import 'dart:io';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:chat_appication/Widgets/chat_user_card.dart';
import 'package:chat_appication/models/chat_user.dart';
import 'package:chat_appication/pages/auth/login_page.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:image_picker/image_picker.dart';

import '../../api/apis.dart';
import '../../helper/dialog.dart';
import '../../main.dart';
class ProfileScreen extends StatefulWidget {
  final ChatUser user;
  const ProfileScreen({super.key, required this.user});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _formkey = GlobalKey<FormState>();
  String? _image;

  @override
  Widget build(BuildContext context) {
    mq=MediaQuery.of(context).size;
    return GestureDetector(
      onTap: ()=>FocusScope.of(context).unfocus(),
      child: Scaffold(
          resizeToAvoidBottomInset: false,
          appBar: AppBar(
            title: Text("Profile Screen"),
          ),
          floatingActionButton: Padding(
            padding: const EdgeInsets.only(bottom: 20,right: 10),
            child: FloatingActionButton.extended(onPressed: () async{
              Dialogs.showProgressBar(context);
              await Apis.auth.signOut().then((value) async {
                await GoogleSignIn().signOut().then((value){
                  // for hiding progress dialog
                  Navigator.pop(context);
                  // for moving to home screen
                  Navigator.pop(context);
                  Navigator.pushReplacement(context,
                      MaterialPageRoute(builder: (_)=>LoginPage()));
                });
              });
      
            },icon: Icon(Icons.logout),label: Text('logout'),),
          ),
          body: Form(
            key: _formkey,
            child: Padding(
              padding: EdgeInsets.symmetric(horizontal: mq.width*.05),
              child: SingleChildScrollView(
                child: Column(children: [
                  SizedBox(width: mq.width,height: mq.height*.03,),
                  Stack(
                    children: [
                      _image != null
                          ?
                      ClipRRect(
                        borderRadius: BorderRadius.circular(mq.height*.1),
                        child: Image.file(File(_image!),
                          width: mq.height*.2,
                          height: mq.height*.2,
                          fit: BoxFit.cover,
                        ),
                      ):
                      ClipRRect(
                        borderRadius: BorderRadius.circular(mq.height*.1),
                        child: CachedNetworkImage(
                          width: mq.height*.2,
                          height: mq.height*.2,
                          fit: BoxFit.cover,
                          imageUrl: widget.user.image,
                          // imageUrl: "http:/via.placeholder.com/350X150",
                          placeholder: (context, url) => CircularProgressIndicator(),
                          errorWidget: (context, url, error) => const CircleAvatar(child: Icon(CupertinoIcons.person)),
                        ),
                      ),
                      Positioned(
                        bottom: 0,
                        right: 0,
                        child: MaterialButton(
                          elevation: 1,
                          onPressed: (){
                            _showBottomSheet();
                          },
                          shape: const CircleBorder(),
                          color: Colors.white,
                          child: const Icon(Icons.edit,color: Colors.deepPurpleAccent,),
                        ),
                      )
                    ],
                  ),
                  SizedBox(height: mq.height*.03,),
                  Text(widget.user.email,style: TextStyle(color: Colors.black54,fontSize: 16),),
                  SizedBox(height: mq.height*.05,),
                  TextFormField(
                    initialValue: widget.user.Name,
                    onSaved: (val)=>Apis.me.Name=val??'',
                    validator: (val)=> val!= null && val.isNotEmpty
                      ?null
                      : 'Required Field',
                    decoration: InputDecoration(
                      prefixIcon: Icon(Icons.person,color: Colors.deepPurple[300],),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      hintText: "eg: happy singh",
                      label:Text('Name'),
                    ),
                  ),
                      
                  SizedBox(height: mq.height*.02,),
                      
                  TextFormField(
                    initialValue: widget.user.about,
                    onSaved: (val)=>Apis.me.about=val??'',
                    validator: (val)=> val!= null && val.isNotEmpty
                        ?null
                        : 'Required Field',
                    decoration: InputDecoration(
                      prefixIcon: Icon(Icons.info_outline,color: Colors.deepPurple[300],),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      hintText: "eg: feeling happy",
                      label:Text('About'),
                    ),
                  ),
                  SizedBox(height: mq.height*.03,),
                  ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        shape: const StadiumBorder(),
                        minimumSize: Size(mq.width*.5, mq.height*.06),
                      ),
                      onPressed: (){
                        if(_formkey.currentState!.validate()){
                          _formkey.currentState!.save();
                          Apis.updateUserInfo().then((value){
                            Dialogs.showSnackBar(context, "Profile updated succesfully");
                          });
                          print('inside validator');
                        }
                      },
                      icon:const Icon(Icons.edit,size: 28,),
                      label: const Text('UPDATE',style: TextStyle(fontSize: 16),),
                  ),
                ],),
              ),
            ),
          )
      ),
    );
  }
  void _showBottomSheet(){
    showModalBottomSheet(
        context: context,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.only(topLeft: Radius.circular(20),topRight: Radius.circular(20))),
        builder: (_){
          return ListView(
            shrinkWrap: true,
            padding: EdgeInsets.only(top: mq.height*.03,bottom: mq.height*0.05),
            children: [
              Text("Pick Profile Picture",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 20,fontWeight: FontWeight.bold,),),
              SizedBox(height: mq.height * .02,),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    shape: const CircleBorder(),
                    fixedSize: Size(mq.width*.3, mq.height*.15),
                  ),
                    onPressed: () async {
                      final ImagePicker _picker= ImagePicker();
                      final XFile ? image = await _picker.pickImage(source: ImageSource.gallery,imageQuality: 80);
                      if(image != null){
                        print('Image Path: ${image.path} -- mime type:${image.mimeType}');
                        setState(() {
                          _image= image.path;

                        });
                        Apis.updateProfilePicture(File(_image!));

                        Navigator.pop(context);
                      }

                    }, child: Image.asset(
                'assets/images/gallery.png'
              )),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      shape: const CircleBorder(),
                      fixedSize: Size(mq.width*.3, mq.height*.15),
                    ),
                    onPressed: () async {
                      final ImagePicker _picker= ImagePicker();
                      final XFile ? image = await _picker.pickImage(source: ImageSource.camera,imageQuality: 80);
                      if(image != null){
                        print('Image Path: ${image.path} -- mime type:${image.mimeType}');
                        setState(() {
                          _image= image.path;

                        });
                        Apis.updateProfilePicture(File(_image!));

                        Navigator.pop(context);
                      }
                    }, child: Image.asset(
                    'assets/images/camera.png'
                )),
              ],)
            ],
          );
        });
  }
}
