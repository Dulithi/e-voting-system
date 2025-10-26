import { Box, Typography, Paper } from '@mui/material'
import React from 'react'

export default function Results() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Results
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          Results dashboard will show tallied election results with audit trails.
        </Typography>
      </Paper>
    </Box>
  )
}
