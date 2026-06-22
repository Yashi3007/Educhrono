import { useState, useEffect } from "react";
import { loginUser } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  // ✅ Auto redirect if user already logged in
  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("edu_user"));
    if (user?.role) {
      redirectByRole(user.role);
    }
  }, [navigate]);

  // 🔹 Helper for role-based navigation
  const redirectByRole = (role) => {
    const r = role.toUpperCase();
    switch (r) {
      case "ADMIN":
        navigate("/dashboard/timetable");
        break;
      case "HOD":
        navigate("/dashboard/hod");
        break;
      case "FACULTY":
      case "TEACHER":
        navigate("/dashboard/faculty");
        break;
      case "STUDENT":
        navigate("/dashboard/student");
        break;
      default:
        navigate("/dashboard/timetable");
    }
  };

  // ✅ Handle login form submit
  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await loginUser({ email, password });
      const user = res.data.user;

      // Save in AuthContext + localStorage
      login(user);
      localStorage.setItem("edu_user", JSON.stringify(user));

      // Redirect based on role
      redirectByRole(user.role);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Invalid credentials.");
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gray-100">
      <form
        onSubmit={handleLogin}
        className="bg-white p-8 rounded-2xl shadow-md w-96"
      >
        <h1 className="text-2xl font-semibold mb-6 text-center text-blue-600">
          EduChrono Login
        </h1>

        <input
          type="email"
          placeholder="Email"
          className="w-full mb-4 p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full mb-4 p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2.5 rounded-md hover:bg-blue-700 transition duration-200"
        >
          Login
        </button>
        <p className="text-sm text-center mt-4 text-gray-500">
  Forgot your password? 
           <span className="text-blue-600 font-medium cursor-pointer">
    Contact admin
  </span>
</p>
      </form>
    </div>
  );
};

export default Login;
