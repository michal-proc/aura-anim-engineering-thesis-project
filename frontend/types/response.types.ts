/**
 * Error codes for API responses
 */
export enum ErrorCode {
  INVALID_CREDENTIALS = "INVALID_CREDENTIALS",
  NETWORK_ERROR = "NETWORK_ERROR",
  UNKNOWN_ERROR = "UNKNOWN_ERROR",
  NOT_FOUND = "NOT_FOUND",
  INVALID_STATUS = "INVALID_STATUS",
}

/**
 * Success response structure with optional metadata
 */
export interface ApiSuccessResponse<T, M = undefined> {
  success: true;
  data: T;
  meta?: M;
}

/**
 * Error response structure
 */
export interface ApiErrorResponse {
  success: false;
  error: {
    code: ErrorCode | string;
    message?: string;
  };
}

/**
 * Generic API response type
 */
export type ApiResponse<T, M = undefined> =
  | ApiSuccessResponse<T, M>
  | ApiErrorResponse;
