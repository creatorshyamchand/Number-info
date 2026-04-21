import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

# ---------------- CONFIG ----------------
API_BASE_URL = "https://yash-code-with-ai.alphamovies.workers.dev"
API_KEY = "7189814021"

# ---------------- HELPER FUNCTIONS ----------------
def validate_phone(number):
    """Validate Indian phone number format"""
    # Remove any non-digit characters
    clean_number = re.sub(r'\D', '', number)
    
    # Check if it's a valid Indian mobile number (10 digits, starting with 6-9)
    if len(clean_number) == 10:
        if clean_number[0] in ['6', '7', '8', '9']:
            return True, clean_number
    # Check with country code
    elif len(clean_number) == 12 and clean_number.startswith('91'):
        if clean_number[2] in ['6', '7', '8', '9']:
            return True, clean_number[2:]
    elif len(clean_number) == 13 and clean_number.startswith('+91'):
        if clean_number[3] in ['6', '7', '8', '9']:
            return True, clean_number[3:]
    
    return False, clean_number

def get_number_info(phone_number):
    """Fetch number information from the API"""
    try:
        url = f"{API_BASE_URL}/?num={phone_number}&key={API_KEY}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "success" and "data" in data:
                # Clean and restructure the response
                cleaned_data = []
                for item in data["data"]:
                    cleaned_item = {
                        "name": item.get("name", "N/A"),
                        "mobile": item.get("mobile", phone_number),
                        "father_name": item.get("fname", "N/A"),
                        "address": item.get("address", "N/A"),
                        "alternate_number": item.get("alt", "N/A"),
                        "telecom_circle": item.get("circle", "N/A"),
                        "reference_id": item.get("id", "N/A")
                    }
                    cleaned_data.append(cleaned_item)
                
                return {
                    "success": True,
                    "number": phone_number,
                    "results_count": len(cleaned_data),
                    "data": cleaned_data,
                    "checked_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "checked_timestamp": int(datetime.utcnow().timestamp()),
                    "api_info": {
                        "developed_by": "Creator Shyamchand & Ayan",
                        "organization": "CEO & Founder Of - Nexxon Hackers",
                        "version": "1.0.0"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "No data found for this number",
                    "number": phone_number
                }
        else:
            return {
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "number": phone_number
            }
            
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}",
            "number": phone_number
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "number": phone_number
        }

def batch_lookup(numbers):
    """Perform batch lookup for multiple numbers"""
    results = []
    for num in numbers:
        num = num.strip()
        is_valid, clean_num = validate_phone(num)
        if is_valid:
            info = get_number_info(clean_num)
            results.append(info)
        else:
            results.append({
                "success": False,
                "error": "Invalid phone number format",
                "number": num
            })
    return results

