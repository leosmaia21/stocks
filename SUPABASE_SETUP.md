# Supabase Database Setup

## Create the user_api_keys table

Run this SQL in your Supabase SQL Editor:

```sql
-- Create table for storing user API keys
CREATE TABLE user_api_keys (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  trading_212_key_id TEXT,
  trading_212_secret TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
  UNIQUE(user_id)
);

-- Enable Row Level Security (RLS)
ALTER TABLE user_api_keys ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can only read their own API keys
CREATE POLICY "Users can read own api keys"
  ON user_api_keys
  FOR SELECT
  USING (auth.uid() = user_id);

-- Create policy: Users can insert their own API keys
CREATE POLICY "Users can insert own api keys"
  ON user_api_keys
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Create policy: Users can update their own API keys
CREATE POLICY "Users can update own api keys"
  ON user_api_keys
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Create policy: Users can delete their own API keys
CREATE POLICY "Users can delete own api keys"
  ON user_api_keys
  FOR DELETE
  USING (auth.uid() = user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = TIMEZONE('utc', NOW());
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_user_api_keys_updated_at 
  BEFORE UPDATE ON user_api_keys 
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();
```

## Security Features

1. **Row Level Security (RLS)**: Each user can only access their own API keys
2. **User Isolation**: Keys are tied to auth.users via foreign key
3. **Encrypted Storage**: Data is encrypted at rest in Supabase
4. **No .env exposure**: Keys never stored in environment files
5. **Session-based**: Keys loaded into session state, not passed around

## Usage

The app will automatically:
- Store your Trading 212 API key in Supabase when you save it
- Load it into session state on login
- Clear it on logout
- Never display the actual key in the UI (password field)
