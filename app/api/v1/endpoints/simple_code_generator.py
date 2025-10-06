"""Simple code generator for client integration - DarkVisitors style."""

def generate_python_simple(site_id: str, api_url: str) -> str:
    """Generate simple Python code for AI detection."""
    return f"""# AI Bot Detection - Simple Integration
# Add this to your FastAPI/Django/Flask app

import requests

def track_ai_bot(request):
    \"\"\"Detect AI bots in the background.\"\"\"
    try:
        json_to_send = {{
            "request_path": str(request.path),
            "request_method": request.method,
            "request_headers": dict(request.headers),
        }}
        
        requests.post(
            "{api_url}/api/v1/tracking/detect",
            headers={{
                "Authorization": "Bearer {site_id}",
                "Content-Type": "application/json",
            }},
            json=json_to_send,
            timeout=2
        )
    except Exception:
        pass


# Usage in FastAPI:
# @app.middleware("http")
# async def detect_bots(request: Request, call_next):
#     import threading
#     threading.Thread(target=track_ai_bot, args=(request,)).start()
#     return await call_next(request)

# Usage in Flask:
# @app.before_request
# def before_request():
#     track_ai_bot(request)

# Usage in Django:
# Add to middleware.py:
# def process_request(self, request):
#     import threading
#     threading.Thread(target=track_ai_bot, args=(request,)).start()
#     return None
"""


def generate_nodejs_simple(site_id: str, api_url: str) -> str:
    """Generate simple Node.js code for AI detection."""
    return f"""// AI Bot Detection - Simple Integration
// Add this to your Express/Next.js app

const axios = require('axios');

async function trackAIBot(req) {{
    try {{
        await axios.post(
            '{api_url}/api/v1/tracking/detect',
            {{
                request_path: req.path,
                request_method: req.method,
                request_headers: req.headers,
            }},
            {{
                headers: {{
                    'Authorization': `Bearer {site_id}`,
                    'Content-Type': 'application/json',
                }},
            }}
        );
    }} catch (error) {{
        // Silent fail - don't break your app
    }}
}}

// Usage in Express:
// app.use((req, res, next) => {{
//     trackAIBot(req).catch(() => {{}});
//     next();
// }});
"""


def generate_php_simple(site_id: str, api_url: str) -> str:
    """Generate simple PHP code for AI detection."""
    return f"""<?php
// AI Bot Detection - Simple Integration
// Add this to your PHP app

function trackAIBot() {{
    $data = json_encode([
        'request_path' => $_SERVER['REQUEST_URI'],
        'request_method' => $_SERVER['REQUEST_METHOD'],
        'request_headers' => getallheaders(),
    ]);
    
    $options = [
        'http' => [
            'method' => 'POST',
            'header' => [
                'Authorization: Bearer {site_id}',
                'Content-Type: application/json',
            ],
            'content' => $data,
            'ignore_errors' => true,
        ],
    ];
    
    $context = stream_context_create($options);
    @file_get_contents('{api_url}/api/v1/tracking/detect', false, $context);
}}

// Usage:
// trackAIBot();  // Call at the start of your script
?>
"""


def generate_go_simple(site_id: str, api_url: str) -> str:
    """Generate simple Go code for AI detection."""
    return f"""// AI Bot Detection - Simple Integration
// Add this to your Go app

package main

import (
    "bytes"
    "encoding/json"
    "net/http"
)

func trackAIBot(r *http.Request) {{
    go func() {{
        defer func() {{
            if r := recover(); r != nil {{
                // Silent fail
            }}
        }}()
        
        data := map[string]interface{{}}{{
            "request_path":    r.URL.Path,
            "request_method":  r.Method,
            "request_headers": r.Header,
        }}
        
        jsonData, _ := json.Marshal(data)
        
        req, _ := http.NewRequest("POST", "{api_url}/api/v1/tracking/detect", bytes.NewBuffer(jsonData))
        req.Header.Set("Authorization", "Bearer {site_id}")
        req.Header.Set("Content-Type", "application/json")
        
        client := &http.Client{{}}
        client.Do(req)
    }}()
}}

// Usage in middleware:
// func middleware(next http.Handler) http.Handler {{
//     return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {{
//         trackAIBot(r)
//         next.ServeHTTP(w, r)
//     }})
// }}
"""


def generate_ruby_simple(site_id: str, api_url: str) -> str:
    """Generate simple Ruby code for AI detection."""
    return f"""# AI Bot Detection - Simple Integration
# Add this to your Rails/Sinatra app

require 'net/http'
require 'json'

def track_ai_bot(request)
  Thread.new do
    begin
      uri = URI('{api_url}/api/v1/tracking/detect')
      
      http = Net::HTTP.new(uri.host, uri.port)
      http.use_ssl = true if uri.scheme == 'https'
      
      req = Net::HTTP::Post.new(uri.path)
      req['Authorization'] = 'Bearer {site_id}'
      req['Content-Type'] = 'application/json'
      req.body = {{
        request_path: request.path,
        request_method: request.request_method,
        request_headers: request.headers.to_h
      }}.to_json
      
      http.request(req)
    rescue
      # Silent fail
    end
  end
end

# Usage in Rails:
# before_action :track_ai_bot
"""
