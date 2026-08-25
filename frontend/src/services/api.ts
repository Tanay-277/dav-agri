import axios from "axios"
import type { AxiosError } from "axios"

const baseURL = import.meta.env.VITE_API_BASE_URL || "/api/v1"

export const api = axios.create({
  baseURL,
  timeout: 20_000,
  headers: { "Content-Type": "application/json" },
})

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const status = error.response?.status
    const message =
      error.response?.data?.detail ||
      error.message ||
      "An unexpected error occurred"
    return Promise.reject(new ApiError(status, message))
  }
)

export class ApiError extends Error {
  status?: number

  constructor(status: number | undefined, message: string) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}
