#!/usr/bin/env python3
"""
Standalone Zoho CRM Connection Test
This script tests the Zoho CRM authentication and API connectivity independently.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from zoho_auth import ZohoAuth
import requests
import json

def main():
    """Test Zoho CRM connection."""
    print("="*60)
    print("    Zoho CRM Connection Test")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    client_id = os.getenv('ZOHO_CLIENT_ID')
    client_secret = os.getenv('ZOHO_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Error: ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET must be set in .env file")
        print("Please copy .env.example to .env and configure your credentials.")
        return False
    
    if client_id == "your_client_id_here" or client_secret == "your_client_secret_here":
        print("❌ Error: Please replace placeholder values in .env with your actual credentials")
        return False
    
    print(f"✓ Found Client ID: {client_id[:10]}...")
    print(f"✓ Found Client Secret: {client_secret[:10]}...")
    print()
    
    try:
        # Initialize auth handler
        print("📡 Initializing Zoho authentication...")
        auth = ZohoAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=os.getenv('ZOHO_REDIRECT_URI', 'http://localhost:8080/callback'),
            scope=os.getenv('ZOHO_SCOPE', 'ZohoCRM.modules.ALL,ZohoCRM.settings.ALL,ZohoCRM.users.ALL'),
            token_file_path=os.getenv('TOKEN_FILE_PATH', '.zoho_tokens.json')
        )
        
        # Check if we have valid tokens
        print("🔑 Checking for existing valid tokens...")
        token = auth.get_valid_access_token()
        
        if not token:
            print("❌ No valid access token available")
            return False
        
        print("✓ Valid access token obtained!")
        print()
        
        # Test API connectivity
        print("🧪 Testing Zoho CRM API connectivity...")
        
        # Test 1: Get current user info
        headers = auth.get_headers()
        api_domain = auth.get_api_domain()
        
        print("   Testing user information endpoint...")
        user_url = f"{api_domain}/crm/v2/users?type=CurrentUser"
        
        response = requests.get(user_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            user_data = response.json()
            if 'users' in user_data and user_data['users']:
                user = user_data['users'][0]
                print(f"   ✓ Connected as: {user.get('full_name', 'Unknown')}")
                print(f"   ✓ Email: {user.get('email', 'Unknown')}")
                print(f"   ✓ Role: {user.get('role', {}).get('name', 'Unknown')}")
            else:
                print("   ⚠ Unexpected user data format")
        else:
            print(f"   ❌ User info failed: {response.status_code} - {response.text}")
            return False
        
        print()
        
        # Test 2: Get modules
        print("   Testing modules endpoint...")
        modules_url = f"{api_domain}/crm/v2/settings/modules"
        
        response = requests.get(modules_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            modules_data = response.json()
            if 'modules' in modules_data:
                modules = modules_data['modules']
                print(f"   ✓ Found {len(modules)} CRM modules")
                
                # Show first few modules
                for i, module in enumerate(modules[:5]):
                    print(f"     - {module.get('module_name', 'Unknown')}")
                
                if len(modules) > 5:
                    print(f"     ... and {len(modules) - 5} more")
            else:
                print("   ⚠ Unexpected modules data format")
        else:
            print(f"   ❌ Modules test failed: {response.status_code} - {response.text}")
            return False
        
        print()
        
        # Test 3: Get organization info
        print("   Testing organization endpoint...")
        org_url = f"{api_domain}/crm/v2/org"
        
        response = requests.get(org_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            org_data = response.json()
            if 'org' in org_data and org_data['org']:
                org = org_data['org'][0]
                print(f"   ✓ Organization: {org.get('company_name', 'Unknown')}")
                print(f"   ✓ Country: {org.get('country', 'Unknown')}")
                print(f"   ✓ Time Zone: {org.get('time_zone', 'Unknown')}")
            else:
                print("   ⚠ Unexpected organization data format")
        else:
            print(f"   ❌ Organization test failed: {response.status_code} - {response.text}")
            return False
        
        print()
        print("="*60)
        print("🎉 SUCCESS! Zoho CRM connection is working perfectly!")
        print("✓ Authentication: Working")
        print("✓ Token management: Working") 
        print("✓ API connectivity: Working")
        print("✓ User access: Confirmed")
        print("✓ Module access: Confirmed")
        print("✓ Organization access: Confirmed")
        print()
        print("Your MCP server is ready to use with AI assistants!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        import traceback
        print("\nDetailed error:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)