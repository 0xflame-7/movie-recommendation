import { useCallback, useEffect, useState } from "react";
import type {
  AuthResponse,
  User,
  LoginRequest,
  RegisterRequest,
  AuthContextType,
} from "@/types";
import type {
  AxiosError,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from "axios";
import { AuthContext } from "@/context/authContext";
import api from "@/lib/api";
import { toast } from "sonner";

interface Props {
  children: React.ReactNode;
}

interface ExtendedRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

export default function AuthProvider({ children }: Props) {
  const [token, setToken] = useState<string | null>(
    () => sessionStorage.getItem("authToken") || null
  );
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  // Persist token
  useEffect(() => {
    if (token) sessionStorage.setItem("authToken", token);
    else sessionStorage.removeItem("authToken");
  }, [token]);

  // Try refreshing on mount
  useEffect(() => {
    const fetchToken = async (): Promise<void> => {
      if (token) return;

      setLoading(true);
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/auth/refresh`,
          {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
          }
        );

        if (response.ok) {
          if (response.status === 204) {
            setToken(null);
            return;
          }
          const data = (await response.json()) as AuthResponse;
          setToken(data.accessToken);
        } else {
          setToken(null);
        }
      } catch {
        setToken(null);
      } finally {
        setLoading(false);
      }
    };

    fetchToken();

    // Only run once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchMe = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const response = await api.get<User>("/user/me");
      setUser(response.data);
      setLoading(false);
    } catch {
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Fetch user
  useEffect(() => {
    fetchMe();
  }, [fetchMe]);

  // Request interceptor
  useEffect(() => {
    const authInterceptor = api.interceptors.request.use(
      (config: ExtendedRequestConfig): ExtendedRequestConfig => {
        if (!config._retry && token) {
          config.headers = config.headers ?? {};
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      }
    );
    return () => api.interceptors.request.eject(authInterceptor);
  }, [token]);

  // Response interceptor (refresh)
  useEffect(() => {
    const refreshInterceptor = api.interceptors.response.use(
      (response: AxiosResponse): AxiosResponse => response,
      async (error: AxiosError): Promise<AxiosResponse | unknown> => {
        const originalRequest = error.config as ExtendedRequestConfig;

        if (
          error.response?.status === 401 &&
          !originalRequest._retry &&
          !originalRequest.url?.includes("/auth/refresh")
        ) {
          try {
            const response = await api.post<AuthResponse>(
              "/auth/refresh",
              {},
              { withCredentials: true }
            );
            const newToken = response.data.accessToken;
            setToken(newToken);

            originalRequest.headers = originalRequest.headers ?? {};
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            originalRequest._retry = true;

            return api(originalRequest);
          } catch (err) {
            setToken(null);
            setUser(null);
            return Promise.reject(err);
          }
        }

        return Promise.reject(error);
      }
    );
    return () => api.interceptors.response.eject(refreshInterceptor);
  }, []);

  // Actions
  const login = async (credentials: LoginRequest): Promise<AuthResponse> => {
    setLoading(true);
    try {
      const response = await api.post<AuthResponse>("/auth/login", credentials);
      setToken(response.data.accessToken);
      await fetchMe();
      toast.success("Welcome Back", {
        description: "You have been signed in successfully.",
      });
      return response.data;
    } catch (error: unknown) {
      toast.error("Login failed", {
        description: (error as Error)?.message || "An error occurred.",
      });
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: RegisterRequest): Promise<AuthResponse> => {
    setLoading(true);
    try {
      const response = await api.post<AuthResponse>("/auth/register", data);
      setToken(response.data.accessToken);
      await fetchMe();
      toast.success("Account Created", {
        description: "You have been registered successfully.",
      });
      return response.data;
    } catch (error: unknown) {
      toast.error("Registration failed", {
        description: (error as Error)?.message || "An error occurred.",
      });
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    setLoading(true);
    try {
      await api.post("/auth/logout", {}, { withCredentials: true });
      toast.success("Logged out", {
        description: "You have been logged out successfully.",
      });
    } finally {
      setToken(null);
      setUser(null);
      setLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    isAuth: !!user,
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
