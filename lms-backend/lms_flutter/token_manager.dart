import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class TokenManager {
  static final storage = const FlutterSecureStorage();

  /// Get the current access token from storage
  static Future<String?> getAccessToken() async {
    return await storage.read(key: "accessToken");
  }

  /// Refresh the access token using the refresh token
  static Future<String?> refreshAccessToken() async {
    final refreshToken = await storage.read(key: "refreshToken");
    if (refreshToken == null) return null;

    final response = await http.post(
      Uri.parse("http://127.0.0.1:8000/api/token/refresh/"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"refresh": refreshToken}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final newAccess = data['access'];
      await storage.write(key: "accessToken", value: newAccess);
      return newAccess;
    } else {
      return null;
    }
  }

  /// Wrapper for GET requests with auto-refresh
  static Future<http.Response> authorizedGet(Uri url) async {
    String? token = await getAccessToken();
    var response = await http.get(url, headers: {"Authorization": "Bearer $token"});

    if (response.statusCode == 401) {
      token = await refreshAccessToken();
      if (token != null) {
        response = await http.get(url, headers: {"Authorization": "Bearer $token"});
      }
    }
    return response;
  }

  /// Wrapper for POST requests with auto-refresh
  static Future<http.Response> authorizedPost(Uri url, Map<String, dynamic> body) async {
    String? token = await getAccessToken();
    var response = await http.post(
      url,
      headers: {
        "Authorization": "Bearer $token",
        "Content-Type": "application/json",
      },
      body: jsonEncode(body),
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
          body: jsonEncode(body),
        );
      }
    }
    return response;
  }

  /// Wrapper for PUT requests with auto-refresh
  static Future<http.Response> authorizedPut(Uri url, Map<String, dynamic> body) async {
    String? token = await getAccessToken();
    var response = await http.put(
      url,
      headers: {
        "Authorization": "Bearer $token",
        "Content-Type": "application/json",
      },
      body: jsonEncode(body),
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
          body: jsonEncode(body),
        );
      }
    }
    return response;
  }

  /// Wrapper for DELETE requests with auto-refresh
  static Future<http.Response> authorizedDelete(Uri url) async {
    String? token = await getAccessToken();
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
