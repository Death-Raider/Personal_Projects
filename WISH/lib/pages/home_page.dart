import 'package:flutter/cupertino.dart';
import 'package:wish/Widgets/drawer.dart';
import 'package:wish/Widgets/papers.dart';
import 'package:wish/classes/user.dart';
import 'package:flutter/material.dart';

class HomePage extends StatelessWidget {
  final User userData;
  HomePage({super.key, required this.userData}){
    this.userData.displayUser();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).appBarTheme.backgroundColor,
        title: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          // mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            Padding(
              padding: EdgeInsets.fromLTRB(10, 0, 10, 0),
              child: Text("WISH"),
            ),
            Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10.0),
              ),
              height: 50,
              width: 50,
              child: Image(
                image: AssetImage("assets/images/logo.png"),
                fit: BoxFit.fill,
              ),
            )
          ],
        ),
      ),
      body: Column(
        children: [
          Container(
            padding: EdgeInsets.all(8.0),
            child: Row(
              children: [
                SizedBox(width: 8.0), // Add some spacing between logo and search bars
                Expanded(
                  child: CupertinoSearchTextField()
                )
              ]
            )
          ),
          Expanded(
            child: Papers(),
          ),
        ],
      ),
      drawer: MyDrawer(),
    );

  }
}
