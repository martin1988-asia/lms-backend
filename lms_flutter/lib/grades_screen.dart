import 'package:flutter/material.dart';
import 'dart:convert';

import 'api_client.dart';

class GradesScreen extends StatefulWidget {
  final int assignmentId;
  final String assignmentTitle;

  const GradesScreen({super.key, required this.assignmentId, required this.assignmentTitle});

  @override
  State<GradesScreen> createState() => _GradesScreenState();
}

class _GradesScreenState extends State<GradesScreen> {
  List<dynamic> grades = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchGrades();
  }

  Future<void> fetchGrades() async {
    try {
      final response = await ApiClient.get(
          "grades/grades/?submission__assignment=${widget.assignmentId}");
      print("Grades status: ${response.statusCode}");
      print("Grades body: ${response.body}");

      if (response.statusCode == 200) {
        setState(() {
          grades = json.decode(response.body);
          isLoading = false;
        });
      } else {
        setState(() {
          isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Failed to load grades: ${response.statusCode}"),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Error fetching grades: $e"),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Grades - ${widget.assignmentTitle}")),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : grades.isEmpty
              ? const Center(child: Text("No grades yet"))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: grades.length,
                  itemBuilder: (context, index) {
                    final grade = grades[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 4,
                      child: ListTile(
                        leading: const Icon(Icons.grade, color: Colors.purple),
                        title: Text(
                          "Score: ${grade['score'] ?? 'N/A'}",
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text("Feedback: ${grade['feedback'] ?? 'No feedback'}"),
                      ),
                    );
                  },
                ),
    );
  }
}
