"""AI Bot Detection Service."""

import re
from typing import Optional, Tuple


class AIBotDetectionService:
    """Service for detecting AI bots based on User-Agent strings."""
    
    # Known AI bot patterns
    AI_BOT_PATTERNS = {
        'GPTBot': [
            r'GPTBot',
            r'ChatGPT-User',
            r'OpenAI',
        ],
        'Perplexity': [
            r'PerplexityBot',
            r'Perplexity',
        ],
        'Google Gemini': [
            r'Google-Extended',
            r'Gemini',
            r'GoogleAI',
        ],
        'Claude': [
            r'Claude-Web',
            r'Anthropic',
            r'ClaudeBot',
        ],
        'Bing AI': [
            r'BingBot',
            r'Microsoft-BingBot',
            r'BingPreview',
        ],
        'Meta AI': [
            r'facebookexternalhit',
            r'MetaBot',
        ],
        'Other AI Bots': [
            r'AI2Bot',
            r'YouBot',
            r'Character\.AI',
            r'JasperBot',
            r'Copy\.ai',
            r'NotionBot',
            r'SlackBot',
            r'DiscordBot',
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
