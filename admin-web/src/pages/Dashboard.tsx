import { useEffect, useState } from 'react'
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  HowToVote as ElectionsIcon,
  People as PeopleIcon,
  CheckCircle as ActiveIcon,
  Schedule as PendingIcon,
} from '@mui/icons-material'
import { electionApi } from '../services/api'
import React from 'react'

interface Stats {
  total_elections: number
  active_elections: number
  total_voters: number
  pending_kyc: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    total_elections: 0,
    active_elections: 0,
    total_voters: 0,
    pending_kyc: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await electionApi.get('/election/stats/dashboard')
      setStats(response.data)
    } catch (error: any) {
      console.error('Failed to load stats:', error)
      setError(error.response?.data?.detail || 'Failed to load dashboard statistics')
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    {
      title: 'Total Elections',
      value: stats.total_elections,
      icon: <ElectionsIcon sx={{ fontSize: 40 }} />,
      color: '#1976d2',
    },
    {
      title: 'Active Elections',
      value: stats.active_elections,
      icon: <ActiveIcon sx={{ fontSize: 40 }} />,
      color: '#2e7d32',
    },
    {
      title: 'Total Voters',
      value: stats.total_voters,
      icon: <PeopleIcon sx={{ fontSize: 40 }} />,
      color: '#ed6c02',
    },
    {
      title: 'Pending KYC',
      value: stats.pending_kyc,
      icon: <PendingIcon sx={{ fontSize: 40 }} />,
      color: '#d32f2f',
    },
  ]

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {statCards.map((card) => (
          <Grid item xs={12} sm={6} md={3} key={card.title}>
            <Card elevation={2}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      {card.title}
                    </Typography>
                    <Typography variant="h4">{card.value}</Typography>
                  </Box>
                  <Box sx={{ color: card.color }}>{card.icon}</Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper sx={{ mt: 4, p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Welcome to the SecureVote Admin Panel. Use the sidebar to navigate through different sections.
        </Typography>
      </Paper>
    </Box>
  )
}
