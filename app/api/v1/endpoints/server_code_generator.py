"""
Server Code Generator - Clean version without f-string issues
"""

def generate_nodejs_code(site_id: str, detection_url: str) -> str:
    """Generate Node.js middleware code for AI detection."""
    return """/**
 * AI Bot Detection Middleware for Node.js
 * Place this file in your project and use as middleware
 */

const https = require('https');
const http = require('http');

class AIBotDetector {
    constructor(siteId) {
        this.siteId = siteId;
        this.detectionUrl = '""" + detection_url + """';
    }
    
    /**
     * Express middleware for AI detection
     */
    middleware() {
        return (req, res, next) => {
            this.detectAIBot(req);
            next(); // Continue to next middleware
        };
    }
    
    /**
     * Detect AI bot from request
     */
    detectAIBot(req) {
        const clientIp = this.getClientIP(req);
        const userAgent = req.get('User-Agent') ? req.get('User-Agent') : '';
        const referrer = req.get('Referer') ? req.get('Referer') : '';
        
        console.log('=== NEW REQUEST ===');
        console.log('IP:', clientIp);
        console.log('User-Agent:', userAgent.substring(0, 80) + '...');
        console.log('Is AI Bot?', this.isAIBot(userAgent));

        const detectionData = {
            site_id: this.siteId,
            ip_address: clientIp,
            user_agent: userAgent,
            url: req.originalUrl,
            referrer: referrer,
            timestamp: new Date().toISOString()
        };
        
        console.log('Sending detection data:', JSON.stringify(detectionData, null, 2));

        // Send detection request (async)
        this.sendDetectionRequest(detectionData);
        
        // Log locally if AI bot detected
        if (this.isAIBot(userAgent)) {
            console.log('🤖 AI Bot detected:', clientIp, userAgent);
        } else {
            console.log('👤 human user detected');
        }
    }
    
    /**
     * Send detection request to API
     */
    sendDetectionRequest(data) {
        console.log('🚀 Sending request to:', this.detectionUrl);
        const postData = JSON.stringify(dataS);
        
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData),
                'User-Agent': 'NodeJS-Server/""" + site_id + """'
            },
            timeout: 5000
        };
        
        const req = http.request(this.detectionUrl.replace('https://', 'http://'), options, (res) => {
            console.log('✅ AI Detector API responded:', res.statusCode);
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                console.log('AI Detector response:', data);
            });
        });
        
        req.on('error', (err) => {
            console.error('❌ AI Detection request failed:', err.message);
        });
        
        req.write(postData);
        req.end();
    }
    
    /**
     * Get client IP address
     */
    getClientIP(req) {
        return req.ip || 
               req.connection.remoteAddress || 
               req.socket.remoteAddress ||
               (req.connection.socket ? req.connection.socket.remoteAddress : null) ||
               '127.0.0.1';
    }
    
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
import time
from typing import Optional, Dict, Any
from datetime import datetime

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
        
        Args:
            request_data: Dictionary containing IP, User-Agent, URL, etc.
        
        Returns:
            Detection result dictionary
        \"\"\"
        try:
            # Log the request
            print(f"=== NEW REQUEST ===")
            print(f"IP: {request_data.get('ip_address', 'unknown')}")
            print(f"User-Agent: {request_data.get('user_agent', 'unknown')[:80]}...")
            
            # Prepare detection payload
            payload = {
                'site_id': self.site_id,
                'site_id': self.site_id,
                'ip_address': request_data.get('ip_address', ''),
                'user_agent': request_data.get('user_agent', ''),
                'url': request_data.get('url', ''),
                'referrer': request_data.get('referrer', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"Sending detection data: {json.dumps(payload, indent=2)}")
            
            # Send detection request
            response = self.send_detection_request(payload)
            
            # Check if AI bot detected locally
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
        \"\"\"
        Send detection request to AI Detector API
        
        Args:
            payload: Detection payload
        
        Returns:
            API response or None
        \"\"\"
        try:
            print(f"🚀 Sending request to: {self.detection_url}")
            
            response = self.session.post(
                self.detection_url,
                json=payload,
                timeout=5,
                stream=False
            )
            
            print(f"✅ AI Detector API responded: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"AI Detector response: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            return None
    
    def get_client_ip(self, request_data: Dict[str, Any]) -> str:
        \"\"\"
        Extract client IP from request data
        
        Args:
            request_data: Request dictionary
            
        Returns:
            Client IP address
        \"\"\"
        # Try different IP headers in order of preference
        ip_keys = [
            'http_x_forwarded_for',
            'http_x_real_ip', 
            'http_client_ip',
            'remote_addr'
        ]
        
        for key in ip_keys:
            if key in request_data and request_data[key]:
                ip = request_data[key]
                # Handle comma-separated IPs (proxy chains)
                if ',' in ip:
                    ip = ip.split(',')[0].strip()
                # Basic IP validation
                if self.is_valid_ip(ip):
                    return ip
        
        return request_data.get('remote_addr', '127.0.0.1')
    
    def is_ai_bot(self, user_agent: str) -> bool:
        \"\"\"
        Check if User-Agent indicates AI bot
        
        Args:
            user_agent: HTTP User-Agent header
            
        Returns:
            True if likely AI bot, False otherwise
        \"\"\"
        ai_patterns = [
            'gptbot', 'chatgpt', 'openai', 'googlebot', 'bingbot',
            'perplexity', 'anthropic', 'claude', 'bardbot'
        ]
        
        if not user_agent:
            return False
            
        ua_lower = user_agent.lower()
        return any(pattern in ua_lower for pattern in ai_patterns)
    
    def is_valid_ip(self, ip: str) -> bool:
        \"\"\"
        Basic IP address validation
        
        Args:
            ip: IP address string
            
        Returns:
            True if valid IP format
        \"\"\"
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not (0 <= int(part) <= 255):
                    return False
            return True
        except (ValueError, AttributeError):
            return False


# Django Integration
def django_middleware(get_response):
    \"\"\"
    Django middleware factory
    Place this in your settings.py MIDDLEWARE list:
    'path.to.this.file.django_middleware'
    \"\"\"
    detector = AIBotDetector('""" + site_id + """')
    
    def middleware(request):
        # Gather request data
        request_data = {
            'ip_address': detector.get_client_ip({
                'http_x_forwarded_for': request.META.get('HTTP_X_FORWARDED_FOR'),
                'http_x_real_ip': request.META.get('HTTP_X_REAL_IP'),
                'http_client_ip': request.META.get('HTTP_CLIENT_IP'),
                'remote_addr': request.META.get('REMOTE_ADDR')
            }),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'url': request.get_full_path(),
            'referrer': request.META.get('HTTP_REFERER', '')
        }
        
        # Perform detection
        detector.detect_ai_bot(request_data)
        
        # Continue to next middleware/view
        return get_response(request)
    
    return middleware


# Flask Integration
def flask_detector():
    \"\"\"
    Flask decorator/middleware
    Usage:
    from flask import Flask, request
    from ai_detector import AIBotDetector, flask_detector
    
    app = Flask(__name__)
    detector = AIBotDetector('""" + site_id + """')
    
    # Apply to all routes
    @app.before_request
    def before_request():
        flask_detector()
    
    Or decorate specific routes:
    @app.route('/')
    @flask_detector()
    def home():
        return 'Hello World!'
    \"\"\"
    def decorator(f):
        def decorated_function(*args, **kwargs):
            from flask import request
            
            # Gather request data
            request_data = {
                'ip_address': detector.get_client_ip({
                    'http_x_forwarded_for': request.headers.get('X-Forwarded-For'),
                    'http_x_real_ip': request.headers.get('X-Real-IP'),
                    'http_client_ip': request.headers.get('X-Client-IP'),
                    'remote_addr': request.remote_addr
                }),
                'user_agent': request.headers.get('User-Agent', ''),
                'url': request.url,
                'referrer': request.headers.get('Referer', '')
            }
            
            # Perform detection
            detector.detect_ai_bot(request_data)
            
            # Continue to original function
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# FastAPI Integration
class FastAPIDetector:
    \"\"\"
    FastAPI dependency for AI detection
    
    Usage:
    from fastapi import FastAPI, Depends, Request
    from ai_detector import FastAPIDetector
    
    app = FastAPI()
    detector = FastAPIDetector('""" + site_id + """')
    
    @app.get("/")
    async def root(request: Request, detection = Depends(detector.detect)):
        return {"message": "Hello World"}
    
    # Or apply globally
    app.middleware("http")(detector.middleware)
    \"\"\"
    
    def __init__(self, site_id, detection_url='""" + detection_url + """'):
        self.site_id = site_id
        self.detection_url = detection_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FastAPI-Server/""" + site_id + """'
        })
    
    async def detect(self, request: Request):
        \"\"\"FastAPI dependency\"\"\"
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', '')
        
        # Handle proxy headers
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for and ',' in forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
        
        request_data = {
            'ip_address': client_ip,
            'user_agent': user_agent,
            'url': str(request.url),
            'referrer': request.headers.get('referer', '')
        }
        
        return await self._detect_async(request_data)
    
    async def _detect_async(self, request_data):
        \"\"\"Async version of detection\"\"\"
        try:
            import asyncio
            
            # Run detection in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.detect_ai_bot, request_data)
        except Exception as e:
            print(f"❌ Async detection error: {str(e)}")
            return {'error': str(e)}
    
    def middleware(self, request: Request, call_next):
        \"\"\"FastAPI middleware\"\"\"
        try:
            # Gather request data
            client_ip = request.client.host
            user_agent = request.headers.get('user-agent', '')
            
            request_data = {
                'ip_address': client_ip,
                'user_agent': user_agent,
                'url': str(request.url),
                'referrer': request.headers.get('referer', '')
            }
            
            # Perform detection (async)
            detection_result = asyncio.create_task(self._detect_async(request_data))
            
        except Exception as e:
            see_print(f"Middleware error: {str(e)}")
        
        # Continue to next middleware/route
        response = await call_next(request)
        return response


# Standalone usage
if __name__ == "__main__":
    \"\"\"
    Example usage for standalone testing
    \"\"\"
    detector = AIBotDetector('""" + site_id + """')
    
    # Test request data
    test_request = {
        'ip_address': '127.0.0.1',
        'user_agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0',
        'url': '/test',
        'referrer': ''
    }
    
    result = detector.detect_ai_bot(test_request)
    print(f"Detection result: {result}")
"""