# ---------------- HTML TEMPLATE ----------------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Number Information API - Nexxon Hackers</title>
<script src="https://cdn.tailwindcss.com/3.4.16"></script>
<script>tailwind.config={theme:{extend:{colors:{primary:'#10b981',secondary:'#059669'},borderRadius:{'none':'0px','sm':'4px',DEFAULT:'8px','md':'12px','lg':'16px','xl':'20px','2xl':'24px','3xl':'32px','full':'9999px','button':'8px'}}}}</script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css" rel="stylesheet">
<style>
.loading-spinner {
    border: 2px solid #f3f3f3;
    border-top: 2px solid #10b981;
    border-radius: 50%;
    width: 16px;
    height: 16px;
    animation: spin 1s linear infinite;
    display: inline-block;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.json-viewer {
    background: #1e1e1e;
    border-radius: 8px;
    padding: 16px;
    overflow-x: auto;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 13px;
    line-height: 1.5;
}
.json-key { color: #9cdcfe; }
.json-string { color: #ce9178; }
.json-number { color: #b5cea8; }
.json-boolean { color: #569cd6; }
.json-null { color: #569cd6; }
.glow-text {
    text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}
</style>
</head>
<body class="bg-gradient-to-br from-emerald-50 via-white to-teal-50 min-h-screen">
<main class="pt-8 pb-12 px-4 max-w-4xl mx-auto">
    
    <!-- Header -->
    <header class="text-center py-8">
        <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary to-secondary rounded-3xl mb-6 shadow-lg">
            <i class="ri-phone-line text-white ri-3x"></i>
        </div>
        <h1 class="text-4xl font-bold text-gray-900 mb-2 glow-text">Number Information API</h1>
        <p class="text-lg text-gray-600 mb-2">Advanced Phone Number Lookup Service</p>
        <p class="text-sm text-gray-500">Name • Address • Telecom Circle • Alternate Numbers</p>
    </header>

    <!-- Live Test Section -->
    <section class="mb-8 bg-white rounded-3xl p-8 shadow-xl border border-emerald-100">
        <h2 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <i class="ri-flask-line text-primary mr-2"></i>
            Live API Test
        </h2>
        <div class="flex flex-col sm:flex-row gap-3 mb-4">
            <input type="text" id="numberInput" placeholder="Enter phone number (e.g., 8016827315)" 
                   class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none">
            <button id="testBtn" class="bg-gradient-to-r from-primary to-secondary text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition flex items-center justify-center gap-2">
                <i class="ri-search-line"></i>
                <span>Lookup Number</span>
            </button>
        </div>
        <div class="flex gap-2 mb-4 flex-wrap">
            <button onclick="document.getElementById('numberInput').value='8016827315'; document.getElementById('testBtn').click()" 
                    class="text-xs bg-emerald-50 hover:bg-emerald-100 px-3 py-1 rounded-full text-emerald-700 transition border border-emerald-200">
                Try 8016827315
            </button>
            <button onclick="document.getElementById('numberInput').value='9876543210'; document.getElementById('testBtn').click()" 
                    class="text-xs bg-emerald-50 hover:bg-emerald-100 px-3 py-1 rounded-full text-emerald-700 transition border border-emerald-200">
                Try Sample 1
            </button>
            <button onclick="document.getElementById('numberInput').value='9999999999'; document.getElementById('testBtn').click()" 
                    class="text-xs bg-emerald-50 hover:bg-emerald-100 px-3 py-1 rounded-full text-emerald-700 transition border border-emerald-200">
                Try Sample 2
            </button>
        </div>
        <div id="responseContainer" class="hidden">
            <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Response:</span>
                <button id="copyBtn" class="text-xs text-primary hover:text-secondary flex items-center gap-1">
                    <i class="ri-file-copy-line"></i> Copy
                </button>
            </div>
            <pre id="responseDisplay" class="json-viewer"></pre>
        </div>
        <div id="loadingIndicator" class="hidden text-center py-8">
            <div class="loading-spinner w-8 h-8"></div>
            <span class="ml-3 text-gray-500">Fetching number information...</span>
        </div>
        <div id="errorDisplay" class="hidden bg-red-50 border border-red-200 rounded-xl p-4 text-red-700"></div>
    </section>

    <!-- Features Grid -->
    <section class="mb-8">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="bg-white rounded-xl p-5 border border-emerald-100 shadow-sm">
                <div class="flex items-center">
                    <div class="w-10 h-10 flex items-center justify-center bg-emerald-100 rounded-xl mr-3">
                        <i class="ri-user-line text-emerald-600 ri-lg"></i>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900">Name & Details</h4>
                        <p class="text-xs text-gray-600">Full name and father's name</p>
                    </div>
                </div>
            </div>
            <div class="bg-white rounded-xl p-5 border border-teal-100 shadow-sm">
                <div class="flex items-center">
                    <div class="w-10 h-10 flex items-center justify-center bg-teal-100 rounded-xl mr-3">
                        <i class="ri-map-pin-line text-teal-600 ri-lg"></i>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900">Complete Address</h4>
                        <p class="text-xs text-gray-600">Full postal address</p>
                    </div>
                </div>
            </div>
            <div class="bg-white rounded-xl p-5 border border-green-100 shadow-sm">
                <div class="flex items-center">
                    <div class="w-10 h-10 flex items-center justify-center bg-green-100 rounded-xl mr-3">
                        <i class="ri-signal-tower-line text-green-600 ri-lg"></i>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900">Telecom Circle</h4>
                        <p class="text-xs text-gray-600">Network provider info</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- API Endpoints -->
    <section class="mb-8">
        <h2 class="text-xl font-bold text-gray-900 mb-4">API Endpoints</h2>
        <div class="space-y-4">
            
            <!-- Single Number -->
            <div class="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="font-semibold text-gray-900">Single Number Lookup</h3>
                    <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">GET</span>
                </div>
                <div class="bg-gray-900 rounded-lg p-3 mb-3">
                    <code class="text-green-400 text-sm">/api/number?number={PHONE_NUMBER}</code>
                </div>
                <div class="bg-emerald-50 rounded-lg p-3 border border-emerald-200">
                    <p class="text-xs font-medium text-emerald-900 mb-1">Example:</p>
                    <code class="text-xs text-emerald-700">curl "https://api.example.com/api/number?number=8016827315"</code>
                </div>
            </div>

            <!-- Batch Numbers (Comma) -->
            <div class="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="font-semibold text-gray-900">Batch Lookup (Comma)</h3>
                    <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">GET</span>
                </div>
                <div class="bg-gray-900 rounded-lg p-3 mb-3">
                    <code class="text-green-400 text-sm">/api/number?number={NUM1},{NUM2},{NUM3}</code>
                </div>
                <div class="bg-emerald-50 rounded-lg p-3 border border-emerald-200">
                    <p class="text-xs font-medium text-emerald-900 mb-1">Example:</p>
                    <code class="text-xs text-emerald-700">curl "https://api.example.com/api/number?number=8016827315,9876543210"</code>
                </div>
            </div>

            <!-- Batch Numbers (POST) -->
            <div class="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="font-semibold text-gray-900">Batch Lookup (POST)</h3>
                    <span class="px-3 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">POST</span>
                </div>
                <div class="bg-gray-900 rounded-lg p-3 mb-3">
                    <code class="text-green-400 text-sm">/api/batch</code>
                </div>
                <div class="bg-emerald-50 rounded-lg p-3 border border-emerald-200">
                    <p class="text-xs font-medium text-emerald-900 mb-1">Request Body:</p>
                    <code class="text-xs text-emerald-700">{"numbers": ["8016827315", "9876543210"]}</code>
                </div>
            </div>

        </div>
    </section>

    <!-- Sample Response -->
    <section class="mb-8 bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <i class="ri-braces-line text-primary mr-2"></i>
            Sample Response
        </h2>
        <pre class="json-viewer text-xs">{
  "success": true,
  "number": "8016827315",
  "results_count": 1,
  "data": [
    {
      "name": "Abhay Kumar Das",
      "mobile": "8016827315",
      "father_name": "Bishwanath Das",
      "address": "VILL Gopalpur Hafania Dafahat co-bishwanath das vill-gopalpur hafania murshidabad West Bengal 742224",
      "alternate_number": "8768367514",
      "telecom_circle": "JIO WB",
      "reference_id": "779410414335"
    }
  ],
  "checked_at": "2024-01-15 10:30:45 UTC",
  "checked_timestamp": 1705315245,
  "api_info": {
    "developed_by": "Creator Shyamchand & Ayan",
    "organization": "CEO & Founder Of - Nexxon Hackers",
    "version": "1.0.0"
  }
}</pre>
    </section>

    <!-- Developer Team Image -->
    <section class="mb-8">
        <div class="bg-gradient-to-br from-emerald-100 to-teal-100 rounded-3xl p-6 border border-emerald-200">
            <h3 class="text-lg font-bold text-gray-900 mb-4 text-center">Powered By Nexxon Hackers Team</h3>
            <img src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&h=400&fit=crop" 
                 alt="Nexxon Hackers Development Team" 
                 class="w-full h-48 object-cover object-top rounded-xl shadow-md">
            <p class="text-center text-sm text-gray-600 mt-4">Our expert team building innovative solutions</p>
        </div>
    </section>

    <!-- Developer Credit -->
    <div class="text-center py-6">
        <div class="inline-block bg-gradient-to-r from-primary to-secondary text-white px-8 py-4 rounded-2xl shadow-lg">
            <p class="font-bold text-lg">Developed by Creator Shyamchand & Ayan</p>
            <p class="text-sm opacity-95">CEO & Founder Of - Nexxon Hackers</p>
        </div>
    </div>

</main>

<script>
function syntaxHighlight(json) {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g, function (match) {
        var cls = 'json-number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'json-key';
                match = match.slice(0, -1) + '</span>:';
                return '<span class="' + cls + '">' + match;
            } else {
                cls = 'json-string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'json-boolean';
        } else if (/null/.test(match)) {
            cls = 'json-null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

document.getElementById('testBtn').addEventListener('click', async function() {
    const numberInput = document.getElementById('numberInput');
    const number = numberInput.value.trim();
    
    if (!number) {
        alert('Please enter a phone number');
        return;
    }
    
    const responseContainer = document.getElementById('responseContainer');
    const responseDisplay = document.getElementById('responseDisplay');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorDisplay = document.getElementById('errorDisplay');
    
    responseContainer.classList.add('hidden');
    errorDisplay.classList.add('hidden');
    loadingIndicator.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/number?number=' + encodeURIComponent(number));
        const data = await response.json();
        
        loadingIndicator.classList.add('hidden');
        
        const jsonStr = JSON.stringify(data, null, 2);
        responseDisplay.innerHTML = syntaxHighlight(jsonStr);
        responseContainer.classList.remove('hidden');
        
    } catch (error) {
        loadingIndicator.classList.add('hidden');
        errorDisplay.textContent = 'Error: ' + error.message;
        errorDisplay.classList.remove('hidden');
    }
});

document.getElementById('copyBtn').addEventListener('click', function() {
    const responseDisplay = document.getElementById('responseDisplay');
    const text = responseDisplay.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copyBtn');
        btn.innerHTML = '<i class="ri-check-line"></i> Copied!';
        setTimeout(() => {
            btn.innerHTML = '<i class="ri-file-copy-line"></i> Copy';
        }, 2000);
    });
});

document.getElementById('numberInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        document.getElementById('testBtn').click();
    }
});
</script>
</body>
</html>
'''

# ---------------- FLASK ROUTES ----------------
@app.route('/')
def home():
    """Home page with API documentation"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/number', methods=['GET'])
def number_lookup():
    """Single number lookup endpoint"""
    number_param = request.args.get('number')
    
    if not number_param:
        return jsonify({
            "success": False,
            "error": "Missing 'number' parameter",
            "usage": {
                "endpoint": "/api/number?number=PHONE_NUMBER",
                "example": "/api/number?number=8016827315"
            },
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        }), 400
    
    # Handle multiple numbers separated by comma
    if ',' in number_param:
        numbers = [num.strip() for num in number_param.split(',')]
        results = batch_lookup(numbers)
        
        return jsonify({
            "success": True,
            "batch_mode": True,
            "total_requested": len(numbers),
            "results": results,
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        })
    
    # Single number lookup
    is_valid, clean_number = validate_phone(number_param)
    
    if not is_valid:
        return jsonify({
            "success": False,
            "error": "Invalid phone number format. Must be a valid 10-digit Indian mobile number.",
            "provided_number": number_param,
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        }), 400
    
    result = get_number_info(clean_number)
    
    # Add API info to all responses
    if "api_info" not in result:
        result["api_info"] = {
            "developed_by": "Creator Shyamchand & Ayan",
            "organization": "CEO & Founder Of - Nexxon Hackers"
        }
    
    return jsonify(result)

@app.route('/api/batch', methods=['POST'])
def batch_number_lookup():
    """Batch number lookup endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'numbers' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'numbers' array in request body",
                "example": {"numbers": ["8016827315", "9876543210"]},
                "api_info": {
                    "developed_by": "Creator Shyamchand & Ayan",
                    "organization": "CEO & Founder Of - Nexxon Hackers"
                }
            }), 400
        
        numbers = data['numbers']
        if not isinstance(numbers, list):
            return jsonify({
                "success": False,
                "error": "'numbers' must be an array",
                "api_info": {
                    "developed_by": "Creator Shyamchand & Ayan",
                    "organization": "CEO & Founder Of - Nexxon Hackers"
                }
            }), 400
        
        results = batch_lookup(numbers)
        
        return jsonify({
            "success": True,
            "total_requested": len(numbers),
            "total_processed": len(results),
            "results": results,
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Number Information API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "api_info": {
            "developed_by": "Creator Shyamchand & Ayan",
            "organization": "CEO & Founder Of - Nexxon Hackers"
        }
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": {
            "home": "/",
            "single_number": "/api/number?number=PHONE_NUMBER",
            "batch_get": "/api/number?number=NUM1,NUM2,NUM3",
            "batch_post": "/api/batch (POST)",
            "health": "/api/health"
        },
        "api_info": {
            "developed_by": "Creator Shyamchand & Ayan",
            "organization": "CEO & Founder Of - Nexxon Hackers"
        }
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "api_info": {
            "developed_by": "Creator Shyamchand & Ayan",
            "organization": "CEO & Founder Of - Nexxon Hackers"
        }
    }), 500

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
