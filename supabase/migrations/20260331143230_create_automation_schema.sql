/*
  # Create Automation Operations Schema

  1. New Tables
    - `automation_operations`
      - `id` (uuid, primary key)
      - `user_id` (uuid, references auth.users)
      - `name` (text, operation name)
      - `description` (text, operation description)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
    
    - `operation_actions`
      - `id` (uuid, primary key)
      - `operation_id` (uuid, references automation_operations)
      - `order` (integer, action sequence)
      - `action_type` (text: 'click', 'type', 'wait', 'screenshot')
      - `config` (jsonb, action-specific configuration)
      - `created_at` (timestamp)
    
    - `execution_logs`
      - `id` (uuid, primary key)
      - `operation_id` (uuid, references automation_operations)
      - `user_id` (uuid, references auth.users)
      - `batch_item` (text, the search term or item processed)
      - `status` (text: 'pending', 'running', 'success', 'error')
      - `error_message` (text, if error occurred)
      - `started_at` (timestamp)
      - `completed_at` (timestamp)

  2. Security
    - Enable RLS on all tables
    - Users can only access their own operations and logs
*/

CREATE TABLE IF NOT EXISTS automation_operations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id),
  name text NOT NULL,
  description text DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE automation_operations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own operations"
  ON automation_operations FOR ALL
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE TABLE IF NOT EXISTS operation_actions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  operation_id uuid NOT NULL REFERENCES automation_operations(id) ON DELETE CASCADE,
  "order" integer NOT NULL,
  action_type text NOT NULL CHECK (action_type IN ('click', 'type', 'wait', 'screenshot')),
  config jsonb NOT NULL,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE operation_actions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage actions in their operations"
  ON operation_actions FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM automation_operations
      WHERE automation_operations.id = operation_actions.operation_id
      AND automation_operations.user_id = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM automation_operations
      WHERE automation_operations.id = operation_actions.operation_id
      AND automation_operations.user_id = auth.uid()
    )
  );

CREATE TABLE IF NOT EXISTS execution_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  operation_id uuid NOT NULL REFERENCES automation_operations(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES auth.users(id),
  batch_item text NOT NULL,
  status text NOT NULL CHECK (status IN ('pending', 'running', 'success', 'error')),
  error_message text DEFAULT '',
  started_at timestamptz DEFAULT now(),
  completed_at timestamptz
);

ALTER TABLE execution_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their execution logs"
  ON execution_logs FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create execution logs for their operations"
  ON execution_logs FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their execution logs"
  ON execution_logs FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS idx_automation_operations_user_id ON automation_operations(user_id);
CREATE INDEX IF NOT EXISTS idx_operation_actions_operation_id ON operation_actions(operation_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_user_id ON execution_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_operation_id ON execution_logs(operation_id);
