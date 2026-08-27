import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import LoginButton from "./components/LoginButton.jsx";
import LogoutButton from "./components/LogoutButton.jsx";
import DarkModeToggle from "./components/DarkModeToggle.jsx";
import Dashboard from "./components/Dashboard.jsx";

export default function App() {
  const { isAuthenticated, isLoading, error } = useAuth0();
  const [dark, setDark] = useState(
    () => localStorage.getItem("theme") === "dark"
  );

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>🌤️ Weather Comfort Index</h1>
        <div className="app-header__actions">
          <DarkModeToggle dark={dark} setDark={setDark} />
          {isAuthenticated && <LogoutButton />}
        </div>
      </header>

      <main>
        {isLoading && <p className="status-msg">Loading…</p>}
        {error && (
          <p className="status-msg status-msg--error">{error.message}</p>
        )}
        {!isLoading && !isAuthenticated && (
          <div className="login-gate">
            <p>Log in to view the Comfort Index dashboard.</p>
            <LoginButton />
          </div>
        )}
        {isAuthenticated && <Dashboard />}
      </main>
    </div>
  );
}
