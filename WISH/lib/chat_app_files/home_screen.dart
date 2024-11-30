import 'dart:convert';

import 'package:chat_appication/Widgets/chat_user_card.dart';
import 'package:chat_appication/pages/auth/login_page.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';

import '../api/apis.dart';
import '../main.dart';
import '../models/chat_user.dart';
import '../pages/auth/profile_screen.dart';
class home_screen extends StatefulWidget {
  const home_screen({super.key});

  @override
  State<home_screen> createState() => _home_screenState();
}

class _home_screenState extends State<home_screen> {
  List<ChatUser> list = [];
  final List<ChatUser> _searchlist = [];
  bool _isSearching = false;
  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    Apis.getselfInfo();
  }
  @override
  Widget build(BuildContext context) {
    Color blueColor = Color(0xFF585FFF);
    mq=MediaQuery.of(context).size;
    return GestureDetector(
      onTap: ()=>FocusScope.of(context).unfocus(),
      child: WillPopScope(
        onWillPop: (){
          if(_isSearching){
            setState(() {
              _isSearching = !_isSearching;
            });
            return Future.value(false);
          }
          else{
            return Future.value(true);
          }

        },
        child: Scaffold(
            appBar: AppBar(
              // leading: Icon(CupertinoIcons.home),
              leading: Icon(Icons.home),
              iconTheme: IconThemeData(
                color: Colors.black87,
              ),
              title: _isSearching ? TextField(
                decoration: const InputDecoration(
                  border: InputBorder.none,hintText: 'Name'),
                autofocus: true,
                style: const TextStyle(fontSize: 17,letterSpacing: 0.5,),
                onChanged: (val){
                  _searchlist.clear();
                  for(var i in list){
                      if(i.Name.toLowerCase().contains(val.toLowerCase()) || i.email.toLowerCase().contains(val.toLowerCase())){
                        _searchlist.add(i);
                        setState(() {
                          _searchlist;
                        });
                      }
                  }
                },
              ) : Text(
                  "WISH",
                  style: TextStyle(
                    color: blueColor, // Change the color to red
                    fontSize: 30, // Set the font size
                    fontWeight: FontWeight.bold, // Set the font weight to bold
                  ),
                ),
              actions: [
                IconButton(onPressed: (){
                  setState(() {
                    _isSearching= !_isSearching;
                  });
                }, icon: Icon(_isSearching
                    ? CupertinoIcons.clear_circled_solid
                    : Icons.search)),
                IconButton(onPressed: (){
                  Navigator.push(context, MaterialPageRoute(builder: (_)=>ProfileScreen(user: Apis.me,)));
                }, icon: Icon(Icons.more_vert)),
                // IconButton(onPressed: (){}, icon: Icon(Icons.home)),
              ],
            ),
            backgroundColor: Colors.pink[50],
            floatingActionButton: Padding(
              padding: const EdgeInsets.only(bottom: 20,right: 10),
              child: FloatingActionButton(onPressed: () async{
                await Apis.auth.signOut();
                await GoogleSignIn().signOut();
              },child: Icon(Icons.add_comment_rounded)),
            ),
            body: StreamBuilder(
              stream: Apis.getallusers(),
              builder: (context,Snapshot){
                switch(Snapshot.connectionState){
                  case ConnectionState.waiting:
                  case ConnectionState.none:
                    return const Center(child: CircularProgressIndicator(),);
                  case ConnectionState.active:
                  case ConnectionState.done:
                    final data = Snapshot.data?.docs;
                    list=data?.map((e) => ChatUser.fromJson(e.data())).toList() ?? [];
                    if(list.isNotEmpty){
                      return ListView.builder(
                          itemCount:_isSearching ? _searchlist.length: list.length,
                          padding: EdgeInsets.only(top:mq.height * .01),
                          physics: const BouncingScrollPhysics(),
                          itemBuilder: (context,index){
                            return ChatUserCard(user: _isSearching?_searchlist[index]:list[index],);
                            // return Text("Name: ${list[index]}");
                          });
                    }
                    else{
                      return const Center(child:
                      Text("No Connection Found!",
                        style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.black54,
                        ),
                      ));
                    }
              }
        
        
              },
            )
        ),
      ),
    );
  }
}
