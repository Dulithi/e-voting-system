import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

interface Candidate {
  candidate_id: string
  name: string
  party: string
  display_order: number
}

interface Election {
  election_id: string
  title: string
  description: string
  start_time: string
  end_time: string
  status: string
  candidates?: Candidate[]
}

interface ElectionState {
  elections: Election[]
  currentElection: Election | null
  loading: boolean
}

const initialState: ElectionState = {
  elections: [],
  currentElection: null,
  loading: false,
}

const electionSlice = createSlice({
  name: 'election',
  initialState,
  reducers: {
    setElections: (state, action: PayloadAction<Election[]>) => {
      state.elections = action.payload
    },
    setCurrentElection: (state, action: PayloadAction<Election>) => {
      state.currentElection = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
  },
})

export const { setElections, setCurrentElection, setLoading } = electionSlice.actions
export default electionSlice.reducer
