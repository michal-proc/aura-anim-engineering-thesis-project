export interface User {
  user_id: number;
  username: string;
  full_name: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface UpdateUserPayload {
  email?: string;
  username?: string;
  full_name?: string;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

export interface DeactivateAccountPayload {
  password: string;
}

export interface DeleteAccountPayload {
  password: string;
}
