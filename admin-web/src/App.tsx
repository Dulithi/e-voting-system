import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import type { RootState } from './store/store'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Elections from './pages/Elections'
import ElectionDetails from './pages/ElectionDetails'
import Voters from './pages/Voters'
import Results from './pages/Results'
import VotingCodes from './pages/VotingCodes'
import Trustees from './pages/Trustees'
import BulletinBoard from './pages/BulletinBoard'
import Layout from './components/Layout'
import React from 'react'

function App() {
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated)

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route
        path="/"
        element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}
      >
        <Route index element={<Navigate to="/dashboard" />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="elections" element={<Elections />} />
        <Route path="elections/:id" element={<ElectionDetails />} />
        <Route path="elections/:electionId/codes" element={<VotingCodes />} />
        <Route path="elections/:electionId/trustees" element={<Trustees />} />
        <Route path="elections/:electionId/bulletin" element={<BulletinBoard />} />
        <Route path="voters" element={<Voters />} />
        <Route path="results/:electionId" element={<Results />} />
      </Route>
      
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default App
