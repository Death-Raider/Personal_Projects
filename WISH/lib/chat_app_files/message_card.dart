import 'package:chat_appication/api/apis.dart';
import 'package:chat_appication/helper/my_date_util.dart';
import 'package:chat_appication/models/message.dart';
import 'package:flutter/material.dart';
import '../main.dart';
class MessageCard extends StatefulWidget {
  const MessageCard({super.key, required this.message});
  final Message message;
  @override
  State<MessageCard> createState() => _MessageCardState();
}

class _MessageCardState extends State<MessageCard> {
  @override
  Widget build(BuildContext context) {
    return Apis.user.uid == widget.message.fromid ? _greenmessage():_bluemessage();
  }
  Widget _bluemessage(){

    if(widget.message.read.isEmpty){
      Apis.updateMessageReadStatus(widget.message);
      print("message read updated");
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Flexible(
          child: Container(
            padding: EdgeInsets.all(mq.width*.04),
            margin: EdgeInsets.symmetric(horizontal: mq.width*.04,vertical: mq.height *0.02),
            decoration: BoxDecoration(color: Color.fromARGB(255,221,245,255),border: Border.all(color: Colors.lightBlue),borderRadius: BorderRadius.only(topLeft: Radius.circular(30),topRight: Radius.circular(30),bottomRight: Radius.circular(30))),
            child: Text(
              widget.message.msg,
              style: TextStyle(fontSize: 15,color: Colors.black87),
            ),
          ),
        ),
    Padding(
      padding: EdgeInsets.only(right: mq.width*.04),
      child: Text(
        MyDateUtil.getFormattedTime(context: context, time: widget.message.sent),
        style: TextStyle(fontSize: 13,color: Colors.black54),
      ),
    ),


      ],
    );
  }
  Widget _greenmessage(){
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [

        Row(
          children: [
            SizedBox(width: mq.width*.04,),
            if(widget.message.read.isNotEmpty)
              Icon(Icons.done_all_rounded,color: Colors.blue,size: 20,),
            SizedBox(width: 2,),
            Text(
              MyDateUtil.getFormattedTime(context: context, time: widget.message.sent),
              style: TextStyle(fontSize: 13,color: Colors.black54),),
          ],
        ),
        Flexible(
          child: Container(
            padding: EdgeInsets.all(mq.width*.04),
            margin: EdgeInsets.symmetric(horizontal: mq.width*.04,vertical: mq.height *0.02),
            decoration: BoxDecoration(color: Color.fromARGB(255,218,255,176),border: Border.all(color: Colors.lightGreen),borderRadius: BorderRadius.only(topLeft: Radius.circular(30),topRight: Radius.circular(30),bottomLeft: Radius.circular(30))),
            child: Text(
              widget.message.msg,
              style: TextStyle(fontSize: 15,color: Colors.black87),

            ),
          ),
        ),


      ],
    );
  }
}
