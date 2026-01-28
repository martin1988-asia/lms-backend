import 'package:flutter/material.dart';
import 'dart:convert';

import 'grades_screen.dart';
import 'api_client.dart';

class AssignmentsScreen extends StatefulWidget {
  final int courseId;
  final String courseTitle;

  const AssignmentsScreen({super.key, required this.courseId, required this.courseTitle});

  @override
  State<AssignmentsScreen> createState() => _AssignmentsScreenState();
}

class _AssignmentsScreenState extends State<AssignmentsScreen> {
  List<dynamic> assignments = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchAssignments();
  }

  Future<void> fetchAssignments() async {
    try {
      final response = await ApiClient.get("assignments/assignments/?course=${widget.courseId}");
      print("Assignments status: ${response.statusCode}");
      print("Assignments body: ${response.body}");

      if (response.statusCode == 200) {
        setState(() {
          assignments = json.decode(response.body);
          isLoading = false;
        });
      } else {
        setState(() {
          isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Failed to load assignments: ${response.statusCode}"),
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
          content: Text("Error fetching assignments: $e"),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Assignments - ${widget.courseTitle}")),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : assignments.isEmpty
              ? const Center(child: Text("No assignments yet"))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: assignments.length,
                  itemBuilder: (context, index) {
                    final assignment = assignments[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 4,
                      child: ListTile(
                        leading: const Icon(Icons.assignment, color: Colors.green),
                        title: Text(
                          assignment['title'] ?? 'No title',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(assignment['description'] ?? 'No description'),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => GradesScreen(
                                assignmentId: assignment['id'],
                                assignmentTitle: assignment['title'],
                              ),
                            ),
                          );
                        },
                      ),
                    );
                  },
                ),
    );
  }
}
