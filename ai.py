import xmlrpc.client
import openai

# --- CONFIGURATION ---
URL = "https://qcoffee.odoo.com"
DB = "qcoffee"
USER_EMAIL = "tharcisse@questioncoffee.com"
API_KEY = "06eba304b4c684be9079e54b4c31b4cc0c9ce3db"
openai.api_key = "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"

def get_odoo_connection():
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USER_EMAIL, API_KEY, {})
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    return uid, models

def analyze_inventory_quality(product_name, required_qty):
    uid, models = get_odoo_connection()

    # 1. Find Product & Stock
    product = models.execute_kw(DB, uid, API_KEY, 'product.product', 'search_read', 
                               [[['name', 'ilike', product_name]]], 
                               {'fields': ['id', 'name', 'qty_available']})
    
    if not product: return "Product not found."
    
    p_id = product[0]['id']
    total_qty = product[0]['qty_available']

    # 2. Find Failed/Pending Quality Checks
    quality_issues = models.execute_kw(DB, uid, API_KEY, 'quality.check', 'search_count',
                                      [[['product_id', '=', p_id], 
                                        ['quality_state', '!=', 'pass']]])

    # 3. Final AI Calculation
    net_available = total_qty - quality_issues
    
    # 4. Generate AI Response
    prompt = (f"Context: planitswiss logistics. Product: {product_name}. "
              f"Total Stock: {total_qty}. Quality Issues: {quality_issues}. "
              f"Net Ready: {net_available}. Requirement: {required_qty}. "
              "Write a professional response to the team.")
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Example Execution
print(analyze_inventory_quality("Tent", 10))