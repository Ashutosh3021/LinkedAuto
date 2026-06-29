# Deploy to Render

This guide will help you deploy your LinkedIn Automation app to Render, a cloud platform for hosting web apps and databases.

## Prerequisites

1. A GitHub account
2. A Render account (sign up at [render.com](https://render.com))
3. Your OpenRouter API key
4. LinkedIn Developer Account credentials (Client ID and Client Secret)

## Quick Deploy (1-Click)

The easiest way to deploy is using Render Blueprint:

1. Click the button below to deploy:
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
2. Follow the prompts to connect your GitHub repo
3. Wait for the deployment to finish

## Manual Deployment Steps

If you prefer to deploy manually, follow these steps:

### 1. Prepare your Code

Make sure you have the following files in your project root:
- `Procfile`: Tells Render how to start your app
- `requirements.txt`: Lists all dependencies
- `render.yaml`: Optional (for Blueprint deployments)

### 2. Create a New Web Service on Render

1. Log in to your Render account
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository and select your LinkedIn Automation repo
4. Configure your web service:
   - **Name**: `linkedin-automation` (or whatever you prefer)
   - **Environment**: `Python`
   - **Region**: Choose the one closest to you
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave blank
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Choose **Free** (for testing)

### 3. Add a Database

1. Click **"New"** → **"PostgreSQL"**
2. Name it `linkedin-automation-db`
3. Choose **Free** instance type
4. Click **"Create Database"**

### 4. Configure Environment Variables

1. Go to your Web Service → **"Environment"**
2. Add the following environment variables:

| Key                          | Value                                                                 |
|------------------------------|-----------------------------------------------------------------------|
| `SECRET_KEY`                 | Click "Generate" to create a secure random key                        |
| `DEBUG`                      | `False`                                                               |
| `OPENROUTER_API_KEY`         | Your OpenRouter API key (from openrouter.ai)                          |
| `OPENROUTER_MODEL`           | (Optional) Default: `openai/gpt-4o-mini`                              |
| `LINKEDIN_CLIENT_ID`         | Your LinkedIn Client ID (from LinkedIn Developer Portal)              |
| `LINKEDIN_CLIENT_SECRET`     | Your LinkedIn Client Secret (from LinkedIn Developer Portal)          |
| `LINKEDIN_REDIRECT_URI`      | `https://your-render-app-url.onrender.com/linkedin/callback`          |

> **Important**: Replace `your-render-app-url` with the actual URL of your deployed Render app!

### 5. Deploy!

1. Click **"Save Changes"** to start the deployment
2. Wait for Render to build and deploy your app (this may take a few minutes)
3. Once deployed, you'll see your app's URL at the top of the page

## Configure LinkedIn OAuth

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Select your app
3. Go to **"Auth"** → **"OAuth 2.0 Settings"**
4. Add your Render app's callback URL to **"Authorized Redirect URLs"**:
   - Example: `https://your-app-name.onrender.com/linkedin/callback`
5. Save your changes

## Test Your Deployment

1. Open your Render app's URL in a browser
2. Go to **Settings** → **Connect LinkedIn**
3. Complete the OAuth flow
4. Try generating a post to verify everything works!

## Optional: Custom Domain

1. In Render, go to your Web Service → **"Custom Domains"**
2. Click **"Add Custom Domain"**
3. Follow the instructions to configure your domain's DNS settings

## Updating Your App

To deploy changes:
1. Commit and push your code to GitHub
2. Render will automatically detect the change and redeploy your app
3. You can also trigger a manual deployment from Render's dashboard

## Troubleshooting

- **Build fails**: Check the build logs in Render for errors
- **Database errors**: Make sure your `DATABASE_URL` environment variable is correctly set
- **LinkedIn OAuth issues**: Verify your `LINKEDIN_REDIRECT_URI` matches exactly what's in LinkedIn Developer Portal
- **Scheduler not running**: Check the app logs to ensure APScheduler is starting properly

## Security Notes

- Never commit your `.env` file or secrets to GitHub!
- Use Render's environment variables to store all sensitive information
- Regularly rotate your API keys and secrets
- Consider using a paid Render plan for production apps (better performance and reliability)
