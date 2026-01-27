import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

// ✅ Pages
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import Courses from "./pages/Courses";
import Assignments from "./pages/Assignments";
import Grades from "./pages/Grades";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import UserManagement from "./pages/UserManagement";
import Analytics from "./pages/Analytics";
import ManageCourses from "./pages/ManageCourses";
import GradeSubmissions from "./pages/GradeSubmissions";
import NotFound from "./pages/NotFound";

// ✅ Components
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

// ✅ Environment variable (safe logging)
const API_URL = process.env.REACT_APP_API_URL;
if (process.env.NODE_ENV !== "production") {
  console.log("Backend URL:", API_URL);
}

function App() {
  return (
    <Router>
      <Routes>
        {/* -------------------- Public Routes -------------------- */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password/:uidb64/:token" element={<ResetPassword />} />

        {/* -------------------- Protected Routes -------------------- */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/courses"
          element={
            <ProtectedRoute>
              <Layout>
                <Courses />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/assignments"
          element={
            <ProtectedRoute>
              <Layout>
                <Assignments />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/grades"
          element={
            <ProtectedRoute>
              <Layout>
                <Grades />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* -------------------- Admin Routes -------------------- */}
        <Route
          path="/users"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <Layout>
                <UserManagement />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <Layout>
                <Analytics />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* -------------------- Instructor Routes -------------------- */}
        <Route
          path="/manage-courses"
          element={
            <ProtectedRoute allowedRoles={["instructor"]}>
              <Layout>
                <ManageCourses />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/grade-submissions"
          element={
            <ProtectedRoute allowedRoles={["instructor"]}>
              <Layout>
                <GradeSubmissions />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* -------------------- Redirects & Fallback -------------------- */}
        <Route path="/home" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}

export default App;
