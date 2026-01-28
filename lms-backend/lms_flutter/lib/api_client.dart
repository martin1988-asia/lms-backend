import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiClient {
  static const String baseUrl = "http://127.0.0.1:8000/api";
  static final FlutterSecureStorage storage = FlutterSecureStorage();

  // Save tokens securely
  static Future<void> saveTokens(String access, String refresh) async {
    await storage.write(key: "access", value: access);
    await storage.write(key: "refresh", value: refresh);
  }

  // Get stored access token
  static Future<String?> getAccessToken() async {
    return await storage.read(key: "access");
  }

  // Get stored refresh token
  static Future<String?> getRefreshToken() async {
    return await storage.read(key: "refresh");
  }

  // Refresh access token using refresh token
  static Future<String?> refreshAccessToken() async {
    final refreshToken = await getRefreshToken();
    if (refreshToken == null) return null;

    final url = Uri.parse("$baseUrl/token/refresh/");
    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: json.encode({"refresh": refreshToken}),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final newAccess = data['access'];
      await storage.write(key: "access", value: newAccess);
      return newAccess;
    } else {
      return null;
    }
  }

  // ✅ Generic GET request with auto-refresh
  static Future<http.Response> get(String endpoint) async {
    String? token = await getAccessToken();
    final url = Uri.parse("$baseUrl/$endpoint");

    var response = await http.get(url, headers: {"Authorization": "Bearer $token"});

    if (response.statusCode == 401) {
      token = await refreshAccessToken();
      if (token != null) {
        response = await http.get(url, headers: {"Authorization": "Bearer $token"});
      }
    }
    return response;
  }

  // ✅ Generic POST request with auto-refresh
  static Future<http.Response> post(String endpoint, Map<String, dynamic> body) async {
    String? token = await getAccessToken();
    final url = Uri.parse("$baseUrl/$endpoint");

    var response = await http.post(
      url,
      headers: {
        "Authorization": "Bearer $token",
        "Content-Type": "application/json",
      },
      body: json.encode(body),
    );

    if (response.statusCode == 401) {
      token = await refreshAccessToken();
      if (token != null) {
        response = await http.post(
          url,
          headers: {
            "Authorization": "Bearer $token",
            "Content-Type": "application/json",
          },
          body: json.encode(body),
        );
      }
    }
    return response;
  }

  // ✅ Generic PUT request with auto-refresh
  static Future<http.Response> put(String endpoint, Map<String, dynamic> body) async {
    String? token = await getAccessToken();
    final url = Uri.parse("$baseUrl/$endpoint");

    var response = await http.put(
      url,
      headers: {
        "Authorization": "Bearer $token",
        "Content-Type": "application/json",
      },
      body: json.encode(body),
    );

    if (response.statusCode == 401) {
      token = await refreshAccessToken();
      if (token != null) {
        response = await http.put(
          url,
          headers: {
            "Authorization": "Bearer $token",
            "Content-Type": "application/json",
          },
          body: json.encode(body),
        );
      }
    }
    return response;
  }

  // ✅ Generic DELETE request with auto-refresh
  static Future<http.Response> delete(String endpoint) async {
    String? token = await getAccessToken();
    final url = Uri.parse("$baseUrl/$endpoint");

    var response = await http.delete(url, headers: {"Authorization": "Bearer $token"});

    if (response.statusCode == 401) {
      token = await refreshAccessToken();
      if (token != null) {
        response = await http.delete(url, headers: {"Authorization": "Bearer $token"});
      }
    }
    return response;
  }
}
