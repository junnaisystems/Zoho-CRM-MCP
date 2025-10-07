# Zoho CRM MCP Server

<div align="center">

**🚀 Built by [JunnAI](https://junnaisystem.com) - Empowering AI-driven business automation**

[![Website](https://img.shields.io/badge/Website-junnaisystem.com-blue?style=flat-square)](https://junnaisystem.com)
[![GitHub](https://img.shields.io/badge/GitHub-junnaisystems-black?style=flat-square&logo=github)](https://github.com/junnaisystems)
[![Support](https://img.shields.io/badge/Support-contact%20us-green?style=flat-square)](https://junnaisystem.com/contact)

</div>

---

A comprehensive **Model Context Protocol (MCP) server** for seamless integration with Zoho CRM. This server enables AI assistants like Claude to interact with your Zoho CRM data through a secure, OAuth-based authentication system.

**Free & Open Source** - Built with ❤️ by the team at [JunnAI](https://junnaisystem.com)

## ✨ Features

- **🔐 Secure OAuth Authentication** - Full OAuth 2.0 flow with automatic token refresh
- **📊 Complete CRM Operations** - Create, read, update, delete records across all modules
- **🔍 Advanced Search** - Powerful search and filtering capabilities
- **📈 Analytics Support** - Access to user information and organization data
- **🔄 Bulk Operations** - Efficiently handle multiple records at once
- **🎯 Lead Conversion** - Convert leads to accounts, contacts, and deals
- **📱 Relationship Management** - Access related records across modules
- **⚡ Real-time Token Management** - Automatic token refresh and error handling
- **📝 Comprehensive Logging** - Detailed logging for debugging and monitoring

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Zoho CRM account with API access
- Claude Pro subscription (for AI integration)

### 1. Installation

#### Option A: Using pip (Recommended)
```bash
pip install -r requirements.txt
```

#### Option B: Using uv (Alternative)
```bash
# Install uv (if not already installed)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt
```

### 2. Zoho CRM Setup

#### Create a Zoho CRM Application

1. Go to [Zoho Developer Console](https://api-console.zoho.com/)
2. Click "Add Client"
3. Choose "Server-based Applications"
4. Fill in the details:
   - **Client Name**: Your application name
   - **Homepage URL**: Your website URL
   - **Authorized Redirect URIs**: `http://localhost:8080/callback`
5. Click "Create"
6. Note down your **Client ID** and **Client Secret**

#### Configure API Scopes

Make sure your application has the following scopes:
- `ZohoCRM.modules.ALL`
- `ZohoCRM.settings.ALL`
- `ZohoCRM.users.ALL`

### 3. Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your Zoho credentials:
```bash
# Zoho OAuth Configuration
ZOHO_CLIENT_ID=your_client_id_here
ZOHO_CLIENT_SECRET=your_client_secret_here
ZOHO_REDIRECT_URI=http://localhost:8080/callback
ZOHO_SCOPE=ZohoCRM.modules.ALL,ZohoCRM.settings.ALL,ZohoCRM.users.ALL

# Optional: Customize other settings
# ZOHO_API_DOMAIN=https://www.zohoapis.com
# ZOHO_ACCOUNTS_DOMAIN=https://accounts.zoho.com
# LOG_LEVEL=INFO
```

### 4. Using with AI Assistants

This MCP server is designed to work with AI assistants that support the Model Context Protocol (MCP).

#### For Warp Terminal Users:

Tell your AI assistant:

```
I have a Zoho CRM MCP server ready to use. Here are the details:

Path to MCP Server: /path/to/your/zoho-crm-mcp/src/server.py

Please use this MCP server to help me work with my Zoho CRM data. 
Start by running authenticate_zoho() to connect to my Zoho CRM account.
```

#### For Claude Desktop Users:

Add this to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "zoho-crm": {
      "command": "python",
      "args": ["/path/to/your/zoho-crm-mcp/src/server.py"],
      "env": {
        "ZOHO_CLIENT_ID": "your_client_id_here",
        "ZOHO_CLIENT_SECRET": "your_client_secret_here"
      }
    }
  }
}
```

#### First-Time Setup:

On first use, the server will:
1. Open your web browser for Zoho authentication
2. Redirect you to Zoho's login page
3. After successful login, redirect back to the server
4. Store authentication tokens securely for future use

### 5. Quick Reference - Available Tools

Once connected, your AI assistant can use these tools:

```
• authenticate_zoho() - Authenticate with Zoho CRM (opens browser)
• get_modules() - Get all available CRM modules  
• get_records(module_name, page, per_page) - Get records from modules
• search_records(module_name, criteria) - Search for specific records
• create_record(module_name, record_data) - Create new records
• update_record(module_name, record_id, record_data) - Update existing records
• get_record_by_id(module_name, record_id) - Get specific record by ID
• convert_lead(lead_id, convert_data) - Convert leads to accounts/contacts/deals
• get_organization_info() - Get organization details
• get_users() - Get CRM users information
• bulk_create_records(module_name, records_data) - Create multiple records
• get_related_records(module_name, record_id, related_module) - Get related records
• get_record_count(module_name, criteria) - Get record counts
```

## 📚 Available Tools

### Authentication Tools

- **`authenticate_zoho()`** - Authenticate with Zoho CRM (handles OAuth flow)
- **`revoke_authentication()`** - Revoke stored authentication tokens

### Module & Metadata Tools

- **`get_modules()`** - Get all available CRM modules
- **`get_module_fields(module_name)`** - Get field information for a specific module

### Record Management Tools

- **`get_records(module_name, page, per_page, sort_order, sort_by)`** - Get records from a module
- **`get_record_by_id(module_name, record_id)`** - Get a specific record by ID
- **`search_records(module_name, criteria, page, per_page)`** - Search records using criteria
- **`create_record(module_name, record_data, trigger_workflow)`** - Create a new record
- **`update_record(module_name, record_id, record_data, trigger_workflow)`** - Update an existing record
- **`delete_record(module_name, record_id)`** - Delete a record
- **`bulk_create_records(module_name, records_data, trigger_workflow)`** - Create multiple records

### Relationship Tools

- **`get_related_records(module_name, record_id, related_module, page, per_page)`** - Get related records

### Analytics & Info Tools

- **`get_organization_info()`** - Get organization information
- **`get_users(type_filter)`** - Get CRM users information
- **`get_record_count(module_name, criteria)`** - Get record count with optional filtering

### Utility Tools

- **`convert_lead(lead_id, convert_data)`** - Convert leads to accounts, contacts, and deals

## 💡 Usage Examples

### Example 1: Get All Leads
```python
# This will be called by the AI assistant
result = get_records("Leads", page=1, per_page=50)
print(f"Found {result['count']} leads")
```

### Example 2: Search for Contacts
```python
# Search for contacts with specific email
result = search_records("Contacts", "(Email:equals:john@example.com)")
```

### Example 3: Create a New Lead
```python
lead_data = {
    "First_Name": "John",
    "Last_Name": "Doe", 
    "Email": "john.doe@example.com",
    "Company": "Example Corp",
    "Phone": "+1234567890"
}
result = create_record("Leads", lead_data)
```

### Example 4: Convert a Lead
```python
convert_data = {
    "overwrite": False,
    "notify_lead_owner": True,
    "notify_new_entity_owner": True,
    "Accounts": {
        "Account_Name": "Example Corp"
    },
    "Deals": {
        "Deal_Name": "New Business Opportunity",
        "Amount": 50000
    }
}
result = convert_lead("lead_id_here", convert_data)
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ZOHO_CLIENT_ID` | - | **Required**: Your Zoho app client ID |
| `ZOHO_CLIENT_SECRET` | - | **Required**: Your Zoho app client secret |
| `ZOHO_REDIRECT_URI` | `http://localhost:8080/callback` | OAuth redirect URI |
| `ZOHO_SCOPE` | `ZohoCRM.modules.ALL,ZohoCRM.settings.ALL,ZohoCRM.users.ALL` | API permissions scope |
| `ZOHO_API_DOMAIN` | `https://www.zohoapis.com` | Zoho API base URL |
| `ZOHO_ACCOUNTS_DOMAIN` | `https://accounts.zoho.com` | Zoho accounts URL |
| `TOKEN_FILE_PATH` | `.zoho_tokens.json` | Path to store OAuth tokens |
| `LOG_LEVEL` | `INFO` | Logging level |
| `REQUEST_TIMEOUT` | `30` | API request timeout in seconds |
| `RATE_LIMIT` | `100` | Requests per minute limit |

## 🔒 Security Features

- **OAuth 2.0 Flow**: Secure authentication without exposing passwords
- **Token Auto-Refresh**: Automatically refreshes expired tokens
- **Secure Token Storage**: Tokens stored locally and encrypted
- **Rate Limiting**: Built-in protection against API abuse
- **Request Timeout**: Prevents hanging requests
- **Comprehensive Logging**: Track all API interactions

## 🐛 Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Check your `ZOHO_CLIENT_ID` and `ZOHO_CLIENT_SECRET`
   - Ensure redirect URI matches exactly: `http://localhost:8080/callback`
   - Verify your Zoho app has the required scopes

2. **"Token refresh failed"**
   - Delete `.zoho_tokens.json` and re-authenticate
   - Check if your Zoho app is still active

3. **"Module not found"**
   - Use `get_modules()` to see available modules
   - Check module name spelling (case-sensitive)

4. **"Permission denied"**
   - Verify your user has access to the requested module
   - Check if the module is enabled in your CRM

### Debug Mode

Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

This will show detailed API requests and responses.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🎆 About JunnAI

[**JunnAI**](https://junnaisystem.com) is a leading provider of AI-driven business automation solutions. We specialize in:

- 🤖 **AI Voice Agents** - Intelligent conversational AI for customer service
- 🔗 **CRM Integrations** - Seamless connections between AI and business systems  
- 📈 **Sales Automation** - AI-powered lead generation and conversion
- ⚙️ **Custom AI Solutions** - Tailored automation for your business needs

**Why choose JunnAI?**
- ✅ Proven expertise in AI and business automation
- ✅ Open-source contributions to the community
- ✅ Enterprise-grade solutions with dedicated support
- ✅ Cutting-edge technology stack

🚀 **Ready to transform your business with AI?** 
➡️ Visit [junnaisystem.com](https://junnaisystem.com) to learn more!

---

## 📞 Support

- **🌐 Website**: [junnaisystem.com](https://junnaisystem.com)
- **📧 Email**: [support@junnaisystem.com](mailto:support@junnaisystem.com)
- **🐛 Issues**: [Report bugs via GitHub Issues](https://github.com/junnaisystems/zoho-crm-mcp/issues)
- **📖 Documentation**: See this README and inline code documentation
- **💬 Contact**: [Get in touch](https://junnaisystem.com/contact)

## 🚦 Status

- ✅ OAuth Authentication
- ✅ Core CRUD Operations
- ✅ Advanced Search
- ✅ Bulk Operations
- ✅ Lead Conversion
- ✅ Relationship Management
- ✅ Error Handling
- ✅ Token Management
- 🔄 Enhanced Analytics (planned)
- 🔄 Webhook Support (planned)

---

**Made with ❤️ by [JunnAI](https://junnaisystem.com)** - [Empowering AI-driven business automation](https://junnaisystem.com)

🚀 **Explore more AI solutions at [junnaisystem.com](https://junnaisystem.com)**
