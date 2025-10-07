"""
Zoho CRM MCP Server
A comprehensive Model Context Protocol server for Zoho CRM integration.
"""

import os
import json
import logging
import requests
from typing import Optional, Dict, Any, List, Union
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from datetime import datetime, timedelta
import asyncio
from functools import wraps

from zoho_auth import ZohoAuth

# Load environment variables
load_dotenv()

# Configure logging
log_file_path = os.getenv('LOG_FILE_PATH', 'logs/zoho_crm_mcp.log')
log_dir = os.path.dirname(log_file_path)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file_path)
    ]
)

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    name=os.getenv('MCP_SERVER_NAME', 'ZohoCRM')
)

# Global auth instance
auth: Optional[ZohoAuth] = None

def init_auth():
    """Initialize Zoho authentication."""
    global auth
    
    client_id = os.getenv('ZOHO_CLIENT_ID')
    client_secret = os.getenv('ZOHO_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError("ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET must be set in environment variables")
    
    auth = ZohoAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=os.getenv('ZOHO_REDIRECT_URI', 'http://localhost:8080/callback'),
        scope=os.getenv('ZOHO_SCOPE', 'ZohoCRM.modules.ALL,ZohoCRM.settings.ALL,ZohoCRM.users.ALL'),
        token_file_path=os.getenv('TOKEN_FILE_PATH', '.zoho_tokens.json'),
        api_domain=os.getenv('ZOHO_API_DOMAIN', 'https://www.zohoapis.com'),
        accounts_domain=os.getenv('ZOHO_ACCOUNTS_DOMAIN', 'https://accounts.zoho.com')
    )

