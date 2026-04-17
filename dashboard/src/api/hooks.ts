import { useQuery, useMutation } from '@tanstack/react-query'
import api from './client'

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.get('/dashboard/stats').then(r => r.data),
    refetchInterval: 30000,
  })
}

export function useClaims(page: number, size: number, filters?: Record<string, string>) {
  return useQuery({
    queryKey: ['claims', page, size, filters],
    queryFn: () => api.get('/claims', { params: { page, size, ...filters } }).then(r => r.data),
  })
}

export function useClaimStatus(an: string) {
  return useQuery({
    queryKey: ['claim-status', an],
    queryFn: () => api.get(`/status/${an}`).then(r => r.data),
    enabled: !!an,
  })
}

export function useLogin() {
  return useMutation({
    mutationFn: (credentials: { username: string; password: string }) =>
      api.post('/auth/login', credentials).then(r => r.data),
    onSuccess: (data) => {
      sessionStorage.setItem('access_token', data.access_token)
      sessionStorage.setItem('refresh_token', data.refresh_token)
    },
  })
}

export function useHISHealth() {
  return useQuery({
    queryKey: ['his-health'],
    queryFn: () => api.get('/his/health').then(r => r.data),
  })
}
