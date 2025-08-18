# 🚀 Streamlit Cloud Deployment Guide

## Quick Fix for Requirements Error

If you're getting a requirements installation error on Streamlit Cloud, follow these steps:

### Step 1: Update Requirements for Cloud Compatibility

The issue is likely the `win10toast` package which is Windows-specific. I've already fixed this:

1. **Updated requirements.txt** - Now includes platform-specific conditions
2. **Created requirements-streamlit.txt** - Cloud-compatible version

### Step 2: Deploy to Streamlit Cloud

**Option A: Use the updated requirements.txt (Recommended)**
- The main `requirements.txt` now includes: `win10toast>=0.9; sys_platform == "win32"`
- This will automatically skip Windows-specific packages on Linux (Streamlit Cloud)

**Option B: Use the cloud-specific requirements file**
- Rename `requirements-streamlit.txt` to `requirements.txt` before deploying
- This version excludes all Windows-specific packages

### Step 3: Streamlit Cloud Deployment Steps

1. **Push the latest changes** (already done ✅)
   ```bash
   git push origin main
   ```

2. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with GitHub

3. **Deploy your app**
   - Click "New app"
   - Repository: `nwinnie450/BCResearch_Update`
   - Branch: `main`
   - Main file path: `app.py`

4. **Wait for deployment**
   - The app will automatically install requirements
   - Should work without the Windows notification error

### Step 4: Expected Behavior on Cloud

**✅ Will Work:**
- All core blockchain research features
- Real-time data fetching
- Email notifications
- Slack notifications
- Schedule management UI
- Chat interface
- Analytics and comparisons

**❌ Won't Work (Expected):**
- Desktop notifications (Windows-specific)
- Background scheduling (Streamlit Cloud limitation)

**💡 Cloud Alternative:**
- Use email/Slack notifications instead of desktop
- Manual data refresh instead of background scheduling

### Step 5: Environment Variables (Optional)

If you want to use premium APIs on Streamlit Cloud:

1. **In Streamlit Cloud Settings** add:
   ```
   COINGECKO_API_KEY=your_key_here
   ETHERSCAN_API_KEY=your_key_here
   BSCSCAN_API_KEY=your_key_here
   MORALIS_API_KEY=your_key_here
   ```

2. **Email Configuration** (if desired):
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password
   RECIPIENT_EMAIL=notifications@yourcompany.com
   ```

### Step 6: Troubleshooting

**If deployment still fails:**

1. **Check the logs** in Streamlit Cloud console
2. **Try Option B** (use requirements-streamlit.txt)
3. **Remove problematic packages** one by one:
   ```txt
   # Comment out potentially problematic lines:
   # apscheduler>=3.10.4
   # croniter>=1.4.1
   ```

### Step 7: Post-Deployment Verification

Once deployed successfully:

1. **Test the main features:**
   - ✅ Chat interface works
   - ✅ Real-time data displays
   - ✅ Schedule management shows up
   - ✅ Slack configuration available

2. **Expected limitations:**
   - Desktop notifications: "Not available on this platform"
   - Scheduler: May show as "Not running" (normal for cloud)

## 📱 Mobile-Friendly Deployment

The app is already mobile-responsive and will work great on:
- ✅ Desktop browsers
- ✅ Mobile phones
- ✅ Tablets

## 🔗 Share Your App

Once deployed, you'll get a URL like:
`https://your-app-name.streamlit.app`

Share this with your team for blockchain research collaboration!

## 🛟 Need Help?

If you still encounter issues:

1. **Check this commit** for the latest fixes: https://github.com/nwinnie450/BCResearch_Update/commit/7ac031d
2. **View the requirements fix**: The `win10toast` package is now platform-conditional
3. **Contact support**: Streamlit Cloud support or GitHub issues

Your blockchain research agent should now deploy successfully! 🎉