def require_auth(func):
    """Decorator to ensure authentication before API calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not auth:
            init_auth()
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    
    return wrapper

def make_api_request(endpoint: str, method: str = 'GET', data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Make authenticated API request to Zoho CRM."""
    if not auth:
        raise Exception("Authentication not initialized")
    
    headers = auth.get_headers()
    api_domain = auth.get_api_domain()
    api_version = os.getenv('ZOHO_API_VERSION', 'v2')
    
    url = f"{api_domain}/crm/{api_version}/{endpoint}"
    
    timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, params=params, timeout=timeout)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, params=params, timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, params=params, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if response.status_code in [200, 201, 202]:
            return {
                'status': 'success',
                'status_code': response.status_code,
                'data': response.json()
            }
        else:
            return {
                'status': 'error',
                'status_code': response.status_code,
                'message': response.text,
                'error': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
    
    except requests.exceptions.Timeout:
        return {
            'status': 'error',
            'message': 'Request timed out',
            'error': 'timeout'
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'Request failed: {str(e)}',
            'error': str(e)
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Unexpected error: {str(e)}',
            'error': str(e)
        }

# Authentication Tools

@mcp.tool()
@require_auth
def authenticate_zoho(ctx) -> Dict[str, Any]:
    """
    Authenticate with Zoho CRM. This will open a browser window for OAuth if needed.
    
    Returns:
        Dict containing authentication status and user information
    """
    try:
        token = auth.get_valid_access_token()
        if not token:
            return {
                'status': 'error',
                'message': 'Authentication failed. Please check your credentials and try again.'
            }
        
        # Test the token by making a simple API call
        result = make_api_request('users?type=CurrentUser')
        
        if result['status'] == 'success':
            user_data = result['data'].get('users', [{}])[0]
            return {
                'status': 'success',
                'message': 'Successfully authenticated with Zoho CRM',
                'user': {
                    'name': user_data.get('full_name'),
                    'email': user_data.get('email'),
                    'role': user_data.get('role', {}).get('name'),
                    'organization': user_data.get('org', {}).get('company_name')
                }
            }
        else:
            return result
            
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return {
            'status': 'error',
            'message': f'Authentication error: {str(e)}'
        }

@mcp.tool()
@require_auth
def revoke_authentication(ctx) -> Dict[str, Any]:
    """
    Revoke Zoho CRM authentication and clear stored tokens.
    
    Returns:
        Dict containing revocation status
    """
    try:
        success = auth.revoke_tokens()
        if success:
            return {
                'status': 'success',
                'message': 'Authentication revoked successfully'
            }
        else:
            return {
                'status': 'error',
                'message': 'Failed to revoke authentication'
            }
    except Exception as e:
        logger.error(f"Token revocation error: {e}")
        return {
            'status': 'error',
            'message': f'Error revoking authentication: {str(e)}'
        }

# Module and Metadata Tools

@mcp.tool()
@require_auth
def get_modules(ctx) -> Dict[str, Any]:
    """
    Get all available modules in Zoho CRM.
    
    Returns:
        Dict containing list of available modules and their metadata
    """
    result = make_api_request('settings/modules')
    
    if result['status'] == 'success':
        modules = result['data'].get('modules', [])
        return {
            'status': 'success',
            'count': len(modules),
            'modules': [
                {
                    'api_name': module.get('api_name'),
                    'singular_label': module.get('singular_label'),
                    'plural_label': module.get('plural_label'),
                    'module_name': module.get('module_name'),
                    'creatable': module.get('creatable'),
                    'editable': module.get('editable'),
                    'deletable': module.get('deletable'),
                    'viewable': module.get('viewable')
                }
                for module in modules
            ]
        }
    
    return result

@mcp.tool()
@require_auth
def get_module_fields(ctx, module_name: str) -> Dict[str, Any]:
    """
    Get field information for a specific module.
    
    Args:
        module_name: Name of the module (e.g., 'Leads', 'Contacts', 'Deals')
    
    Returns:
        Dict containing field information for the module
    """
    result = make_api_request(f'settings/fields?module={module_name}')
    
    if result['status'] == 'success':
        fields = result['data'].get('fields', [])
        return {
            'status': 'success',
            'module': module_name,
            'count': len(fields),
            'fields': [
                {
                    'api_name': field.get('api_name'),
                    'field_label': field.get('field_label'),
                    'data_type': field.get('data_type'),
                    'required': field.get('required'),
                    'read_only': field.get('read_only'),
                    'visible': field.get('visible'),
                    'length': field.get('length'),
                    'pick_list_values': field.get('pick_list_values', []) if field.get('data_type') == 'picklist' else None
                }
                for field in fields
            ]
        }
    
    return result

# Record Management Tools

@mcp.tool()
@require_auth
def get_records(ctx, module_name: str, page: int = 1, per_page: int = 200, sort_order: str = 'desc', sort_by: str = 'Modified_Time') -> Dict[str, Any]:
    """
    Get records from a specific module.
    
    Args:
        module_name: Name of the module (e.g., 'Leads', 'Contacts', 'Deals')
        page: Page number (default: 1)
        per_page: Records per page (default: 200, max: 200)
        sort_order: Sort order 'asc' or 'desc' (default: 'desc')
        sort_by: Field to sort by (default: 'Modified_Time')
    
    Returns:
        Dict containing records from the module
    """
    params = {
        'page': page,
        'per_page': min(per_page, 200),
        'sort_order': sort_order,
        'sort_by': sort_by
    }
    
    result = make_api_request(module_name, params=params)
    
    if result['status'] == 'success':
        data = result['data']
        records = data.get('data', [])
        info = data.get('info', {})
        
        return {
            'status': 'success',
            'module': module_name,
            'count': len(records),
            'page_info': {
                'page': info.get('page', page),
                'per_page': info.get('per_page', per_page),
                'count': info.get('count', len(records)),
                'more_records': info.get('more_records', False)
            },
            'records': records
        }
    
    return result

@mcp.tool()
@require_auth
def get_record_by_id(ctx, module_name: str, record_id: str) -> Dict[str, Any]:
    """
    Get a specific record by its ID.
    
    Args:
        module_name: Name of the module (e.g., 'Leads', 'Contacts', 'Deals')
        record_id: ID of the record to retrieve
    
    Returns:
        Dict containing the record data
    """
    result = make_api_request(f'{module_name}/{record_id}')
    
    if result['status'] == 'success':
        records = result['data'].get('data', [])
        return {
            'status': 'success',
            'module': module_name,
            'record_id': record_id,
            'record': records[0] if records else None
        }
    
    return result

@mcp.tool()
@require_auth
def search_records(ctx, module_name: str, criteria: str, page: int = 1, per_page: int = 200) -> Dict[str, Any]:
    """
    Search for records in a specific module using criteria.
    
    Args:
        module_name: Name of the module (e.g., 'Leads', 'Contacts', 'Deals')
        criteria: Search criteria (e.g., '(Email:equals:john@example.com)')
        page: Page number (default: 1)
        per_page: Records per page (default: 200, max: 200)
    
    Returns:
        Dict containing matching records
    """
    params = {
        'criteria': criteria,
        'page': page,
        'per_page': min(per_page, 200)
    }
    
    result = make_api_request(f'{module_name}/search', params=params)
    
    if result['status'] == 'success':
        data = result['data']
        records = data.get('data', [])
        info = data.get('info', {})
        
        return {
            'status': 'success',
            'module': module_name,
            'criteria': criteria,
            'count': len(records),
            'page_info': {
                'page': info.get('page', page),
                'per_page': info.get('per_page', per_page),
                'count': info.get('count', len(records)),
                'more_records': info.get('more_records', False)
            },
            'records': records
        }
    
    return result

@mcp.tool()
@require_auth
def create_record(ctx, module_name: str, record_data: Dict[str, Any], trigger_workflow: bool = True) -> Dict[str, Any]:
    """
    Create a new record in a specific module.
    
    Args:
        module_name: Name of the module (e.g., 'Leads', 'Contacts', 'Deals')
        record_data: Dictionary containing the record fields and values
        trigger_workflow: Whether to trigger workflows (default: True)
    
    Returns:
        Dict containing the created record information
    """
    data = {'data': [record_data]}
    params = {}
    
    if not trigger_workflow:
        params['trigger'] = 'workflow'
    
    result = make_api_request(module_name, method='POST', data=data, params=params)
    
    if result['status'] == 'success':
        created_records = result['data'].get('data', [])
        return {
            'status': 'success',
            'module': module_name,
            'message': 'Record created successfully',
            'created_record': created_records[0] if created_records else None
        }
    
    return result

@mcp.tool()
@require_auth
def update_record(ctx, module_name: str, record_id: str, record_data: Dict[str, Any], trigger_workflow: bool = True) -> Dict[str, Any]:
    """
    Update an existing record in a specific module.
    
    Args:
        module_name: Name of the module (e.g., 'Leads', 'Contacts', 'Deals')
        record_id: ID of the record to update
        record_data: Dictionary containing the fields to update and their new values
        trigger_workflow: Whether to trigger workflows (default: True)
    
    Returns:
        Dict containing the update result
    """
    # Add the record ID to the data
    record_data['id'] = record_id
    
    data = {'data': [record_data]}
    params = {}
    
    if not trigger_workflow:
        params['trigger'] = 'workflow'
    
    result = make_api_request(f'{module_name}/{record_id}', method='PUT', data=data, params=params)
    
    if result['status'] == 'success':
        updated_records = result['data'].get('data', [])
        return {
            'status': 'success',
            'module': module_name,
            'record_id': record_id,
            'message': 'Record updated successfully',
            'updated_record': updated_records[0] if updated_records else None
        }
    
    return result

@mcp.tool()
@require_auth
def delete_record(ctx, module_name: str, record_id: str) -> Dict[str, Any]:
    """
    Delete a record from a specific module.
    
    Args:
        module_name: Name of the module (e.g., 'Leads', 'Contacts', 'Deals')
        record_id: ID of the record to delete
    
    Returns:
        Dict containing the deletion result
    """
    result = make_api_request(f'{module_name}/{record_id}', method='DELETE')
    
    if result['status'] == 'success':
        deleted_records = result['data'].get('data', [])
        return {
            'status': 'success',
            'module': module_name,
            'record_id': record_id,
            'message': 'Record deleted successfully',
            'deleted_record': deleted_records[0] if deleted_records else None
        }
    
    return result

@mcp.tool()
@require_auth
def bulk_create_records(ctx, module_name: str, records_data: List[Dict[str, Any]], trigger_workflow: bool = True) -> Dict[str, Any]:
    """
    Create multiple records in a specific module (bulk operation).
    
    Args:
        module_name: Name of the module (e.g., 'Leads', 'Contacts', 'Deals')
        records_data: List of dictionaries containing record data (max 100 records)
        trigger_workflow: Whether to trigger workflows (default: True)
    
    Returns:
        Dict containing the bulk creation results
    """
    if len(records_data) > 100:
        return {
            'status': 'error',
            'message': 'Maximum 100 records allowed per bulk operation'
        }
    
    data = {'data': records_data}
    params = {}
    
    if not trigger_workflow:
        params['trigger'] = 'workflow'
    
    result = make_api_request(module_name, method='POST', data=data, params=params)
    
    if result['status'] == 'success':
        created_records = result['data'].get('data', [])
        return {
            'status': 'success',
            'module': module_name,
            'message': f'{len(created_records)} records created successfully',
            'created_records': created_records
        }
    
    return result

# Relationship and Association Tools

@mcp.tool()
@require_auth
def get_related_records(ctx, module_name: str, record_id: str, related_module: str, page: int = 1, per_page: int = 200) -> Dict[str, Any]:
    """
    Get related records for a specific record.
    
    Args:
        module_name: Name of the parent module (e.g., 'Accounts')
        record_id: ID of the parent record
        related_module: Name of the related module (e.g., 'Contacts', 'Deals')
        page: Page number (default: 1)
        per_page: Records per page (default: 200, max: 200)
    
    Returns:
        Dict containing related records
    """
    params = {
        'page': page,
        'per_page': min(per_page, 200)
    }
    
    result = make_api_request(f'{module_name}/{record_id}/{related_module}', params=params)
    
    if result['status'] == 'success':
        data = result['data']
        records = data.get('data', [])
        info = data.get('info', {})
        
        return {
            'status': 'success',
            'module': module_name,
            'record_id': record_id,
            'related_module': related_module,
            'count': len(records),
            'page_info': {
                'page': info.get('page', page),
                'per_page': info.get('per_page', per_page),
                'count': info.get('count', len(records)),
                'more_records': info.get('more_records', False)
            },
            'related_records': records
        }
    
    return result

# Dashboard and Analytics Tools

@mcp.tool()
@require_auth
def get_organization_info(ctx) -> Dict[str, Any]:
    """
    Get information about the Zoho CRM organization.
    
    Returns:
        Dict containing organization information
    """
    result = make_api_request('org')
    
    if result['status'] == 'success':
        org_data = result['data'].get('org', [{}])[0]
        return {
            'status': 'success',
            'organization': {
                'company_name': org_data.get('company_name'),
                'org_id': org_data.get('id'),
                'primary_email': org_data.get('primary_email'),
                'website': org_data.get('website'),
                'phone': org_data.get('phone'),
                'country': org_data.get('country'),
                'time_zone': org_data.get('time_zone'),
                'currency': org_data.get('currency'),
                'mc_status': org_data.get('mc_status'),
                'gapps_enabled': org_data.get('gapps_enabled')
            }
        }
    
    return result

@mcp.tool()
@require_auth
def get_users(ctx, type_filter: str = 'AllUsers') -> Dict[str, Any]:
    """
    Get information about CRM users.
    
    Args:
        type_filter: Type of users to retrieve ('AllUsers', 'ActiveUsers', 'DeactiveUsers', 'ConfirmedUsers', 'NotConfirmedUsers', 'DeletedUsers', 'ActiveConfirmedUsers', 'AdminUsers', 'ActiveConfirmedAdmins')
    
    Returns:
        Dict containing user information
    """
    params = {'type': type_filter}
    result = make_api_request('users', params=params)
    
    if result['status'] == 'success':
        users = result['data'].get('users', [])
        return {
            'status': 'success',
            'type_filter': type_filter,
            'count': len(users),
            'users': [
                {
                    'id': user.get('id'),
                    'full_name': user.get('full_name'),
                    'email': user.get('email'),
                    'role': user.get('role', {}).get('name'),
                    'profile': user.get('profile', {}).get('name'),
                    'status': user.get('status'),
                    'created_time': user.get('created_time'),
                    'modified_time': user.get('modified_time')
                }
                for user in users
            ]
        }
    
    return result

# Utility Tools

@mcp.tool()
@require_auth
def convert_lead(ctx, lead_id: str, convert_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a lead to Account, Contact, and optionally Deal.
    
    Args:
        lead_id: ID of the lead to convert
        convert_data: Dictionary containing conversion data with keys:
                     - overwrite: boolean (optional)
                     - notify_lead_owner: boolean (optional) 
                     - notify_new_entity_owner: boolean (optional)
                     - Accounts: dict with account data (optional)
                     - Contacts: dict with contact data (optional)
                     - Deals: dict with deal data (optional)
    
    Returns:
        Dict containing the conversion result
    """
    data = {'data': [convert_data]}
    
    result = make_api_request(f'Leads/{lead_id}/actions/convert', method='POST', data=data)
    
    if result['status'] == 'success':
        conversion_data = result['data'].get('data', [{}])[0]
        return {
            'status': 'success',
            'lead_id': lead_id,
            'message': 'Lead converted successfully',
            'conversion_result': conversion_data
        }
    
    return result

@mcp.tool() 
@require_auth
def get_record_count(ctx, module_name: str, criteria: str = None) -> Dict[str, Any]:
    """
    Get the count of records in a module, optionally with search criteria.
    
    Args:
        module_name: Name of the module (e.g., 'Leads', 'Contacts', 'Deals')
        criteria: Optional search criteria to filter records
    
    Returns:
        Dict containing the record count
    """
    endpoint = f'{module_name}/actions/count'
    params = {}
    
    if criteria:
        params['criteria'] = criteria
    
    result = make_api_request(endpoint, params=params)
    
    if result['status'] == 'success':
        count_data = result['data']
        return {
            'status': 'success',
            'module': module_name,
            'criteria': criteria,
            'count': count_data.get('count', 0)
        }
    
    return result

# Initialize authentication on import
try:
    init_auth()
    logger.info("Zoho CRM MCP Server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize auth: {e}")
    logger.info("Authentication will be initialized on first tool call")

if __name__ == "__main__":
    mcp.run()