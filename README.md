# Stock App with Supabase Authentication

A simple Streamlit application with Supabase authentication.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Supabase:**
   - Create a free account at [Supabase](https://supabase.com)
   - Create a new project
   - Go to Settings > API and copy your:
     - Project URL
     - Anon/Public key

3. **Set environment variables:**
   
   Create a `.env` file (or set in your terminal):
   ```bash
   export SUPABASE_URL="https://your-project.supabase.co"
   export SUPABASE_KEY="your-anon-key"
   ```

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## Features

- ✅ User registration (sign up)
- ✅ User login
- ✅ Session management
- ✅ Protected dashboard
- ✅ Data visualization
- ✅ Interactive components

## Usage

1. Sign up with your email and password
2. Check your email for verification (Supabase sends a confirmation)
3. Log in with your credentials
4. Access the protected dashboard

## Security Notes

- Never commit your `.env` file or expose your Supabase keys
- The anon key is safe for client-side use (with Row Level Security enabled)
- Consider enabling Row Level Security (RLS) in your Supabase project
