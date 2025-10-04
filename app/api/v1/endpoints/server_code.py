"""Server-side code generation for AI bot detection."""

from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.services.site_service import SiteService
from app.core.config import settings
from app.api.v1.endpoints.simple_code_generator import (
    generate_python_simple,
    generate_nodejs_simple,
    generate_php_simple
)

router = APIRouter()


@router.get("/sites/{site_id}/server-code")
async def get_server_code(
    site_id: str,
    language: str = "php",
    db: Session = Depends(get_db)
):
    """Generate server-side code for AI bot detection on user's site."""
    
    site_service = SiteService(db)
    
    # Try by numeric ID first, then by site_id string
    site = None
    try:
        numeric_id = int(site_id)
        site = site_service.get_site_by_id(numeric_id)
    except ValueError:
        # If not numeric, try by site_id string
        site = site_service.get_site_by_site_id(site_id)
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # API endpoint for detection
    api_url = settings.API_URL
    
    if language.lower() == "php":
        code = generate_php_simple(site.site_id, api_url)
        content_type = "text/php"
        filename = f"ai_detector_{site.site_id}.php"
        
    elif language.lower() == "python":
        code = generate_python_simple(site.site_id, api_url)
        content_type = "text/python"
        filename = f"ai_detector_{site.site_id}.py"
        
    elif language.lower() == "nodejs":
        code = generate_nodejs_simple(site.site_id, api_url)
        content_type = "text/javascript"
        filename = f"ai_detector_{site.site_id}.js"
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported language. Supported: php, python, nodejs"
        )
    
    return {
        "site_id": site.site_id,
        "site_name": site.name,
        "domain": site.domain,
        "language": language,
        "filename": filename,
        "server_code": code,
        "api_url": api_url,
        "instructions": get_server_instructions(language)
    }


def generate_php_code(site_id: str, detection_url: str) -> str:
    """Generate PHP code for AI detection."""
    return """<?php
/**
 * AI Bot Detection Script for Site: """ + site_id + """
 * Place this file on your server and include it in your pages
 */

class AIBotDetector {
    private $siteId = '""" + site_id + """';
    private $detectionUrl = '""" + detection_url + """';
    
    /**
     * Check if current visitor is an AI bot
     */
    public function detectAIBot() {{
        $clientIp = $this->getClientIP();
        $userAgent = $_SERVER['HTTP_USER_AGENT'] ?? '';
        $referrer = $_SERVER['HTTP_REFERER'] ?? '';
        $requestUri = $_SERVER['REQUEST_URI'] ?? '';
        
        // Send detection request
        $data = [
            'site_id' => $this->siteId,
            'ip_address' => $clientIp,
            'user_agent' => $userAgent,
            'referrer' => $referrer,
            'url' => $requestUri,
            'timestamp' => date('c')
        ];
        
        $this->sendDetectionRequest($data);
        
        // Log locally (optional)
        if ($this->isLikelyAIBot($clientIp, $userAgent)) {{
            error_log("AI Bot detected: {{$clientIp}} - {{$userAgent}}");
        }}
    }}
    
    /**
     * Send detection request to AI Detector API
     */
    private function sendDetectionRequest($data) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $this->detectionUrl);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'User-Agent: Site-Server/""" + site_id + """'
        ]);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        
        // Don't wait for response
        curl_setopt($ch, CURLOPT_NOSIGNAL, 1);
        curl_exec($ch);
        curl_close($ch);
    }}
    
    /**
     * Get real client IP address
     */
    private function getClientIP() {{
        $ipKeys = ['HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'HTTP_CLIENT_IP', 'REMOTE_ADDR'];
        
        foreach ($ipKeys as $key) {{
            if (!empty($_SERVER[$key])) {{
                $ip = $_SERVER[$key];
                // Handle comma-separated IPs (from proxies)
                if (strpos($ip, ',') !== false) {{
                    $ip = trim(explode(',', $ip)[0]);
                }}
                if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {{
                    return $ip;
                }}
            }}
        }}
        
        return $_SERVER['REMOTE_ADDR'] ?? '';
    }}
    
    /**
     * Quick AI bot check for logging
     */
    private function isLikelyAIBot($ip, $userAgent) {{
        $aiPatterns = [
            'GPTBot', 'ChatGPT', 'OpenAI', 'googlebot', 'bingbot',
            'perplexity', 'anthropic', 'claude'
        ];
        
        $ua = strtolower($userAgent);
        foreach ($aiPatterns as $pattern) {{
            if (strpos($ua, strtolower($pattern)) !== false) {{
                return true;
            }}
        }}
        
        return false;
    }}
}}

// Auto-execute detection
if (class_exists('AIBotDetector')) {{
    $detector = new AIBotDetector();
    $detector->detectAIBot();
}}

// Optional: For manual include in pages
// include_once 'ai_detector_""" + site_id + """.php';
// $detector->detectAIBot();
?>
"""


