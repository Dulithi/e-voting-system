-- Migration: Remove status column from trustees table
-- Date: October 28, 2025
-- Description: Simplifies trustee management by removing the status field.
--              Admin directly adds trustees who are ready to participate.

-- Remove the status column from trustees table
ALTER TABLE trustees DROP COLUMN IF EXISTS status;

-- Remove the accept_invitation related functionality is handled at API level
-- No database changes needed for that

-- Verification query to check the change
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'trustees' 
ORDER BY ordinal_position;
