export default function DarkModeToggle({ dark, setDark }) {
  return (
    <button
      className="btn btn-icon"
      onClick={() => setDark(!dark)}
      aria-label="Toggle dark mode"
      title="Toggle dark mode"
    >
      {dark ? "☀️ Light" : "🌙 Dark"}
    </button>
  );
}