def generate_nginx_code(site_id: str, detection_url: str) -> str:
    """Generate Nginx configuration for AI detection."""
    return """# AI Bot Detection Nginx Configuration
# Place this in your nginx server block or include as separate file

location / {{
    # AI Bot Detection
    access_by_lua_block {{
        local http = require "resty.http"
        local json = require "cjson"
        
        local client_ip = ngx.var.remote_addr
        local user_agent = ngx.var.http_user_agent or ""
        local request_uri = ngx.var.request_uri or ""
        local referrer = ngx.var.http_referer or ""
        
        -- Prepare detection data
        local data = {{
            site_id = \"""" + site_id + """\",
            ip_address = client_ip,
            user_agent = user_agent,
            url = request_uri,
            referrer = referrer,
            timestamp = os.date("!%Y-%m-%dT%H:%M:%SZ")
        }}
        
        -- Send detection request (async)
        ngx.timer.at(0, function()
            local httpc = http.new()
            local res, err = httpc:request_uri(""" + detection_url + """, {{
                method = "POST",
                headers = {{
                    ["Content-Type"] = "application/json",
                    ["User-Agent"] = "Nginx-Server/""" + site_id + """"
                }},
                body = json.encode(data)
            }})
            
            if not res then
                ngx.log(ngx.ERR, "AI Detection request failed: ", err)
            end
        end)
    }}
    
    # Continue with your normal nginx processing
}}
"""


def generate_apache_code(site_id: str, detection_url: str) -> str:
    """Generate Apache .htaccess code for AI detection."""
    return """# AI Bot Detection for Apache
# Place this in your .htaccess file

<IfModule mod_rewrite.c>
    RewriteEngine On
    
    # AI Bot Detection Hook
    RewriteCond %{{REMOTE_ADDR}} .
    RewriteCond %{{HTTP_USER_AGENT}} .
    RewriteRule ^(.*)$ - [E=DETECTION_DATA:site_id=""" + site_id + """&ip=%{REMOTE_ADDR}&ua=%{HTTP_USER_AGENT}&url=$1]

</IfModule>

<IfModule mod_headers.c>
    # Extract detection data and send to API
    SetEnvIf DETECTION_DATA "^.*$" site_detection
</IfModule>

# PHP detection script (include this in your PHP pages)
# Place this script on your server and require it: require_once 'ai_detector_""" + site_id + """.php';
<Files "ai_detector_""" + site_id + """.php">
    Order allow,deny
    Allow from all
</Files>

# Or use server-side includes
AddType application/x-httpd-php .php

# Include detection in all pages
DirectoryIndex index.php index.html
"""


