// Entry point. Wraps the whole app in:
//   BrowserRouter  — enables client-side routing (/login, /)
//   AuthProvider   — makes login state available everywhere
// Order matters only in that both must be ABOVE <App/>.

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import App from "./App.jsx";
import "./index.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
