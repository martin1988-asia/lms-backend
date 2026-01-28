import 'package:flutter/material.dart';
import 'dart:convert';

// Import the login screen and ApiClient
import 'login_screen.dart';
import 'api_client.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LMS Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginScreen(),
        '/courses': (context) => const CoursesPage(),
      },
    );
  }
}

class CoursesPage extends StatefulWidget {
  const CoursesPage({super.key});

  @override
  State<CoursesPage> createState() => _CoursesPageState();
}

class _CoursesPageState extends State<CoursesPage> {
  List<dynamic> courses = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchCourses();
  }

  Future<void> fetchCourses() async {
    try {
      final response = await ApiClient.get("courses/courses/");
      print("Courses status: ${response.statusCode}");
      print("Courses body: ${response.body}");
      if (response.statusCode == 200) {
        setState(() {
          courses = json.decode(response.body);
          isLoading = false;
        });
      } else {
        setState(() => isLoading = false);
        throw Exception("Failed to load courses: ${response.statusCode}");
      }
    } catch (e) {
      setState(() => isLoading = false);
      debugPrint("Error fetching courses: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Courses")),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: courses.length,
              itemBuilder: (context, index) {
                final course = courses[index];
                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  child: ListTile(
                    leading: const Icon(Icons.school, color: Colors.blue),
                    title: Text(course['title'] ?? 'No title',
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text(course['description'] ?? 'No description'),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => AssignmentsPage(
                            courseId: course['id'],
                            courseTitle: course['title'],
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

class AssignmentsPage extends StatefulWidget {
  final int courseId;
  final String courseTitle;

  const AssignmentsPage({super.key, required this.courseId, required this.courseTitle});

  @override
  State<AssignmentsPage> createState() => _AssignmentsPageState();
}

class _AssignmentsPageState extends State<AssignmentsPage> {
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
        setState(() => isLoading = false);
        throw Exception("Failed to load assignments: ${response.statusCode}");
      }
    } catch (e) {
      setState(() => isLoading = false);
      debugPrint("Error fetching assignments: $e");
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
                  itemCount: assignments.length,
                  itemBuilder: (context, index) {
                    final assignment = assignments[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      child: ListTile(
                        leading: const Icon(Icons.assignment, color: Colors.green),
                        title: Text(assignment['title'] ?? 'No title',
                            style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text(assignment['description'] ?? 'No description'),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => GradesPage(
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

class GradesPage extends StatefulWidget {
  final int assignmentId;
  final String assignmentTitle;

  const GradesPage({super.key, required this.assignmentId, required this.assignmentTitle});

  @override
  State<GradesPage> createState() => _GradesPageState();
}

class _GradesPageState extends State<GradesPage> {
  List<dynamic> grades = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchGrades();
  }

  Future<void> fetchGrades() async {
    try {
      final response = await ApiClient.get("grades/grades/?submission__assignment=${widget.assignmentId}");
      print("Grades status: ${response.statusCode}");
      print("Grades body: ${response.body}");
      if (response.statusCode == 200) {
        setState(() {
          grades = json.decode(response.body);
          isLoading = false;
        });
      } else {
        setState(() => isLoading = false);
        throw Exception("Failed to load grades: ${response.statusCode}");
      }
    } catch (e) {
      setState(() => isLoading = false);
      debugPrint("Error fetching grades: $e");
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
                  itemCount: grades.length,
                  itemBuilder: (context, index) {
                    final grade = grades[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      child: ListTile(
                        leading: const Icon(Icons.grade, color: Colors.purple),
                        title: Text("Score: ${grade['score'] ?? 'N/A'}",
                            style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text("Feedback: ${grade['feedback'] ?? 'No feedback'}"),
                      ),
                    );
                  },
                ),
    );
  }
}
