import axios from 'axios'

// Local development - direct service URLs
const AUTH_SERVICE = 'http://localhost:8001'
const TOKEN_SERVICE = 'http://localhost:8002'
const VOTE_SERVICE = 'http://localhost:8003'
const BULLETIN_SERVICE = 'http://localhost:8004' // Bulletin board service
const ELECTION_SERVICE = 'http://localhost:8005'
const CODE_SHEET_SERVICE = 'http://localhost:8006' // Code sheet service

// Create axios instances for each service
export const authApi = axios.create({
  baseURL: `${AUTH_SERVICE}/api`,
  headers: { 'Content-Type': 'application/json' },
})

export const electionApi = axios.create({
  baseURL: `${ELECTION_SERVICE}/api`,
  headers: { 'Content-Type': 'application/json' },
})

export const tokenApi = axios.create({
  baseURL: `${TOKEN_SERVICE}/api`,
  headers: { 'Content-Type': 'application/json' },
})

export const voteApi = axios.create({
  baseURL: `${VOTE_SERVICE}/api`,
  headers: { 'Content-Type': 'application/json' },
})

export const bulletinApi = axios.create({
  baseURL: `${BULLETIN_SERVICE}/api`,
  headers: { 'Content-Type': 'application/json' },
})

export const codeSheetApi = axios.create({
  baseURL: `${CODE_SHEET_SERVICE}/api`,
  headers: { 'Content-Type': 'application/json' },
})

// Default api for backwards compatibility
const api = authApi

// Request interceptor to add auth token to all services
const requestInterceptor = (config: any) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}

// Response interceptor for error handling
const responseInterceptor = (error: any) => {
  if (error.response?.status === 401) {
    localStorage.removeItem('accessToken')
    window.location.href = '/login'
  }
  return Promise.reject(error)
}

// Apply interceptors to all API instances
;[authApi, electionApi, tokenApi, voteApi, bulletinApi, codeSheetApi].forEach((apiInstance) => {
  apiInstance.interceptors.request.use(requestInterceptor, (error) => Promise.reject(error))
  apiInstance.interceptors.response.use((response) => response, responseInterceptor)
})

export default api
