import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'datatile.dart';

class Papers extends StatefulWidget {
  const Papers({Key? key}) : super(key: key);

  @override
  State<Papers> createState() => _PapersState();
}

class _PapersState extends State<Papers> {
  final String dataFilePath = 'assets/data/dummy.json';
  List<dynamic> data = [];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final String jsonString = await rootBundle.loadString(dataFilePath);
      final jsonData = jsonDecode(jsonString) as Map<String, dynamic>;
      setState(() {
        data = jsonData["dummy_data"];
      });
    } catch (error) {
      print(error);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: data.isEmpty
          ? const Center(child: Text('Loading data...'))
          : ListView.builder(
          itemCount: data.length,
          itemBuilder: (context, index) => DataTile(data: data[index]),
      ),
    );
  }
}