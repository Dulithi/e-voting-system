import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  List,
  ListItem,
  ListItemText,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  CircularProgress,
  Alert,
} from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'
import { electionApi } from '../services/api'
import React from 'react'

interface Candidate {
  candidate_id: string
  name: string
  party: string | null
  display_order: number
}

interface Election {
  election_id: string
  title: string
  description: string | null
  start_time: string
  end_time: string
  status: string
  threshold_t: number
  total_trustees_n: number
  candidates: Candidate[]
}

export default function ElectionDetails() {
  const { id } = useParams()
  const [election, setElection] = useState<Election | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [candidateForm, setCandidateForm] = useState({
    name: '',
    party: '',
  })

  useEffect(() => {
    loadElection()
  }, [id])

  const loadElection = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await electionApi.get(`/election/${id}`)
      setElection(response.data)
    } catch (error: any) {
      console.error('Failed to load election:', error)
      setError(error.response?.data?.detail || 'Failed to load election')
    } finally {
      setLoading(false)
    }
  }

  const handleAddCandidate = async () => {
    try {
      await electionApi.post('/election/candidate/add', {
        election_id: id,
        name: candidateForm.name,
        party: candidateForm.party || null,
      })
      setOpenDialog(false)
      setCandidateForm({ name: '', party: '' })
      loadElection()
    } catch (error) {
      console.error('Failed to add candidate:', error)
      alert('Failed to add candidate')
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error">{error}</Alert>
      </Box>
    )
  }

  if (!election) {
    return (
      <Box>
        <Alert severity="warning">Election not found</Alert>
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {election.title}
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        {election.description || 'No description provided'}
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Candidates</Typography>
              <Button
                size="small"
                startIcon={<AddIcon />}
                onClick={() => setOpenDialog(true)}
                variant="contained"
              >
                Add Candidate
              </Button>
            </Box>
            <Divider sx={{ mb: 2 }} />
            {election.candidates && election.candidates.length > 0 ? (
              <List>
                {election.candidates.map((candidate) => (
                  <ListItem key={candidate.candidate_id}>
                    <ListItemText
                      primary={candidate.name}
                      secondary={`Party: ${candidate.party || 'Independent'} | Order: ${candidate.display_order}`}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No candidates added yet
              </Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Election Details
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body2" gutterBottom>
              <strong>Status:</strong> {election.status}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Start:</strong> {new Date(election.start_time).toLocaleString()}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>End:</strong> {new Date(election.end_time).toLocaleString()}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Threshold (t):</strong> {election.threshold_t}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Total Trustees (n):</strong> {election.total_trustees_n}
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Add Candidate</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Candidate Name"
            fullWidth
            required
            value={candidateForm.name}
            onChange={(e) => setCandidateForm({ ...candidateForm, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Party (Optional)"
            fullWidth
            value={candidateForm.party}
            onChange={(e) => setCandidateForm({ ...candidateForm, party: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleAddCandidate} 
            variant="contained"
            disabled={!candidateForm.name.trim()}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
