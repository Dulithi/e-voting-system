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
  IconButton,
  Tooltip,
  Card,
  CardContent,
} from '@mui/material'
import {
  ArrowBack,
  Refresh,
  Download,
  CheckCircle,
  Pending,
  ContentCopy,
} from '@mui/icons-material'
import { electionApi, codeSheetApi } from '../services/api'
import React from 'react'

interface VotingCode {
  code_id: string
  user_id: string
  user_email: string
  user_name: string
  main_voting_code: string
  candidate_codes: Record<string, string>
  code_sheet_generated: boolean
  main_code_used: boolean
  created_at: string
}

export default function VotingCodes() {
  const { electionId } = useParams<{ electionId: string }>()
  const navigate = useNavigate()
  const [codes, setCodes] = useState<VotingCode[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedCode, setSelectedCode] = useState<VotingCode | null>(null)
  const [copySuccess, setCopySuccess] = useState<string | null>(null)

  useEffect(() => {
    loadCodes()
  }, [electionId])

  const loadCodes = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await codeSheetApi.get(`/code-sheet/election/${electionId}`)
      setCodes(response.data)
    } catch (error: any) {
      console.error('Failed to load voting codes:', error)
      if (error.response?.status === 404) {
        // No codes generated yet
        setCodes([])
      } else {
        setError(error.response?.data?.detail || 'Failed to load voting codes')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateBulk = async () => {
    if (!confirm('Generate voting codes for all eligible voters? This cannot be undone.')) {
      return
    }

    try {
      setGenerating(true)
      setError(null)
      const response = await codeSheetApi.post('/code-sheet/generate-bulk', {
        election_id: electionId,
      })
      alert(`Successfully generated ${response.data.codes_generated} code sheets!`)
      await loadCodes()
    } catch (error: any) {
      console.error('Failed to generate codes:', error)
      setError(error.response?.data?.detail || 'Failed to generate voting codes')
    } finally {
      setGenerating(false)
    }
  }

  const handleCopyCode = (code: string, label: string) => {
    navigator.clipboard.writeText(code)
    setCopySuccess(`${label} copied!`)
    setTimeout(() => setCopySuccess(null), 2000)
  }

  const handleDownloadCodeSheet = (code: VotingCode) => {
    // Generate CSV for printing
    const candidateCodesStr = Object.entries(code.candidate_codes)
      .map(([id, c]) => `Candidate ${id}: ${c}`)
      .join('\\n')

    const content = `VOTING CODE SHEET
==================

Voter: ${code.user_name}
Email: ${code.user_email}

MAIN VOTING CODE:
${code.main_voting_code}

CANDIDATE VERIFICATION CODES:
${candidateCodesStr}

Generated: ${new Date(code.created_at).toLocaleString()}
==================
Keep this code sheet secure and confidential.
`

    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `voting-code-${code.user_email}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleDownloadAll = () => {
    if (codes.length === 0) {
      alert('No codes to download')
      return
    }

    // Generate CSV with all codes
    const csvHeader = 'Email,Name,Main Voting Code,Candidate Codes,Used,Generated\\n'
    const csvRows = codes.map(code => {
      const candidateCodes = JSON.stringify(code.candidate_codes).replace(/"/g, '""')
      return `"${code.user_email}","${code.user_name}","${code.main_voting_code}","${candidateCodes}","${code.main_code_used}","${new Date(code.created_at).toLocaleString()}"`
    }).join('\\n')

    const content = csvHeader + csvRows

    const blob = new Blob([content], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `voting-codes-election-${electionId}.csv`
    a.click()
    URL.revokeObjectURL(url)
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
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <IconButton onClick={() => navigate(-1)}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h4" flexGrow={1}>
          Voting Codes
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={loadCodes}
          disabled={loading}
        >
          Refresh
        </Button>
        {codes.length > 0 && (
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={handleDownloadAll}
          >
            Download All
          </Button>
        )}
        <Button
          variant="contained"
          onClick={handleGenerateBulk}
          disabled={generating}
        >
          {generating ? 'Generating...' : 'Generate Codes'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {copySuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {copySuccess}
        </Alert>
      )}

      {codes.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center" py={4}>
              No voting codes generated yet.
              <br />
              <br />
              Click "Generate Codes" to create voting codes for all eligible voters.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <>
          <Box mb={2}>
            <Alert severity="info">
              <Typography variant="body2">
                <strong>{codes.length} code sheets generated.</strong>
                {' '}
                {codes.filter(c => c.main_code_used).length} codes have been used.
              </Typography>
            </Alert>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Voter</strong></TableCell>
                  <TableCell><strong>Email</strong></TableCell>
                  <TableCell><strong>Main Code</strong></TableCell>
                  <TableCell><strong>Status</strong></TableCell>
                  <TableCell><strong>Generated</strong></TableCell>
                  <TableCell><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {codes.map((code) => (
                  <TableRow key={code.code_id} hover>
                    <TableCell>{code.user_name}</TableCell>
                    <TableCell>{code.user_email}</TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography
                          variant="body2"
                          fontFamily="monospace"
                          sx={{
                            maxWidth: 200,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                        >
                          {code.main_voting_code}
                        </Typography>
                        <IconButton
                          size="small"
                          onClick={() => handleCopyCode(code.main_voting_code, 'Main code')}
                        >
                          <ContentCopy fontSize="small" />
                        </IconButton>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={code.main_code_used ? 'Used' : 'Available'}
                        color={code.main_code_used ? 'success' : 'default'}
                        size="small"
                        icon={code.main_code_used ? <CheckCircle /> : <Pending />}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {new Date(code.created_at).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Tooltip title="View Details">
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => setSelectedCode(code)}
                          >
                            View
                          </Button>
                        </Tooltip>
                        <Tooltip title="Download Code Sheet">
                          <Button
                            size="small"
                            variant="outlined"
                            startIcon={<Download />}
                            onClick={() => handleDownloadCodeSheet(code)}
                          >
                            Download
                          </Button>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}

      {/* Code Details Dialog */}
      <Dialog
        open={!!selectedCode}
        onClose={() => setSelectedCode(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedCode && (
          <>
            <DialogTitle>
              Voting Code Details - {selectedCode.user_name}
            </DialogTitle>
            <DialogContent>
              <Box mb={2}>
                <Typography variant="subtitle2" color="text.secondary">
                  Email
                </Typography>
                <Typography variant="body1">{selectedCode.user_email}</Typography>
              </Box>

              <Box mb={2}>
                <Typography variant="subtitle2" color="text.secondary">
                  Main Voting Code
                </Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography
                    variant="body1"
                    fontFamily="monospace"
                    sx={{
                      bgcolor: 'grey.100',
                      p: 1,
                      borderRadius: 1,
                      flexGrow: 1,
                    }}
                  >
                    {selectedCode.main_voting_code}
                  </Typography>
                  <IconButton
                    onClick={() =>
                      handleCopyCode(selectedCode.main_voting_code, 'Main code')
                    }
                  >
                    <ContentCopy />
                  </IconButton>
                </Box>
              </Box>

              <Box mb={2}>
                <Typography variant="subtitle2" color="text.secondary" mb={1}>
                  Candidate Verification Codes
                </Typography>
                {Object.entries(selectedCode.candidate_codes).map(([candidateId, code]) => (
                  <Box
                    key={candidateId}
                    display="flex"
                    alignItems="center"
                    gap={1}
                    mb={1}
                  >
                    <Typography variant="body2" sx={{ minWidth: 120 }}>
                      Candidate {candidateId}:
                    </Typography>
                    <Typography
                      variant="body2"
                      fontFamily="monospace"
                      sx={{
                        bgcolor: 'grey.100',
                        p: 0.5,
                        px: 1,
                        borderRadius: 1,
                        flexGrow: 1,
                      }}
                    >
                      {code}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={() => handleCopyCode(code, `Candidate ${candidateId} code`)}
                    >
                      <ContentCopy fontSize="small" />
                    </IconButton>
                  </Box>
                ))}
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Status
                </Typography>
                <Chip
                  label={selectedCode.main_code_used ? 'Code Used' : 'Available'}
                  color={selectedCode.main_code_used ? 'success' : 'default'}
                  icon={selectedCode.main_code_used ? <CheckCircle /> : <Pending />}
                />
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedCode(null)}>Close</Button>
              <Button
                variant="contained"
                startIcon={<Download />}
                onClick={() => {
                  handleDownloadCodeSheet(selectedCode)
                  setSelectedCode(null)
                }}
              >
                Download Code Sheet
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  )
}
