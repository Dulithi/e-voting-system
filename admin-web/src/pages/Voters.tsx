import { useEffect, useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Tooltip,
} from '@mui/material'
import { CheckCircle, Pending, Cancel } from '@mui/icons-material'
import { authApi } from '../services/api'
import React from 'react'

interface Voter {
  user_id: string
  full_name: string
  email: string
  nic: string
  kyc_status: string
  created_at: string
  last_login_at: string | null
}

export default function Voters() {
  const [voters, setVoters] = useState<Voter[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadVoters()
  }, [])

  const loadVoters = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await authApi.get('/users/list')
      setVoters(response.data)
    } catch (error: any) {
      console.error('Failed to load voters:', error)
      setError(error.response?.data?.detail || 'Failed to load voters')
    } finally {
      setLoading(false)
    }
  }

  const handleApproveKYC = async (userId: string) => {
    try {
      await authApi.post(`/users/kyc/approve/${userId}`)
      loadVoters()
    } catch (error: any) {
      console.error('Failed to approve KYC:', error)
      alert(error.response?.data?.detail || 'Failed to approve KYC')
    }
  }

  const handleRejectKYC = async (userId: string) => {
    if (!confirm('Are you sure you want to reject this KYC application?')) {
      return
    }
    try {
      await authApi.post(`/users/kyc/reject/${userId}`)
      loadVoters()
    } catch (error: any) {
      console.error('Failed to reject KYC:', error)
      alert(error.response?.data?.detail || 'Failed to reject KYC')
    }
  }

  const getKYCColor = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return 'success'
      case 'PENDING':
        return 'warning'
      case 'REJECTED':
        return 'error'
      default:
        return 'default'
    }
  }

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
        Voters
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Name</strong></TableCell>
              <TableCell><strong>Email</strong></TableCell>
              <TableCell><strong>NIC</strong></TableCell>
              <TableCell><strong>KYC Status</strong></TableCell>
              <TableCell><strong>Registered</strong></TableCell>
              <TableCell><strong>Last Login</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {voters.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography variant="body2" color="text.secondary" py={3}>
                    No voters registered yet
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              voters.map((voter) => (
                <TableRow key={voter.user_id} hover>
                  <TableCell>{voter.full_name}</TableCell>
                  <TableCell>{voter.email}</TableCell>
                  <TableCell>{voter.nic}</TableCell>
                  <TableCell>
                    <Chip
                      label={voter.kyc_status}
                      color={getKYCColor(voter.kyc_status) as any}
                      size="small"
                      icon={
                        voter.kyc_status === 'APPROVED' ? <CheckCircle /> :
                        voter.kyc_status === 'PENDING' ? <Pending /> :
                        <Cancel />
                      }
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">
                      {new Date(voter.created_at).toLocaleDateString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">
                      {voter.last_login_at 
                        ? new Date(voter.last_login_at).toLocaleDateString()
                        : 'Never'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {voter.kyc_status === 'PENDING' && (
                      <Box display="flex" gap={1}>
                        <Tooltip title="Approve KYC">
                          <Button
                            size="small"
                            variant="contained"
                            color="success"
                            onClick={() => handleApproveKYC(voter.user_id)}
                          >
                            Approve
                          </Button>
                        </Tooltip>
                        <Tooltip title="Reject KYC">
                          <Button
                            size="small"
                            variant="outlined"
                            color="error"
                            onClick={() => handleRejectKYC(voter.user_id)}
                          >
                            Reject
                          </Button>
                        </Tooltip>
                      </Box>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}
