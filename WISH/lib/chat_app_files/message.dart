class Message {
  Message({
    required this.msg,
    required this.read,
    required this.told,
    required this.type,
    required this.sent,
    required this.fromid,
  });
  late final String msg;
  late final String read;
  late final String told;
  late final Type type;
  late final String sent;
  late final String fromid;

  Message.fromJson(Map<String, dynamic> json){
    msg = json['msg'].toString();
    read = json['read'].toString();
    told = json['told'].toString();
    type = json['type'].toString() == Type.image.name?Type.image:Type.text;
    sent = json['sent'].toString();
    fromid = json['fromid'];
  }

  Map<String, dynamic> toJson() {
    final data = <String, dynamic>{};
    data['msg'] = msg;
    data['read'] = read;
    data['told'] = told;
    data['type'] = type.name;
    data['sent'] = sent;
    data['fromid'] = fromid;
    return data;
  }
}
enum Type{text,image}