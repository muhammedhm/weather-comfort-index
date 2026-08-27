import { Auth0Provider } from "@auth0/auth0-react";

/**
 * Wraps the app with Auth0's context. `authorizationParams.audience` is what
 * makes Auth0 issue a JWT *access token* (not just an ID token) scoped to
 * our API — without it, auth0-react gives you an opaque token that the
 * FastAPI backend can't verify as a JWT.
 */
export default function Auth0ProviderWithNavigate({ children }) {
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  const audience = import.meta.env.VITE_AUTH0_AUDIENCE;

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: audience,
      }}
      cacheLocation="localstorage"
      useRefreshTokens={true}
    >
      {children}
    </Auth0Provider>
  );
}
