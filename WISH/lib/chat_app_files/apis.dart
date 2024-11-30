

import 'dart:io';

import 'package:wish/models/chat_user.dart';
import 'package:wish/models/message.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_storage/firebase_storage.dart';

class Apis{
  static FirebaseAuth auth = FirebaseAuth.instance;
  static FirebaseFirestore firestore =FirebaseFirestore.instance;
  static FirebaseStorage storage =FirebaseStorage.instance;
  static late ChatUser me;
  static User get user => auth.currentUser!;
  static Future<bool> userExsits() async{
    return (await firestore
        .collection('users')
        .doc(user.uid)
        .get())
        .exists;
  }
  static Future<void> getselfInfo() async{
    await firestore
        .collection('users')
        .doc(user.uid)
        .get()
        .then((user) async {
          if(user.exists){
            me=ChatUser.fromJson(user.data()!);
          }
          else{
            await createUser().then((value) => getselfInfo());
          }
    });
  }
  static Future<void> createUser() async{
    final time =DateTime.now().millisecondsSinceEpoch.toString();
    final chatUser = ChatUser(
      id: user.uid,
      Name: user.displayName.toString(),
      email: user.email.toString(),
      about: "hey i am using wechat ",
      createdAt: time,
      image: user.photoURL.toString(),
      isOnline: false,
      lastActive: time,
      pushNotification: '',
    );
    return await firestore
        .collection('users')
        .doc(user.uid)
        .set(chatUser.toJson());
  }
  static Stream<QuerySnapshot<Map<String, dynamic>>> getallusers(){
    return firestore.collection('users').where('id', isNotEqualTo:user.uid).snapshots();
  }
  static Future<void> updateUserInfo() async{
    await firestore.collection('users').doc(user.uid).update({
      'Name':me.Name,
      'about':me.about,
    });
  }
  static Future<void> updateProfilePicture(File file) async {
    final ext = file.path.split('.').last;
    final ref = storage.ref().child('profile.pictures/${user.uid}');
    await ref.putFile(file, SettableMetadata(contentType: 'image/$ext')).then((p0){
      print('Data Transferred:${p0.bytesTransferred/1000} kb');
    });
    me.image = await ref.getDownloadURL();
    await firestore.collection('users').doc(user.uid).update({
        'image':me.image,
    });
  }
  static String getConversationID(String id) => user.uid.hashCode<=id.hashCode
      ?'${user.uid}_$id'
      :'${id}_${user.uid}';
  static Stream<QuerySnapshot<Map<String, dynamic>>> getallmessages(ChatUser user){
    return firestore
        .collection('chats/${getConversationID(user.id)}/messages/')
        .snapshots();
  }
  static Future<void> sendMessage(ChatUser chatuser,String msg) async{
    final time=DateTime.now().millisecondsSinceEpoch.toString();
    final Message message=Message(msg: msg, read: '', told: chatuser.id, type: Type.text, sent: time, fromid: user.uid);
    final ref=firestore.collection('chats/${getConversationID(chatuser.id)}/messages/');
    await ref.doc(time).set(message.toJson());
  }
  static Future<void> updateMessageReadStatus(Message message) async {
    firestore.collection('chats/${getConversationID(message.fromid)}/messages/').doc(message.sent).update({'read':DateTime.now().millisecondsSinceEpoch.toString()});
  }
  static Stream<QuerySnapshot<Map<String, dynamic>>> getLastMessage(ChatUser user)
    {
      return firestore
          .collection('chats/${getConversationID(user.id)}/messages/')
          .limit(1)
          .snapshots();
    }
}