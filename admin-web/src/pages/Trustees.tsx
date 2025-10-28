import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material'
import {
  ArrowBack,
  Refresh,
  Add,
  Delete,
  VpnKey,
  Lock,
} from '@mui/icons-material'
import { electionApi, authApi } from '../services/api'
import React from 'react'

interface Trustee {
  trustee_id: string
  election_id: string
  user_id: string
  user_email: string
  user_name: string
  has_key_share: boolean
  shares_submitted: boolean
  created_at: string
}

interface User {
  user_id: string
  email: string
  full_name: string
}

export default function Trustees() {
  const { electionId } = useParams<{ electionId: string }>()
  const navigate = useNavigate()
  const [trustees, setTrustees] = useState<Trustee[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [addDialogOpen, setAddDialogOpen] = useState(false)
  const [selectedUserId, setSelectedUserId] = useState('')
  const [keyCeremonyLoading, setKeyCeremonyLoading] = useState(false)
  const [decryptionStatus, setDecryptionStatus] = useState<any>(null)
  const [tallyLoading, setTallyLoading] = useState(false)

  useEffect(() => {
    loadTrustees()
    loadUsers()
    loadDecryptionStatus()
  }, [electionId])

  const loadTrustees = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await electionApi.get(`/trustee/election/${electionId}`)
      setTrustees(response.data)
    } catch (error: any) {
      console.error('Failed to load trustees:', error)
      if (error.response?.status !== 404) {
        setError(error.response?.data?.detail || 'Failed to load trustees')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadUsers = async () => {
    try {
      const response = await authApi.get('/users/list')
      setUsers(response.data.filter((u: any) => !u.is_admin))
    } catch (error: any) {
      console.error('Failed to load users:', error)
    }
  }

  const loadDecryptionStatus = async () => {
    try {
      const response = await electionApi.get(`/trustee/election/${electionId}/decryption-status`)
      setDecryptionStatus(response.data)
    } catch (error: any) {
      console.error('Failed to load decryption status:', error)
    }
  }

  const handleAddTrustee = async () => {
    if (!selectedUserId) {
      alert('Please select a user')
      return
    }

    try {
      await electionApi.post('/trustee/add', {
        election_id: electionId,
        user_id: selectedUserId,
      })
      setAddDialogOpen(false)
      setSelectedUserId('')
      alert('Trustee added successfully!')
      await loadTrustees()
    } catch (error: any) {
      console.error('Failed to add trustee:', error)
      alert(error.response?.data?.detail || 'Failed to add trustee')
    }
  }

  const handleRemoveTrustee = async (trusteeId: string) => {
    if (!confirm('Remove this trustee? This can only be done before key ceremony.')) {
      return
    }

    try {
      await electionApi.delete(`/trustee/${trusteeId}`)
      alert('Trustee removed successfully')
      await loadTrustees()
    } catch (error: any) {
      console.error('Failed to remove trustee:', error)
      alert(error.response?.data?.detail || 'Failed to remove trustee')
    }
  }

  const handleInitiateKeyCeremony = async () => {
    if (
      !confirm(
        'Initiate key ceremony? This will generate the election keypair and distribute shares to all trustees. This cannot be undone.'
      )
    ) {
      return
    }

    try {
      setKeyCeremonyLoading(true)
      setError(null)
      const response = await electionApi.post('/trustee/key-ceremony', {
        election_id: electionId,
      })
      alert(
        `Key ceremony completed! Updated ${response.data.trustees_updated} trustees with key shares.`
      )
      await loadTrustees()
    } catch (error: any) {
      console.error('Failed to initiate key ceremony:', error)
      setError(error.response?.data?.detail || 'Failed to initiate key ceremony')
    } finally {
      setKeyCeremonyLoading(false)
    }
  }

  const handleDecryptAndTally = async () => {
    if (
      !confirm(
        'Decrypt and tally election results? This will combine trustee decryption shares and calculate final vote counts. This action is irreversible.'
      )
    ) {
      return
    }

    try {
      setTallyLoading(true)
      setError(null)
      const response = await electionApi.post(`/election/${electionId}/tally`)
      alert(
        `Election tallied successfully! Total votes: ${response.data.total_votes}\n` +
        `Trustees used: ${response.data.trustees_used}/${response.data.threshold_required}`
      )
      // Navigate to results page or refresh
      await loadDecryptionStatus()
      navigate(`/elections`)
    } catch (error: any) {
      console.error('Failed to tally election:', error)
      setError(error.response?.data?.detail || 'Failed to tally election')
    } finally {
      setTallyLoading(false)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  const canRemoveTrustees = !trustees.some(t => t.has_key_share)
  const canInitiateKeyCeremony =
    trustees.length > 0 &&
    !trustees.some(t => t.has_key_share)

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <IconButton onClick={() => navigate(-1)}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h4" flexGrow={1}>
          Election Trustees
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={loadTrustees}
          disabled={loading}
        >
          Refresh
        </Button>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setAddDialogOpen(true)}
          disabled={!canRemoveTrustees}
        >
          Add Trustee
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Status Cards */}
      <Box display="grid" gridTemplateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={2} mb={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">{trustees.length}</Typography>
            <Typography variant="body2" color="text.secondary">
              Total Trustees
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="h6">
              {trustees.filter(t => t.has_key_share).length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Keys Distributed
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="h6">
              {trustees.filter(t => t.shares_submitted).length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Shares Submitted
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="h6">
              {decryptionStatus?.threshold || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Required for Decryption
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Decryption Status */}
      {decryptionStatus && (
        <Alert
          severity={decryptionStatus.can_decrypt ? 'success' : 'info'}
          sx={{ mb: 3 }}
        >
          <Typography variant="body2">
            <strong>Decryption Status:</strong>{' '}
            {decryptionStatus.can_decrypt ? (
              <>
                ✅ Ready to decrypt! {decryptionStatus.trustees_submitted} of{' '}
                {decryptionStatus.threshold} required trustees have submitted shares.
              </>
            ) : (
              <>
                ⏳ Waiting for decryption shares. {decryptionStatus.trustees_submitted} trustees have submitted. 
                Need {decryptionStatus.trustees_needed} more (minimum {decryptionStatus.threshold} required).
              </>
            )}
          </Typography>
        </Alert>
      )}

      {/* Decrypt & Tally Button */}
      {decryptionStatus?.can_decrypt && (
        <Alert severity="success" sx={{ mb: 3 }}>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="body2">
              <strong>Ready to Tally Results!</strong> All required trustees have submitted 
              their decryption shares. Click to decrypt ballots and count votes.
            </Typography>
            <Button
              variant="contained"
              color="success"
              startIcon={<Lock />}
              onClick={handleDecryptAndTally}
              disabled={tallyLoading}
            >
              {tallyLoading ? 'Processing...' : 'Decrypt & Tally'}
            </Button>
          </Box>
        </Alert>
      )}

      {/* Key Ceremony Button */}
      {canInitiateKeyCeremony && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="body2">
              <strong>Ready for Key Ceremony!</strong> You can now
              generate and distribute key shares.
            </Typography>
            <Button
              variant="contained"
              startIcon={<VpnKey />}
              onClick={handleInitiateKeyCeremony}
              disabled={keyCeremonyLoading}
            >
              {keyCeremonyLoading ? 'Processing...' : 'Initiate Key Ceremony'}
            </Button>
          </Box>
        </Alert>
      )}

      {trustees.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center" py={4}>
              No trustees assigned yet.
              <br />
              <br />
              Add trustees to enable threshold cryptography for secure result decryption.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Name</strong></TableCell>
                <TableCell><strong>Email</strong></TableCell>
                <TableCell><strong>Key Share</strong></TableCell>
                <TableCell><strong>Decryption Share</strong></TableCell>
                <TableCell><strong>Added</strong></TableCell>
                <TableCell><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {trustees.map((trustee) => (
                <TableRow key={trustee.trustee_id} hover>
                  <TableCell>{trustee.user_name}</TableCell>
                  <TableCell>{trustee.user_email}</TableCell>
                  <TableCell>
                    {trustee.has_key_share ? (
                      <Chip label="Distributed" color="success" size="small" icon={<VpnKey />} />
                    ) : (
                      <Chip label="Pending" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    {trustee.shares_submitted ? (
                      <Chip label="Submitted" color="success" size="small" />
                    ) : (
                      <Chip label="Not Submitted" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">
                      {new Date(trustee.created_at).toLocaleDateString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {canRemoveTrustees && !trustee.has_key_share && (
                      <Tooltip title="Remove Trustee">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleRemoveTrustee(trustee.trustee_id)}
                        >
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Add Trustee Dialog */}
      <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Trustee</DialogTitle>
        <DialogContent>
          <Box mt={2}>
            <FormControl fullWidth>
              <InputLabel>Select User</InputLabel>
              <Select
                value={selectedUserId}
                onChange={(e) => setSelectedUserId(e.target.value)}
                label="Select User"
              >
                {users
                  .filter(u => !trustees.some(t => t.user_id === u.user_id))
                  .map((user) => (
                    <MenuItem key={user.user_id} value={user.user_id}>
                      {user.full_name} ({user.email})
                    </MenuItem>
                  ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleAddTrustee} disabled={!selectedUserId}>
            Add Trustee
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
