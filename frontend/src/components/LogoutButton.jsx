import { useAuth0 } from "@auth0/auth0-react";

export default function LogoutButton() {
  const { logout, user } = useAuth0();
  return (
    <div className="user-bar">
      <span>{user?.email}</span>
      <button
        className="btn btn-secondary"
        onClick={() =>
          logout({ logoutParams: { returnTo: window.location.origin } })
        }
      >
        Log out
      </button>
    </div>
  );
}
