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
} from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'
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
}

export default function Elections() {
  const [elections, setElections] = useState<Election[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
  })
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
      setFormData({ title: '', description: '', start_time: '', end_time: '' })
      loadElections()
    } catch (error: any) {
      console.error('Failed to create election:', error)
      alert(error.response?.data?.detail || 'Failed to create election')
    } finally {
      setSubmitting(false)
    }
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
                onClick={() => navigate(`/elections/${election.election_id}`)}
              >
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                    <Typography variant="h6">{election.title}</Typography>
                    <Chip
                      label={election.status}
                      color={getStatusColor(election.status) as any}
                      size="small"
                    />
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
    </Box>
  )
}
