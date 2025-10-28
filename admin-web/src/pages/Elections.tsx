import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
  Paper,
  Menu,
  MenuItem,
  IconButton,
  Tooltip,
} from '@mui/material'
import { 
  Add as AddIcon, 
  MoreVert as MoreVertIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Assessment as AssessmentIcon,
  Edit as EditIcon,
} from '@mui/icons-material'
import { electionApi } from '../services/api'
import { format } from 'date-fns'
import React from 'react'

interface Election {
  election_id: string
  title: string
  description: string | null
  start_time: string
  end_time: string
  status: string
  threshold_t: number
  total_trustees_n: number
}

export default function Elections() {
  const [elections, setElections] = useState<Election[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [openEditDialog, setOpenEditDialog] = useState(false)
  const [editingElection, setEditingElection] = useState<Election | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
    threshold_t: 5,
    total_trustees_n: 9,
  })
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [selectedElection, setSelectedElection] = useState<string | null>(null)
  const [updatingStatus, setUpdatingStatus] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    loadElections()
  }, [])

  const loadElections = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await electionApi.get('/election/list')
      setElections(response.data)
    } catch (error: any) {
      console.error('Failed to load elections:', error)
      setError(error.response?.data?.detail || 'Failed to load elections')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!formData.title.trim() || !formData.start_time || !formData.end_time) {
      alert('Please fill in all required fields')
      return
    }

    try {
      setSubmitting(true)
      await electionApi.post('/election/create', formData)
      setOpenDialog(false)
      setFormData({ 
        title: '', 
        description: '', 
        start_time: '', 
        end_time: '',
        threshold_t: 5,
        total_trustees_n: 9,
      })
      loadElections()
    } catch (error: any) {
      console.error('Failed to create election:', error)
      alert(error.response?.data?.detail || 'Failed to create election')
    } finally {
      setSubmitting(false)
    }
  }

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, electionId: string) => {
    event.stopPropagation()
    setAnchorEl(event.currentTarget)
    setSelectedElection(electionId)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
    setSelectedElection(null)
  }

  const handleStatusChange = async (newStatus: string) => {
    if (!selectedElection) return

    try {
      setUpdatingStatus(true)
      await electionApi.put(`/election/${selectedElection}/status`, { status: newStatus })
      handleMenuClose()
      loadElections()
    } catch (error: any) {
      console.error('Failed to update status:', error)
      alert(error.response?.data?.detail || 'Failed to update election status')
    } finally {
      setUpdatingStatus(false)
    }
  }

  const handleEdit = (election: Election) => {
    setEditingElection(election)
    setFormData({
      title: election.title,
      description: election.description || '',
      start_time: election.start_time.substring(0, 16), // Format for datetime-local
      end_time: election.end_time.substring(0, 16),
      threshold_t: election.threshold_t,
      total_trustees_n: election.total_trustees_n,
    })
    setOpenEditDialog(true)
    handleMenuClose()
  }

  const handleUpdate = async () => {
    if (!editingElection || !formData.title.trim() || !formData.start_time || !formData.end_time) {
      alert('Please fill in all required fields')
      return
    }

    try {
      setSubmitting(true)
      await electionApi.put(`/election/${editingElection.election_id}`, formData)
      setOpenEditDialog(false)
      setEditingElection(null)
      setFormData({ 
        title: '', 
        description: '', 
        start_time: '', 
        end_time: '',
        threshold_t: 5,
        total_trustees_n: 9,
      })
      loadElections()
    } catch (error: any) {
      console.error('Failed to update election:', error)
      alert(error.response?.data?.detail || 'Failed to update election')
    } finally {
      setSubmitting(false)
    }
  }

  const getStatusMenuItems = () => {
    const currentElection = elections.find(e => e.election_id === selectedElection)
    if (!currentElection) return []

    const statuses = [
      { value: 'DRAFT', label: 'Draft', icon: <EditIcon fontSize="small" />, description: 'Edit mode' },
      { value: 'ACTIVE', label: 'Active', icon: <PlayArrowIcon fontSize="small" />, description: 'Open for voting' },
      { value: 'CLOSED', label: 'Closed', icon: <StopIcon fontSize="small" />, description: 'Voting ended' },
      { value: 'TALLIED', label: 'Tallied', icon: <AssessmentIcon fontSize="small" />, description: 'Results published' },
    ]

    return statuses.filter(s => s.value !== currentElection.status)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'success'
      case 'DRAFT':
        return 'default'
      case 'CLOSED':
      case 'TALLIED':
        return 'info'
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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Elections</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Create Election
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {elections.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Elections Yet
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Create your first election to get started
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
          >
            Create Election
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {elections.map((election) => (
            <Grid item xs={12} md={6} key={election.election_id}>
              <Card
                sx={{ cursor: 'pointer', '&:hover': { boxShadow: 4 } }}
              >
                <CardContent onClick={() => navigate(`/elections/${election.election_id}`)}>
                  <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                    <Typography variant="h6">{election.title}</Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Chip
                        label={election.status}
                        color={getStatusColor(election.status) as any}
                        size="small"
                      />
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuOpen(e, election.election_id)}
                        disabled={updatingStatus}
                      >
                        <MoreVertIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {election.description || 'No description provided'}
                  </Typography>
                  <Typography variant="caption" display="block" mt={2}>
                    Start: {format(new Date(election.start_time), 'PPp')}
                  </Typography>
                  <Typography variant="caption" display="block">
                    End: {format(new Date(election.end_time), 'PPp')}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Status Change Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem 
          onClick={() => {
            const election = elections.find(e => e.election_id === selectedElection)
            if (election) handleEdit(election)
          }}
        >
          <Box display="flex" alignItems="center" gap={1}>
            <EditIcon fontSize="small" />
            <Typography variant="body2">Edit Election</Typography>
          </Box>
        </MenuItem>
        {elections.find(e => e.election_id === selectedElection)?.status === 'TALLIED' && (
          <MenuItem 
            onClick={() => {
              handleMenuClose()
              navigate(`/results/${selectedElection}`)
            }}
          >
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="body2">📊 View Results</Typography>
            </Box>
          </MenuItem>
        )}
        <MenuItem disabled sx={{ opacity: 1, mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Change Status
          </Typography>
        </MenuItem>
        {getStatusMenuItems().map((status) => (
          <MenuItem
            key={status.value}
            onClick={() => handleStatusChange(status.value)}
            disabled={updatingStatus}
          >
            <Box display="flex" alignItems="center" gap={1}>
              {status.icon}
              <Box>
                <Typography variant="body2">{status.label}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {status.description}
                </Typography>
              </Box>
            </Box>
          </MenuItem>
        ))}
      </Menu>

      <Dialog open={openDialog} onClose={() => !submitting && setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Election</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Election Title"
            fullWidth
            required
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            disabled={submitting}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            disabled={submitting}
          />
          <TextField
            margin="dense"
            label="Start Time"
            type="datetime-local"
            fullWidth
            required
            InputLabelProps={{ shrink: true }}
            value={formData.start_time}
            onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
            disabled={submitting}
          />
          <TextField
            margin="dense"
            label="End Time"
            type="datetime-local"
            fullWidth
            required
            InputLabelProps={{ shrink: true }}
            value={formData.end_time}
            onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
            disabled={submitting}
          />
          
          <Box sx={{ mt: 2, mb: 1 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              🔐 Threshold Cryptography Settings
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
              These settings control how many trustees are needed to decrypt election results.
            </Typography>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Tooltip title="Minimum number of trustees needed to decrypt results. Lower = less secure but more fault-tolerant.">
                <TextField
                  margin="dense"
                  label="Threshold (t)"
                  type="number"
                  fullWidth
                  required
                  value={formData.threshold_t}
                  onChange={(e) => {
                    const val = parseInt(e.target.value) || 1
                    setFormData({ 
                      ...formData, 
                      threshold_t: Math.max(1, Math.min(val, formData.total_trustees_n))
                    })
                  }}
                  disabled={submitting}
                  inputProps={{ min: 1, max: formData.total_trustees_n }}
                  helperText="Min trustees to decrypt"
                />
              </Tooltip>
            </Grid>
            <Grid item xs={6}>
              <Tooltip title="Total number of trustees. Must be >= threshold. More trustees = better redundancy.">
                <TextField
                  margin="dense"
                  label="Total Trustees (n)"
                  type="number"
                  fullWidth
                  required
                  value={formData.total_trustees_n}
                  onChange={(e) => {
                    const val = parseInt(e.target.value) || 1
                    setFormData({ 
                      ...formData, 
                      total_trustees_n: Math.max(formData.threshold_t, val)
                    })
                  }}
                  disabled={submitting}
                  inputProps={{ min: formData.threshold_t }}
                  helperText="Total trustee shares"
                />
              </Tooltip>
            </Grid>
          </Grid>

          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="caption">
              <strong>Example:</strong> If threshold = 5 and total = 9, any 5 out of 9 trustees can decrypt results.
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)} disabled={submitting}>
            Cancel
          </Button>
          <Button 
            onClick={handleCreate} 
            variant="contained" 
            disabled={submitting || !formData.title.trim() || !formData.start_time || !formData.end_time}
          >
            {submitting ? <CircularProgress size={24} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Election Dialog */}
      <Dialog open={openEditDialog} onClose={() => !submitting && setOpenEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Election</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Election Title"
            fullWidth
            required
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            disabled={submitting}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            disabled={submitting}
          />
          <TextField
            margin="dense"
            label="Start Time"
            type="datetime-local"
            fullWidth
            required
            InputLabelProps={{ shrink: true }}
            value={formData.start_time}
            onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
            disabled={submitting}
          />
          <TextField
            margin="dense"
            label="End Time"
            type="datetime-local"
            fullWidth
            required
            InputLabelProps={{ shrink: true }}
            value={formData.end_time}
            onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
            disabled={submitting}
          />
          
          <Box sx={{ mt: 2, mb: 1 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              🔐 Threshold Cryptography Settings
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
              Adjust trustee requirements. Make sure you have enough trustees added!
            </Typography>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Tooltip title="Minimum number of trustees needed to decrypt results. Lower = less secure but more fault-tolerant.">
                <TextField
                  margin="dense"
                  label="Threshold (t)"
                  type="number"
                  fullWidth
                  required
                  value={formData.threshold_t}
                  onChange={(e) => {
                    const val = parseInt(e.target.value) || 1
                    setFormData({ 
                      ...formData, 
                      threshold_t: Math.max(1, Math.min(val, formData.total_trustees_n))
                    })
                  }}
                  disabled={submitting}
                  inputProps={{ min: 1, max: formData.total_trustees_n }}
                  helperText="Min trustees to decrypt"
                />
              </Tooltip>
            </Grid>
            <Grid item xs={6}>
              <Tooltip title="Total number of trustees. Must be >= threshold. More trustees = better redundancy.">
                <TextField
                  margin="dense"
                  label="Total Trustees (n)"
                  type="number"
                  fullWidth
                  required
                  value={formData.total_trustees_n}
                  onChange={(e) => {
                    const val = parseInt(e.target.value) || 1
                    setFormData({ 
                      ...formData, 
                      total_trustees_n: Math.max(formData.threshold_t, val)
                    })
                  }}
                  disabled={submitting}
                  inputProps={{ min: formData.threshold_t }}
                  helperText="Total trustee shares"
                />
              </Tooltip>
            </Grid>
          </Grid>

          <Alert severity="warning" sx={{ mt: 2 }}>
            <Typography variant="caption">
              <strong>Warning:</strong> Make sure you have {formData.total_trustees_n} trustees added before initiating key ceremony!
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setOpenEditDialog(false)
            setEditingElection(null)
          }} disabled={submitting}>
            Cancel
          </Button>
          <Button 
            onClick={handleUpdate} 
            variant="contained" 
            disabled={submitting || !formData.title.trim() || !formData.start_time || !formData.end_time}
          >
            {submitting ? <CircularProgress size={24} /> : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
