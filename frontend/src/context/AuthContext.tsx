import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { apiFetch, login as apiLogin } from "../api/client";

type User = { id: number; email: string; full_name: string; role: string };

type AuthContextValue = {
  user: User | null;
  token: string | null;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("fixora_token"));
  const [user, setUser] = useState<User | null>(null);

  const loadUser = useCallback(async (t: string) => {
    const me = await apiFetch<User>("/api/v1/auth/me", {}, t);
    setUser(me);
  }, []);

  useEffect(() => {
    if (token) loadUser(token).catch(() => setToken(null));
    else setUser(null);
  }, [token, loadUser]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAdmin: user?.role === "administrator",
      login: async (email, password) => {
        const { access_token } = await apiLogin(email, password);
        localStorage.setItem("fixora_token", access_token);
        setToken(access_token);
      },
      logout: () => {
        localStorage.removeItem("fixora_token");
        setToken(null);
        setUser(null);
      },
    }),
    [user, token]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
