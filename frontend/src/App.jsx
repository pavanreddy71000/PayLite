// Route table. "/" is the protected wallet page; "/login" is public.
// ProtectedRoute guards the wallet — no token means redirect to login.

import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Wallet from "./pages/Wallet";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Wallet />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
