import 'dart:convert';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:wish/chat_app_files/chat_user.dart';
import 'package:wish/chat_app_files/login_page.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

import 'message_card.dart';
import '../api/apis.dart';
import '../main.dart';
import '../models/message.dart';

class ChatScreen extends  StatefulWidget {
  final ChatUser user;

  const ChatScreen({super.key,required this.user});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  List<Message> _list=[];
  final  _textController = TextEditingController();
  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Scaffold(
        appBar: AppBar(
          automaticallyImplyLeading: false,
          flexibleSpace: _appBar(),
          backgroundColor: Colors.white,
        ),
        backgroundColor: Color.fromARGB(255, 234, 248, 255),
        body: Column(children: [
          Expanded(
            child: StreamBuilder(
              stream: Apis.getallmessages(widget.user),
              builder: (context,Snapshot){
                switch(Snapshot.connectionState){
                  case ConnectionState.waiting:
                  case ConnectionState.none:
                    return const SizedBox();
                  case ConnectionState.active:
                  case ConnectionState.done:
                    final data = Snapshot.data?.docs;
                    // logMessage('Data:${jsonEncode(data![0].data())}');
                    _list=data?.map((e) => Message.fromJson(e.data())).toList() ?? [];
                    final newList=data?.map((e) => Message.fromJson(e.data())).toList() ?? [];
                    // _list.clear();
                    // _list.add(Message(msg: 'hi', read: '', told: 'xyz', type: Type.text, sent: '12:00 AM', fromid: Apis.user.uid));
                    // _list.add(Message(msg: 'hello', read: '', told: Apis.user.uid, type: Type.text, sent: '12:05 AM', fromid: 'xyz'));


                    if(_list.isNotEmpty){
                      return ListView.builder(
                          itemCount:_list.length,
                          padding: EdgeInsets.only(top:mq.height * .01),
                          physics: const BouncingScrollPhysics(),
                          itemBuilder: (context,index){
                            return MessageCard(message:_list[index]);
                            // return Text("message: ${_list[index]}");
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
            ),
          ),
          _chatInput()
        ],),
      ),
    );
  }
  Widget _appBar(){
    return InkWell(
      onTap: (){} ,
      child: Row(children: [
        IconButton(onPressed: (){
          Navigator.pop(context);
        },
          icon: Icon(Icons.arrow_back, color: Colors.black54,),),
        ClipRRect(
          borderRadius: BorderRadius.circular(mq.height*.3),
          child: CachedNetworkImage(
            width: mq.height*.05,
            height: mq.height*.05,
            imageUrl: widget.user.image,
            // imageUrl: "http:/via.placeholder.com/350X150",
            placeholder: (context, url) => CircularProgressIndicator(),
            errorWidget: (context, url, error) => const CircleAvatar(child: Icon(CupertinoIcons.person)),
          ),
        ),
        SizedBox(width: 10,),
        Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.user.Name,style: TextStyle(fontSize: 18,color: Colors.black87,fontWeight: FontWeight.w500),),
            const SizedBox(height: 2,),
            Text("last seen not available",style: TextStyle(fontSize: 12,color: Colors.black54,fontWeight: FontWeight.w300),),
          ],)
      ],),
    );
  }
  Widget _chatInput(){
    return Padding(
      padding: EdgeInsets.symmetric(vertical: mq.height*.06,horizontal: mq.width*.025),
      child: Row(
        children: [
          Expanded(
            child: Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
              child: Row(children: [
                IconButton(onPressed: (){
                },
                  icon: Icon(Icons.keyboard, color: Colors.blueAccent,size: 26,),),
                 Expanded(child: TextField(
                  controller: _textController,
                  keyboardType: TextInputType.multiline,
                  maxLines: null,
                  decoration: InputDecoration(
                      hintText: "type something....",
                      hintStyle: TextStyle(color: Colors.blueAccent),
                      border: InputBorder.none,
                  ),
                )),
                IconButton(onPressed: (){
                },
                  icon: Icon(Icons.image, color: Colors.blueAccent,size: 26,),),
                IconButton(onPressed: (){
                },
                  icon: Icon(Icons.camera_alt_rounded, color: Colors.blueAccent,size: 26,),),
                SizedBox(width: mq.width*.02,),
              ],),
            ),
          ),

          MaterialButton(
            onPressed: (){
              if(_textController.text.isNotEmpty){
                Apis.sendMessage(widget.user, _textController.text);
                _textController.text='';
              }
            },
            minWidth: 0,
            padding: EdgeInsets.only(top: 10,bottom: 10,right: 5,left: 10),
            shape: CircleBorder(),
            color: Colors.lightGreen,
            child: Icon(
              Icons.send,
              color: Colors.white,
              size: 28,),)
        ],
      ),
    );
  }
}
