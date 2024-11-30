import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';

class DataTile extends StatelessWidget {
  final Map<String, dynamic> data;

  const DataTile({Key? key, required this.data}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(8.0),
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(8.0),
          color: Theme.of(context).appBarTheme.backgroundColor
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.pink,
            ),
            padding: const EdgeInsets.all(8.0),
            child: CupertinoButton(
              padding: EdgeInsets.zero,
              onPressed: () {
                // Add your logic when the file icon is pressed
              },
              child: Icon(
                CupertinoIcons.doc,
                size: 32.0,
                color: Colors.white,
              ),
            ),
          ),
          SizedBox(width: 16.0),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  data['title'],
                  style: const TextStyle(
                    fontSize: 18.0,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8.0),
                Text(
                  data['link'],
                  style: const TextStyle(
                    fontSize: 16.0,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
