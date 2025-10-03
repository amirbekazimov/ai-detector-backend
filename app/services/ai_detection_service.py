"""AI Bot Detection Service."""

import re
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.services.ip_range_service import IPRangeService


class AIBotDetectionService:
    """Service for detecting AI bots based on User-Agent strings and IP addresses."""
    
    # Known AI bot patterns
    AI_BOT_PATTERNS = {
        'ChatGPT': [
            r'GPTBot',
            r'ChatGPT-User',
            r'OpenAI',
            r'ChatGPT',
        ],
        'DeepSeek': [
            r'DeepSeek',
            r'DeepSeekBot',
            r'DeepSeek-Crawler',
        ],
        'Claude': [
            r'Claude-Web',
            r'Anthropic',
            r'ClaudeBot',
            r'Claude',
        ],
        'Gemini': [
            r'Google-Extended',
            r'Gemini',
            r'GoogleAI',
            r'GeminiBot',
        ],
        'Perplexity': [
            r'PerplexityBot',
            r'Perplexity',
            r'PerplexityAI',
        ],
        'Bing AI': [
            r'BingBot',
            r'Microsoft-BingBot',
            r'BingPreview',
            r'BingAI',
        ],
        'Meta AI': [
            r'facebookexternalhit',
            r'MetaBot',
            r'MetaAI',
        ],
        'Character.AI': [
            r'Character\.AI',
            r'CharacterAI',
        ],
        'You.com': [
            r'YouBot',
            r'You\.com',
        ],
        'Other AI Bots': [
            r'AI2Bot',
            r'JasperBot',
            r'Copy\.ai',
            r'NotionBot',
            r'SlackBot',
            r'DiscordBot',
            r'CohereBot',
            r'ReplicateBot',
            r'HuggingFaceBot',
        ]
    }
    
    @classmethod
    def detect_ai_bot(cls, user_agent: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect if a User-Agent belongs to an AI bot.
        
        Args:
            user_agent: The User-Agent string to analyze
            
        Returns:
            Tuple of (bot_category, bot_name) or (None, None) if not an AI bot
        """
        if not user_agent:
            return None, None
            
        user_agent_lower = user_agent.lower()
        
        for bot_category, patterns in cls.AI_BOT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, user_agent_lower, re.IGNORECASE):
                    return bot_category, pattern
                    
        return None, None
    
    @classmethod
    def is_ai_bot(cls, user_agent: str) -> bool:
        """
        Check if User-Agent belongs to an AI bot.
        
        Args:
            user_agent: The User-Agent string to analyze
            
        Returns:
            True if AI bot detected, False otherwise
        """
        bot_category, _ = cls.detect_ai_bot(user_agent)
        return bot_category is not None
    
    @classmethod
    def get_bot_name(cls, user_agent: str) -> str:
        """
        Get the name of the AI bot from User-Agent.
        
        Args:
            user_agent: The User-Agent string to analyze
            
        Returns:
            Bot name if detected, 'unknown' otherwise
        """
        bot_category, bot_pattern = cls.detect_ai_bot(user_agent)
        
        if bot_category:
            # Extract the actual bot name from the pattern
            if bot_pattern:
                # Remove regex special characters and return clean name
                clean_name = re.sub(r'[^\w\-\.]', '', bot_pattern)
                return clean_name or bot_category
            return bot_category
            
        return 'unknown'
    
    @classmethod
    def detect_ai_bot_comprehensive(cls, user_agent: str, ip_address: str, db: Session) -> Tuple[Optional[str], Optional[str], str]:
        """
        Comprehensive AI bot detection using both User-Agent and IP address.
        
        Args:
            user_agent: The User-Agent string to analyze
            ip_address: The IP address to check against known AI bot ranges
            db: Database session for IP range queries
            
        Returns:
            Tuple of (bot_category, bot_name, detection_method)
            detection_method can be: 'user_agent', 'ip_address', 'both', or 'none'
        """
        user_agent_category, user_agent_pattern = cls.detect_ai_bot(user_agent)
        ip_is_bot, ip_bot_name, ip_source_type = IPRangeService(db).is_ip_in_ai_bot_range(ip_address)
        
        detected_bot_name = ''
        detection_method = 'none'
        final_category = None
        
        # Check User-Agent detection first
        if user_agent_category:
            final_category = user_agent_category
            detected_bot_name = cls.get_bot_name(user_agent)
            detection_method = 'user_agent'
        
        # Check IP-based detection
        if ip_is_bot and ip_bot_name:
            if detection_method == 'user_agent':
                # Both methods detected a bot
                detection_method = 'both'
                # Prioritize User-Agent detection for bot name if it exists
                if not final_category:
                    final_category = 'IP_Detected_Bot'
            else:
                # Only IP detection found a bot
                detection_method = 'ip_address'
                final_category = 'IP_Detected_Bot'
                detected_bot_name = f"IP_{ip_bot_name}"
        
        return final_category, detected_bot_name, detection_method
    
    @classmethod
    def is_ai_bot_comprehensive(cls, user_agent: str, ip_address: str, db: Session) -> bool:
        """
        Comprehensive check if visitor is an AI bot.
        
        Args:
            user_agent: The User-Agent string to analyze
            ip_address: The IP address to check against known AI bot ranges
            db: Database session for IP range queries
            
        Returns:
            True if AI bot detected by either method, False otherwise
        """
        bot_category, _, _ = cls.detect_ai_bot_comprehensive(user_agent, ip_address, db)
        return bot_category is not None