def generate_nodejs_code(site_id: str, detection_url: str) -> str:
    """Generate Node.js middleware code for AI detection."""
    return """/**
 * AI Bot Detection Middleware for Node.js
 * Place this file in your project and use as middleware
 */

const https = require('https');
const http = require('http');

class AIBotDetector {{
    constructor(siteId) {{
        this.siteId = siteId;
        this.detectionUrl = '""" + detection_url + """';
    }}
    
    /**
     * Express middleware for AI detection
     */
    middleware() {{
        return (req, res, next) => {{
            this.detectAIBot(req);
            next(); // Continue to next middleware
        }};
    }}
    
    /**
     * Detect AI bot from request
     */
    detectAIBot(req) {{
        const clientIp = this.getClientIP(req);
        const userAgent = req.get('User-Agent') || '';
        const referrer = req.get('Referer') || '';
        
        const detectionData = {{
            site_id: this.siteId,
            ip_address: clientIp,
            user_agent: userAgent,
            url: req.originalUrl,
            referrer: referrer,
            timestamp: new Date().toISOString()
        }};
        
        // Send detection request (async)
        this.sendDetectionRequest(detectionData);
        
        // Log locally if AI bot detected
        if (this.isAIBot(userAgent)) {{
            console.log('AI Bot detected:', clientIp, userAgent);
        }}
    }}
    
    /**
     * Send detection request to API
     */
    sendDetectionRequest(data) {{
        const postData = JSON.stringify(data);
        
        const options = {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData),
                'User-Agent': 'NodeJS-Server/""" + site_id + """'
            }},
            timeout: 5000
        }};
        
        const req = http.request(this.detectionUrl.replace('https://', 'http://'), options, (res) => {{
            // Optional: handle response
        }});
        
        req.on('error', (err) => {{
            console.error('AI Detection request failed:', err.message);
        }});
        
        req.write(postData);
        req.end();
    }}
    
    /**
     * Get client IP address
     */
    getClientIP(req) {{
        return req.ip || 
               req.connection.remoteAddress || 
               req.socket.remoteAddress ||
               (req.connection.socket ? req.connection.socket.remoteAddress : null) ||
               '127.0.0.1';
    }}
    
    /**
     * Check if likely AI bot
     */
    isAIBot(userAgent) {
        const aiPatterns = [
            'GPTBot', 'ChatGPT', 'OpenAI', 'googlebot', 'bingbot',
            'perplexity', 'anthropic', 'claude'
        ];
        
        const ua = userAgent.toLowerCase();
        return aiPatterns.some(pattern => ua.includes(pattern.toLowerCase()));
    }
}

// Export for CommonJS
module.exports = AIBotDetector;

// Usage example:
// const AIBotDetector = require('./aiBotDetector');
// const detector = new AIBotDetector('""" + site_id + """');
//
// Express.js
// app.use(detector.middleware());
//
// Or manual detection
// app.get('*', (req, res) => {
//     detector.detectAIBot(req);
//     res.send('Your content here');
// });
"""


