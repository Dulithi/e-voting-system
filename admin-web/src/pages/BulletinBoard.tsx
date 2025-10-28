import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Stack,
  Card,
  CardContent,
  Chip,
  Divider,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Refresh as RefreshIcon,
  VerifiedUser as VerifiedIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { bulletinApi } from '../services/api';

interface BulletinEntry {
  seq: number;
  type: string;
  hash: string;
  prev: string | null;
  data: any;
  time: string;
}

interface VerificationResult {
  valid: boolean;
  total_entries: number;
  message?: string;
}

const BulletinBoard: React.FC = () => {
  const { electionId } = useParams<{ electionId: string }>();
  const navigate = useNavigate();
  const [entries, setEntries] = useState<BulletinEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);

  const loadBulletinBoard = async () => {
    if (!electionId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await bulletinApi.get(`/bulletin/${electionId}/chain`);
      setEntries(response.data || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load bulletin board');
      console.error('Error loading bulletin board:', err);
    } finally {
      setLoading(false);
    }
  };

  const verifyChain = async () => {
    if (!electionId) return;
    
    setVerifying(true);
    setVerificationResult(null);
    
    try {
      const response = await bulletinApi.get(`/bulletin/${electionId}/verify`);
      setVerificationResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to verify chain');
      console.error('Error verifying chain:', err);
    } finally {
      setVerifying(false);
    }
  };

  useEffect(() => {
    loadBulletinBoard();
  }, [electionId]);

  const getEntryTypeColor = (type: string): "default" | "primary" | "secondary" | "success" | "error" | "info" | "warning" => {
    const typeMap: { [key: string]: "default" | "primary" | "secondary" | "success" | "error" | "info" | "warning" } = {
      'ELECTION_CREATED': 'primary',
      'KEY_GENERATED': 'info',
      'BALLOT_CAST': 'success',
      'ELECTION_CLOSED': 'warning',
      'TRUSTEE_SHARE': 'secondary',
      'RESULT_PUBLISHED': 'error'
    };
    return typeMap[type] || 'default';
  };

  const formatTimestamp = (timestamp: string): string => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        {/* Header */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
          <Box display="flex" alignItems="center" gap={2}>
            <IconButton onClick={() => navigate(`/elections/${electionId}`)}>
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="h4" component="h1">
              Bulletin Board
            </Typography>
          </Box>
          <Box display="flex" gap={1}>
            <Tooltip title="Refresh">
              <IconButton onClick={loadBulletinBoard} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Button
              variant="contained"
              color="primary"
              startIcon={<VerifiedIcon />}
              onClick={verifyChain}
              disabled={verifying || entries.length === 0}
            >
              {verifying ? 'Verifying...' : 'Verify Chain'}
            </Button>
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" mb={3}>
          Tamper-evident audit log of all election events. Each entry is cryptographically linked to the previous entry.
        </Typography>

        {/* Verification Result */}
        {verificationResult && (
          <Alert 
            severity={verificationResult.valid ? 'success' : 'error'}
            icon={verificationResult.valid ? <CheckCircleIcon /> : <WarningIcon />}
            sx={{ mb: 3 }}
          >
            <strong>{verificationResult.valid ? 'Chain Valid' : 'Chain Invalid'}</strong>
            <br />
            Total Entries: {verificationResult.total_entries}
            {verificationResult.message && (
              <>
                <br />
                {verificationResult.message}
              </>
            )}
          </Alert>
        )}

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Entries List */}
        {entries.length === 0 ? (
          <Box 
            display="flex" 
            flexDirection="column" 
            alignItems="center" 
            justifyContent="center" 
            minHeight="300px"
            sx={{ color: 'text.secondary' }}
          >
            <Typography variant="h6" gutterBottom>
              No entries yet
            </Typography>
            <Typography variant="body2">
              The bulletin board is empty. Entries will appear as election events occur.
            </Typography>
          </Box>
        ) : (
          <Stack spacing={2}>
            {entries.map((entry, index) => (
              <Card key={entry.seq} variant="outlined">
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Chip 
                        label={`#${entry.seq}`} 
                        size="small" 
                        color="default"
                      />
                      <Chip 
                        label={entry.type} 
                        size="small" 
                        color={getEntryTypeColor(entry.type)}
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      {formatTimestamp(entry.time)}
                    </Typography>
                  </Box>

                  <Divider sx={{ my: 1 }} />

                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                      Entry Hash
                    </Typography>
                    <Tooltip title={entry.hash}>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontFamily: 'monospace', 
                          wordBreak: 'break-all',
                          fontSize: '0.75rem'
                        }}
                      >
                        {entry.hash}
                      </Typography>
                    </Tooltip>
                  </Box>

                  {entry.prev && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                        Previous Hash
                      </Typography>
                      <Tooltip title={entry.prev}>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            fontFamily: 'monospace', 
                            wordBreak: 'break-all',
                            fontSize: '0.75rem',
                            color: 'text.secondary'
                          }}
                        >
                          {entry.prev}
                        </Typography>
                      </Tooltip>
                    </Box>
                  )}

                  {entry.data && Object.keys(entry.data).length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                        Entry Data
                      </Typography>
                      <Paper variant="outlined" sx={{ p: 1, backgroundColor: 'grey.50' }}>
                        <Typography 
                          variant="body2" 
                          component="pre"
                          sx={{ 
                            fontFamily: 'monospace',
                            fontSize: '0.75rem',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                            margin: 0
                          }}
                        >
                          {JSON.stringify(entry.data, null, 2)}
                        </Typography>
                      </Paper>
                    </Box>
                  )}

                  {index < entries.length - 1 && (
                    <Box 
                      display="flex" 
                      justifyContent="center" 
                      mt={2}
                      sx={{ color: 'primary.main' }}
                    >
                      <Typography variant="caption">⬇ Linked to next entry</Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            ))}
          </Stack>
        )}

        {/* Summary */}
        {entries.length > 0 && (
          <Box mt={3} p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="body2" color="text.secondary">
              <strong>Total Entries:</strong> {entries.length}
              {' • '}
              <strong>First Entry:</strong> {formatTimestamp(entries[0].time)}
              {' • '}
              <strong>Latest Entry:</strong> {formatTimestamp(entries[entries.length - 1].time)}
            </Typography>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default BulletinBoard;
