export interface User {
  name: string;
  profilePic?: string | null;
}

export interface AuthContextType {
  user: User | null;
  isAuth: boolean;
  loading: boolean;
  login: (credentials: LoginRequest) => Promise<AuthResponse>;
  register: (data: RegisterRequest) => Promise<AuthResponse>;
  logout: () => Promise<void>;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  accessToken: string;
}
