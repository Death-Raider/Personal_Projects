class ChatUser {
  ChatUser({
    required this.pushNotification,
    required this.image,
    required this.about,
    required this.createdAt,
    required this.id,
    required this.lastActive,
    required this.isOnline,
    required this.email,
    required this.Name,
  });
  late  String pushNotification;
  late  String image;
  late  String about;
  late  String createdAt;
  late  String id;
  late  String lastActive;
  late  bool isOnline;
  late  String email;
  late  String Name;

  ChatUser.fromJson(Map<String, dynamic> json){
    pushNotification = json['push_notification'] ?? '';
    image = json['image'] ?? '';
    about = json['about'] ?? '';
    createdAt = json['created_at'] ?? '';
    id = json['id'] ?? '';
    lastActive = json['last_active'] ?? '';
    isOnline = json['is_online'] ?? '';
    email = json['email'] ?? '';
    Name = json['Name'] ?? '';
  }

  Map<String, dynamic> toJson() {
    final data = <String, dynamic>{};
    data['push_notification'] = pushNotification;
    data['image'] = image;
    data['about'] = about;
    data['created_at'] = createdAt;
    data['id'] = id;
    data['last_active'] = lastActive;
    data['is_online'] = isOnline;
    data['email'] = email;
    data['Name'] = Name;
    return data;
  }
}