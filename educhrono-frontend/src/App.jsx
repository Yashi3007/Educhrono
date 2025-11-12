import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

// Pages
import Login from "./pages/Login";
import DashboardHOD from "./pages/DashboardHOD";
import DashboardFaculty from "./pages/DashboardFaculty";
import DashboardStudent from "./pages/DashboardStudent";
import DashboardTimetable from "./pages/DashboardTimetable";
import "./css/index.css";


const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user } = useAuth();

  // if not logged in
  if (!user) return <Navigate to="/" replace />;

  // if logged in but not allowed
  if (allowedRoles && !allowedRoles.includes(user.role?.toUpperCase())) {
    return <Navigate to="/" replace />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* Login */}
        <Route path="/" element={<Login />} />

        {/* HOD Dashboard */}
        <Route
          path="/dashboard/hod"
          element={
            <ProtectedRoute allowedRoles={["HOD"]}>
              <DashboardHOD />
            </ProtectedRoute>
          }
        />

        {/* Faculty Dashboard */}
        <Route
          path="/dashboard/faculty"
          element={
            <ProtectedRoute allowedRoles={["FACULTY"]}>
              <DashboardFaculty />
            </ProtectedRoute>
          }
        />

        {/* Student Dashboard */}
        <Route
          path="/dashboard/student"
          element={
            <ProtectedRoute allowedRoles={["STUDENT"]}>
              <DashboardStudent />
            </ProtectedRoute>
          }
        />

        {/* Timetable (generic page) */}
        <Route
          path="/dashboard/timetable"
          element={
            <ProtectedRoute>
              <DashboardTimetable />
            </ProtectedRoute>
          }
        />

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
