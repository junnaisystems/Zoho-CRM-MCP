# Fixing Zoho CRM App Configuration

Based on our debugging, your Zoho app credentials work with test codes but fail with real authorization codes. This suggests a configuration issue in your Zoho Developer Console.

## Step 1: Check Your Zoho App Configuration

1. **Go to Zoho Developer Console:**
   - Visit: https://api-console.zoho.com/
   - Sign in with your Zoho account

2. **Find Your App:**
   - Look for your app with Client ID: `1000.PR4ZRELLAMIVUOZ1U2AK3OW5FWM2GM`
   - Or create a new app if needed

## Step 2: Verify App Settings

Check these critical settings:

### **Redirect URI:**
- Must EXACTLY match: `http://localhost:8080/callback`
- No trailing slashes, exact case match
- Some apps require multiple redirect URIs to be added

### **Client Type:**
- Should be "Server-based Applications" or "Web-based Applications"
- NOT "Mobile Applications" or "Client-based Applications"

### **Scopes:**
- Ensure your app has the required scopes:
  - `ZohoCRM.modules.ALL`
  - `ZohoCRM.settings.ALL` 
  - `ZohoCRM.users.ALL`

## Step 3: Fix Common Issues

### **Issue 1: Incomplete Client Secret**
Your client secret (43 characters) seems shorter than typical Zoho secrets (64+ chars).

**Solution:**
1. In the Zoho Developer Console, go to your app
2. Go to "Client Secret" section
3. Click "Generate New Secret" or "Regenerate"
4. Copy the FULL secret (it should be much longer)
5. Update your `.env` file

### **Issue 2: Wrong Client Type**
If your app is set as "Client-based Application":

**Solution:**
1. Create a new "Server-based Application"
2. Configure it with the correct redirect URI
3. Use the new credentials

### **Issue 3: Domain Restrictions**
Your app might be restricted to specific domains.

**Solution:**
1. Check "Domain Settings" in your app
2. Ensure `localhost` is allowed or remove domain restrictions for development

## Step 4: Test New Credentials

After making changes:

1. Update your `.env` file with new credentials
2. Run: `python fast_auth.py`
3. The token exchange should now succeed

## Step 5: Create New App (If Needed)

If issues persist, create a completely new app:

1. **App Type:** Server-based Application
2. **Client Name:** "Zoho CRM MCP Server"  
3. **Homepage URL:** `http://localhost:8080`
4. **Authorized Redirect URIs:** 
   - `http://localhost:8080/callback`
5. **Scopes:** 
   - ZohoCRM.modules.ALL
   - ZohoCRM.settings.ALL
   - ZohoCRM.users.ALL

## Expected Result

After fixing the configuration, you should see:
```
📥 Response: {
  'access_token': 'your_access_token_here',
  'refresh_token': 'your_refresh_token_here',
  'api_domain': 'https://www.zohoapis.com',
  'token_type': 'Bearer',
  'expires_in': 3600
}
🎉 SUCCESS! Tokens saved to .zoho_tokens.json
```

## Need Help?

If you're still having issues:
1. Screenshot your Zoho app configuration
2. Check if your Zoho account has CRM access
3. Try creating a completely new Zoho app
4. Verify your Zoho account region (US/EU/IN/AU)

The key insight from our debugging is that your credentials are partially working (they pass initial validation) but fail when used with real authorization codes, which indicates a configuration mismatch in the Zoho app settings.