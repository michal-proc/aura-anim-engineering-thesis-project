export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
}

export interface RegisterUserPayload {
  email: string;
  username: string;
  password: string;
  full_name: string;
}

export interface ForgotPasswordPayload {
  email: string;
}

export interface ResetPasswordPayload {
  token: string;
  password: string;
}

export interface LoginUserPayload {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface LoginUserResponse {
  access_token: string;
  token_type: string;
  refresh_token?: string;
  user?: User;
}

export interface ReactivateAccountPayload {
  email: string;
  password: string;
}
