import { Box, Typography, Paper, CircularProgress, Alert, Card, CardContent, Grid, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material'
import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { electionApi } from '../services/api'
import { IconButton } from '@mui/material'
import { ArrowBack } from '@mui/icons-material'

interface ResultData {
  candidate_id: string
  candidate_name: string
  vote_count: number
  percentage: number
  verified: boolean
  tallied_at: string | null
}

interface ElectionResults {
  election_id: string
  election_title: string
  status: string
  results: ResultData[]
  total_votes: number
}

export default function Results() {
  const { electionId } = useParams<{ electionId: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [resultsData, setResultsData] = useState<ElectionResults | null>(null)

  useEffect(() => {
    if (electionId) {
      loadResults()
    }
  }, [electionId])

  const loadResults = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await electionApi.get(`/election/${electionId}/results`)
      setResultsData(response.data)
    } catch (error: any) {
      console.error('Failed to load results:', error)
      setError(error.response?.data?.detail || 'Failed to load election results')
    } finally {
      setLoading(false)
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
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Box>
    )
  }

  if (!resultsData) {
    return (
      <Box>
        <Alert severity="info">No election results available</Alert>
      </Box>
    )
  }

  const winner = resultsData.results.length > 0 ? resultsData.results[0] : null

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <IconButton onClick={() => navigate(-1)}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h4">
          Election Results
        </Typography>
      </Box>

      {/* Election Info */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                {resultsData.election_title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Election ID: {resultsData.election_id}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                Status
              </Typography>
              <Chip 
                label={resultsData.status} 
                color="primary" 
                sx={{ mt: 1 }} 
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                Total Votes Cast
              </Typography>
              <Typography variant="h4" sx={{ mt: 1 }}>
                {resultsData.total_votes}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Winner Card */}
      {winner && winner.vote_count > 0 && (
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="h6">
            🏆 Winner: {winner.candidate_name}
          </Typography>
          <Typography variant="body2">
            Votes: {winner.vote_count} ({winner.percentage.toFixed(2)}%)
          </Typography>
        </Alert>
      )}

      {/* Results Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Rank</strong></TableCell>
              <TableCell><strong>Candidate Name</strong></TableCell>
              <TableCell align="right"><strong>Votes</strong></TableCell>
              <TableCell align="right"><strong>Percentage</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {resultsData.results.map((result, index) => (
              <TableRow key={result.candidate_id} hover>
                <TableCell>
                  <Chip 
                    label={`#${index + 1}`} 
                    size="small"
                    color={index === 0 ? 'success' : 'default'}
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body1" fontWeight={index === 0 ? 'bold' : 'normal'}>
                    {result.candidate_name}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="h6" color={index === 0 ? 'success.main' : 'text.primary'}>
                    {result.vote_count}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body1">
                    {result.percentage.toFixed(2)}%
                  </Typography>
                </TableCell>
                <TableCell>
                  {result.verified ? (
                    <Chip label="Verified" color="success" size="small" />
                  ) : (
                    <Chip label="Pending" size="small" />
                  )}
                </TableCell>
              </TableRow>
            ))}
            {resultsData.results.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <Typography variant="body2" color="text.secondary" py={3}>
                    No votes were cast in this election
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Verification Info */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>Verification:</strong> These results were decrypted using threshold cryptography 
          with decryption shares from multiple trustees. The results are cryptographically verified 
          and tamper-proof.
        </Typography>
      </Alert>
    </Box>
  )
}
