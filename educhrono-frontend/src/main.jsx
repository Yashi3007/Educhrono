import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";
import "./css/index.css";

const originalLog = console.log;
console.log = (...args) => {
  if (args[0]?.includes?.("Download the React DevTools")) return;
  originalLog(...args);
};

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
