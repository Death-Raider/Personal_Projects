import 'package:flutter/material.dart';
import 'package:wish/Widgets/drawer.dart';
import 'package:wish/utils/routes.dart';

class Question extends StatelessWidget {
  const Question({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MyPage(title:"Create Questionnair");
  }
}

class MyPage extends StatefulWidget {
  const MyPage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<MyPage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyPage> {
  final List<Questionnaire> questionnaires = [];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: MyDrawer(),
      appBar: AppBar(
        backgroundColor: Color(0xFFF4AAC9),
        title: Text(widget.title),
      ),
      body: ListView.builder(
        itemCount: questionnaires.length,
        itemBuilder: (context, index) => QuestionnaireCard(
          questionnaire: questionnaires[index],
          onFilterSelected: _handleFilterSelected(questionnaires[index]), // Wrap onFilterSelected in null-safe callback
          onDelete: () => setState(() => questionnaires.removeAt(index)),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => setState(() => questionnaires.add(Questionnaire())),
        tooltip: 'Add Questionnaire',
        // backgroundColor: Color(0x4AAC9FF),
        child: const Icon(
            Icons.add,
        ),
      ),
    );
  }

  // Helper function to create a null-safe callback
  ValueChanged<String?> _handleFilterSelected(Questionnaire questionnaire) {
    return (filter) => setState(() => questionnaire.filter);
    // return filter;
  }
}

class Questionnaire {
  String title = 'Questionnaire';
  String filter = 'Age';

  Questionnaire();
}

class QuestionnaireCard extends StatefulWidget {
  final Questionnaire questionnaire;
  final ValueChanged<String?> onFilterSelected;
  final VoidCallback onDelete;

  const QuestionnaireCard({
    Key? key,
    required this.questionnaire,
    required this.onFilterSelected,
    required this.onDelete,
  }) : super(key: key);

  @override
  State<QuestionnaireCard> createState() => _QuestionnaireCardState();
}

class _QuestionnaireCardState extends State<QuestionnaireCard> {
  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(8.0),
      child: Row(
        children: [
          const Icon(Icons.question_answer),
          const SizedBox(width: 8.0),
          Text(widget.questionnaire.title),
          Spacer(),
          DropdownButton<String>(
            value: widget.questionnaire.filter,
            items: const [
              DropdownMenuItem(
                value: 'Age',
                child: Text('Age'),
              ),
              DropdownMenuItem(
                value: 'Place',
                child: Text('Place'),
              ),
            ],
            onChanged: widget.onFilterSelected, // Use the null-safe callback
          ),
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: widget.onDelete,
          ),
        ],
      ),
    );
  }
}
