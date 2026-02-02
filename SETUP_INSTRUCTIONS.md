# Setup Instructions

## 1. Database Setup

Trading 212 uses **two-part authentication** (Key ID + Secret). You need to update your Supabase database:

### Option A: New Installation

Run the SQL from [SUPABASE_SETUP.md](SUPABASE_SETUP.md) in your Supabase SQL Editor. It already includes the correct schema.

### Option B: Existing Installation (Migration)

If you already have a `user_api_keys` table with the old `trading_212_key` column, run this migration:

```sql
-- Add new columns for Key ID and Secret
ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS trading_212_key_id TEXT;
ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS trading_212_secret TEXT;

-- Optional: Remove old column if it exists
-- ALTER TABLE user_api_keys DROP COLUMN IF EXISTS trading_212_key;
```

## 2. How to Get Trading 212 API Credentials

1. Log in to your Trading 212 account
2. Go to **Settings → API (Beta)**
3. Generate a new API key
4. You'll receive:
   - **API Key ID** (similar to a username)
   - **API Secret** (similar to a password)
5. Keep both values - you'll need to enter them in the app

## 3. App Configuration

1. Enter your API credentials in the app:
   - Open the Trading 212 page
   - Click on "Settings" expander
   - Choose environment:
     - **Demo**: For testing (uses demo.trading212.com)
     - **Live**: For real trading (uses live.trading212.com)
   - Enter your Key ID and Secret
   - Click "Save Credentials"

2. The credentials are:
   - Stored securely in Supabase with Row Level Security (RLS)
   - Never exposed in the UI (password fields)
   - Automatically loaded on login

## 4. Troubleshooting

### Error 401 (Authentication Failed)

This usually means:
- Incorrect Key ID or Secret
- Wrong environment selected (demo vs live)
- API credentials expired/revoked

**Solution**: 
1. Check your Trading 212 API settings
2. Generate new credentials if needed
3. Verify you're using the correct environment
4. Re-enter the credentials in the app

### No portfolio data showing

Make sure:
- You've saved your credentials in Settings
- You selected the correct environment (demo/live)
- Your Trading 212 account has positions
- The API is enabled in your Trading 212 account

## 5. Security Notes

✅ **What's secure:**
- API credentials stored in Supabase (encrypted at rest)
- Row Level Security (RLS) - users can only see their own keys
- No credentials in `.env` files or source code
- Password-masked input fields

⚠️ **Important:**
- Never share your API credentials
- Use demo environment for testing
- Regularly rotate your API keys
- Revoke keys immediately if compromised