def generate_python_code(site_id: str, detection_url: str) -> str:
    """Generate Python code for AI detection."""
    return """#!/usr/bin/env python3
\"\"\"
AI Bot Detection Module for Python
Works with Django, Flask, FastAPI, and other Python web frameworks
\"\"\"

import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any

class AIBotDetector:
    def __init__(self, site_id, detection_url='""" + detection_url + """'):
        self.site_id = site_id
        self.detection_url = detection_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Python-Server/""" + site_id + """'
        })
    
    def detect_ai_bot(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Detect AI bot from request data
        \"\"\"
        try:
            print(f"=== NEW REQUEST ===")
            print(f"IP: {request_data.get('ip_address', 'unknown')}")
            print(f"User-Agent: {request_data.get('user_agent', 'unknown')[:80]}...")
            
            payload = {
                'site_id': self.site_id,
                'ip_address': request_data.get('ip_address', ''),
                'user_agent': request_data.get('user_agent', ''),
                'url': request_data.get('url', ''),
                'referrer': request_data.get('referrer', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"Sending detection data: {json.dumps(payload, indent=2)}")
            response = self.send_detection_request(payload)
            
            is_ai_bot = self.is_ai_bot(request_data.get('user_agent', ''))
            
            if is_ai_bot:
                print(f"🤖 AI Bot detected: {request_data.get('ip_address')} {request_data.get('user_agent')[:50]}...")
            else:
                print(f"👤 Human user detected")
            
            return {
                'is_ai_bot': is_ai_bot,
                'detection_result': response,
                'site_id': self.site_id
            }
            
        except Exception as e:
            print(f"❌ AI Detection error: {str(e)}")
            return {'error': str(e)}
    
    def send_detection_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        \"\"\"Send detection request to AI Detector API\"\"\"
        try:
            print(f"🚀 Sending request to: {self.detection_url}")
            
            response = self.session.post(
                self.detection_url,
                json=payload,
                timeout=5
            )
            
            print(f"✅ AI Detector API responded: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"AI Detector response: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"❌ API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None
    
    def get_client_ip(self, request_headers: Dict[str, str], remote_addr: str = '127.0.0.1') -> str:
        \"\"\"Extract client IP from request headers\"\"\"
        ip_keys = ['HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'HTTP_CLIENT_IP']
        
        for key in ip_keys:
            if key in request_headers and request_headers[key]:
                ip = request_headers[key]
                if ',' in ip:
                    ip = ip.split(',')[0].strip()
                return ip
        
        return remote_addr
    
    def is_ai_bot(self, user_agent: str) -> bool:
        \"\"\"Check if User-Agent indicates AI bot\"\"\"
        ai_patterns = [
            'gptbot', 'chatgpt', 'openai', 'googlebot', 'bingbot',
            'perplexity', 'anthropic', 'claude', 'bardbot'
        ]
        
        if not user_agent:
            return False
            
        ua_lower = user_agent.lower()
        return any(pattern in ua_lower for pattern in ai_patterns)


# Django Middleware
def django_middleware(get_response):
    \"\"\"
    Django middleware factory
    Add to MIDDLEWARE in settings.py:
    'your_app.middleware.ai_detection_middleware'
    \"\"\"
    detector = AIBotDetector('""" + site_id + """')
    
    def middleware(request):
        request_data = {
            'ip_address': detector.get_client_ip(request.META, request.META.get('REMOTE_ADDR', '127.0.0.1')),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'url': request.get_full_path(),
            'referrer': request.META.get('HTTP_REFERER', '')
        }
        
        detector.detect_ai_bot(request_data)
        return get_response(request)
    
    return middleware


# Flask Integration
def flask_before_request():
    \"\"\"
    Flask before_request function
    Usage:
    from ai_detector import flask_before_request
    app.before_request(flask_before_request)
    \"\"\"
    from flask import request
    
    detector = AIBotDetector('""" + site_id + """')
    
    request_data = {
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'url': request.url,
        'referrer': request.headers.get('Referer', '')
    }
    
    detector.detect_ai_bot(request_data)


# FastAPI Middleware
async def fastapi_middleware(request, call_next):
    \"\"\"
    FastAPI middleware for AI detection
    Usage:
    app.add_middleware(BaseHTTPMiddleware, dispatch=fastapi_middleware)
    \"\"\"
    from starlette.middleware.base import BaseHTTPMiddleware
    
    detector = AIBotDetector('""" + site_id + """')
    
    client_ip = request.client.host
    user_agent = request.headers.get('user-agent', '')
    
    request_data = {
        'ip_address': client_ip,
        'user_agent': user_agent,
        'url': str(request.url),
        'referrer': request.headers.get('referer', '')
    }
    
    detector.detect_ai_bot(request_data)
    
    response = await call_next(request)
    return response


# Example usage
if __name__ == "__main__":
    detector = AIBotDetector('""" + site_id + """')
    
    test_request = {
        'ip_address': '127.0.0.1',
        'user_agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0',
        'url': '/test',
        'referrer': ''
    }
    
    result = detector.detect_ai_bot(test_request)
    print(f"Detection result: {result}")
"""


def get_server_instructions(language: str) -> dict:
    """Get instructions for server integration."""
    instructions = {
        "php": {
            "step1": "Copy the PHP code to your server",
            "step2": "Call trackAIBot() at the start of your PHP scripts",
            "step3": "Or add to your auto_prepend_file in php.ini",
            "step4": "Check server logs for AI bot detection messages"
        },
        "nodejs": {
            "step1": "Copy the JavaScript code to your project",
            "step2": "Add the middleware to your Express app",
            "step3": "Call trackAIBot(req) before your routes",
            "step4": "Monitor console logs for AI bot detection"
        },
        "python": {
            "step1": "Copy the Python code to your project",
            "step2": "Add the middleware to your FastAPI/Django/Flask app",
            "step3": "Call track_ai_bot(request) in your middleware",
            "step4": "Monitor console logs for AI bot detection"
        }
    }
    
    return instructions.get(language, instructions["php"])
