import { apiRequest } from "./client";
import type {
  User,
  UpdateUserPayload,
  ChangePasswordPayload,
  DeactivateAccountPayload,
  DeleteAccountPayload,
} from "@/types/user.types";
import { USE_MOCK_DATA, mockUser } from "@/lib/mock-data";

export const userApi = {
  updateProfile: async (
    payload: UpdateUserPayload,
    token: string,
  ): Promise<User> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      return { ...mockUser, ...payload };
    }
    return apiRequest<User>("/users/me", {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
  },

  changePassword: async (
    payload: ChangePasswordPayload,
    token: string,
  ): Promise<void> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      return;
    }
    return apiRequest<void>("/users/me/change-password", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
  },

  deactivateAccount: async (
    payload: DeactivateAccountPayload,
    token: string,
  ): Promise<void> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      return;
    }
    return apiRequest<void>("/users/me/deactivate", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
  },

  deleteAccount: async (
    payload: DeleteAccountPayload,
    token: string,
  ): Promise<void> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      return;
    }
    return apiRequest<void>("/users/me", {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
  },
};
