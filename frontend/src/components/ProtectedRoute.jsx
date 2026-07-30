// Wraps any page that requires login. If there's no token,
// it redirects to /login instead of rendering the page.
// This is the frontend mirror of your backend's get_current_user
// dependency rejecting an unauthenticated request.

import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    // "replace" so the login redirect doesn't pile up in browser history.
    return <Navigate to="/login" replace />;
  }

  return children;
}
