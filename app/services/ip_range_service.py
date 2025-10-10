"""AI Bot IP Range Service."""

import ipaddress
import requests
import json
from typing import List, Optional, Dict, Any, Set, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, delete

from app.models.ip_ranges import AIBotIPRange, IPRangeUpdateLog
from app.utils.logging import log_error


class IPRangeService:
    """Service for managing AI bot IP ranges and detection."""
    
    # URLs for different AI bot IP sources
    IP_SOURCES = {
        'chatgpt_user': 'https://raw.githubusercontent.com/FabrizioCafolla/openai-crawlers-ip-ranges/main/openai/openai-ip-ranges-chatgpt-user.txt',
        'gptbot': 'https://raw.githubusercontent.com/FabrizioCafolla/openai-crawlers-ip-ranges/main/openai/openai-ip-ranges-gptbot.txt',
        'searchbot': 'https://raw.githubusercontent.com/FabrizioCafolla/openai-crawlers-ip-ranges/main/openai/openai-ip-ranges-searchbot.txt',
        'openai_all': 'https://raw.githubusercontent.com/FabrizioCafolla/openai-crawlers-ip-ranges/main/openai/openai-ip-ranges-all.txt'
    }
    
    # Temporary in-memory storage for IP addresses (заменяет базу данных)
    _ai_bot_ips: Dict[str, Set[str]] = {
        'ChatGPT User': {
            '23.98.142.176', '13.65.138.112', '172.183.222.128',
            '20.102.212.144', '40.116.73.208', '172.183.143.224',
            '52.230.163.36', '52.230.163.32', '172.213.21.158',
            '52.230.163.44', '52.230.163.45'
        },
        'GPTBot': {
            '104.210.139.224', '20.0.53.96', '52.154.22.48',
            '52.242.245.208', '191.235.66.16'
        },
        'SearchBot': {
            '172.212.159.64', '52.255.111.80', '52.255.111.0',
            '4.151.241.240', '52.255.111.32'
        },
        'Other AI': set()
    }
    
    def __init__(self, db: Session):
        self.db = db
        self._load_ip_ranges_from_db()
    
    def _load_ip_ranges_from_db(self):
        """Load IP ranges from database into memory."""
        try:
            print("🔄 Loading IP ranges from database...")
            
            # Получаем все активные IP адреса из базы данных
            ip_ranges = self.db.query(AIBotIPRange).filter(AIBotIPRange.is_active == True).all()
            
            # Очищаем память
            for category in self._ai_bot_ips:
                self._ai_bot_ips[category].clear()
            
            # Загружаем IP адреса в память
            loaded_count = 0
            for ip_range in ip_ranges:
                # Определяем категорию бота
                storage_category = None
                if 'chatgpt' in ip_range.bot_name.lower() or 'user' in ip_range.bot_name.lower():
                    storage_category = 'ChatGPT User'
                elif 'gptbot' in ip_range.bot_name.lower():
                    storage_category = 'GPTBot'
                elif 'search' in ip_range.bot_name.lower():
                    storage_category = 'SearchBot'
                else:
                    storage_category = 'Other AI'
                
                if storage_category in self._ai_bot_ips:
                    self._ai_bot_ips[storage_category].add(ip_range.ip_address)
                    loaded_count += 1
            
            print(f"✅ Loaded {loaded_count} IP addresses from database")
            
        except Exception as e:
            print(f"❌ Error loading IP ranges from database: {e}")
    
    def is_ip_in_ai_bot_range(self, ip_address: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if IP address belongs to any known AI bot range.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            Tuple of (is_ai_bot, bot_name, source_type)
        """
        if not ip_address:
            return False, None, None
            
        try:
            # Проверяем в временном хранилище (in-memory)
            for bot_name, ip_set in self._ai_bot_ips.items():
                if ip_address in ip_set:
                    return True, bot_name, 'direct_ip'
            
            # Если IP не найден в памяти, попробуем базу данных как fallback
            try:
                exact_match = self.db.query(AIBotIPRange).filter(
                    and_(
                        AIBotIPRange.ip_address == ip_address,
                        AIBotIPRange.source_type == 'direct_ip',
                        AIBotIPRange.is_active == True
                    )
                ).first()
                
                if exact_match:
                    return True, exact_match.bot_name, 'direct_ip'
            except Exception:
                pass  # Игнорируем ошибки базы данных, используем только память
            
            return False, None, None
            
        except Exception as e:
            log_error(
                error_message=f"Error checking IP {ip_address} for AI bot range",
                error_details=str(e)
            )
            return False, None, None
    
    def add_ip_address(self, bot_name: str, ip_address: str, source_type: str = 'direct_ip', 
                      source_url: str = None) -> bool:
        """Add an IP address to both memory and database storage."""
        
        try:
            # Определяем категорию бота для нашего хранилища
            storage_category = None
            if 'chatgpt' in bot_name.lower() or 'user' in bot_name.lower():
                storage_category = 'ChatGPT User'
            elif 'gptbot' in bot_name.lower():
                storage_category = 'GPTBot'
            elif 'search' in bot_name.lower():
                storage_category = 'SearchBot'
            else:
                storage_category = 'Other AI'
            
            # Проверяем валидность IP
            if not self._is_valid_ip(ip_address):
                print(f"❌ Неверный IP адрес: {ip_address}")
                return False
            
            # Проверяем, не существует ли уже этот IP в базе данных
            existing_ip = self.db.query(AIBotIPRange).filter(
                AIBotIPRange.bot_name == bot_name,
                AIBotIPRange.ip_address == ip_address
            ).first()
            
            if existing_ip:
                print(f"⚠️ IP {ip_address} уже существует в базе данных")
                # Добавляем в память для консистентности
                self._ai_bot_ips[storage_category].add(ip_address)
                return True
            
            # Создаем новую запись в базе данных
            new_ip_range = AIBotIPRange(
                bot_name=bot_name,
                ip_address=ip_address,
                source_type=source_type,
                source_url=source_url,
                is_active=True
            )
            
            self.db.add(new_ip_range)
            self.db.commit()
            self.db.refresh(new_ip_range)
            
            # Добавляем в память
            self._ai_bot_ips[storage_category].add(ip_address)
            print(f"✅ Добавлен IP {ip_address} в категорию {storage_category} (сохранено в БД)")
            return True
                
        except Exception as e:
            print(f"❌ Ошибка добавления IP {ip_address}: {e}")
            self.db.rollback()
            return False
    
    async def update_ip_ranges_from_source(self, source_name: str, source_url: str, 
                                         bot_name: str = None) -> Dict[str, Any]:
        """
        Update IP ranges from external source.
        
        Args:
            source_name: Name of the source (e.g., 'chatgpt_user')
            source_url: URL to fetch IP ranges from
            bot_name: Bot name to associate with IPs (if None, extracted from source_name)
            
        Returns:
            Dictionary with update results
        """
        start_time = datetime.now()
        
        try:
            if not bot_name:
                bot_name = source_name.replace('_', ' ').replace('openai', 'OpenAI').title()
            
            # Fetch IP list from URL
            response = requests.get(source_url, timeout=30)
            response.raise_for_status()
            
            ip_lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
            
            # Get existing IPs for this bot
            existing_ips = {ip.ip_address for ip in self.db.query(AIBotIPRange.ip_address).filter(
                or_(
                    AIBotIPRange.bot_name == bot_name,
                    AIBotIPRange.bot_name.like(f'%{bot_name}%')
                )
            ).all()}
            
            # Process new IPs
            new_ips = set(ip_lines) - existing_ips
            removed_ips = existing_ips - set(ip_lines)
            
            changes_count = 0
            
            # Add new IPs
            for ip in new_ips:
                if self._is_valid_ip(ip):
                    self.add_ip_address(
                        bot_name=bot_name,
                        ip_address=ip,
                        source_type='direct_ip',
                        source_url=source_url
                    )
                    changes_count += 1
            
            # Deactivate removed IPs (don't delete, just mark as inactive)
            for ip in removed_ips:
                self.db.query(AIBotIPRange).filter(
                    and_(
                        AIBotIPRange.ip_address == ip,
                        AIBotIPRange.bot_name == bot_name
                    )
                ).update({'is_active': False, 'last_updated': func.now()})
                changes_count += 1
            
            self.db.commit()
            
            # Log update
            duration = (datetime.now() - start_time).total_seconds()
            self._log_update(
                bot_name=bot_name,
                update_type='full_update',
                changes_count=changes_count,
                source_url=source_url,
                duration_seconds=int(duration)
            )
            
            return {
                'success': True,
                'bot_name': bot_name,
                'source_url': source_url,
                'new_ips_count': len(new_ips),
                'removed_ips_count': len(removed_ips),
                'total_ips': len(ip_lines),
                'duration_seconds': duration,
                'changes_count': changes_count
            }
            
        except Exception as e:
            error_msg = f"Failed to update IP ranges for {source_name}: {str(e)}"
            log_error(
                error_message=error_msg,
                error_details=str(e),
                site_id=None
            )
            
            # Log failed update
            self._log_update(
                bot_name=bot_name or source_name,
                update_type='full_update',
                changes_count=0,
                source_url=source_url,
                error_message=error_msg,
                duration_seconds=int((datetime.now() - start_time).total_seconds())
            )
            
            return {
                'success': False,
                'error': error_msg,
                'bot_name': bot_name or source_name,
                'source_url': source_url
            }
    
    async def update_all_ai_bot_ips(self) -> Dict[str, Any]:
        """Update IP ranges for all known AI bot sources."""
        results = {}
        total_updates = 0
        successful_updates = 0
        
        for source_name, source_url in self.IP_SOURCES.items():
            result = await self.update_ip_ranges_from_source(source_name, source_url)
            results[source_name] = result
            
            if result.get('success'):
                successful_updates += 1
            
            total_updates += 1
        
        return {
            'total_sources': total_updates,
            'successful_updates': successful_updates,
            'failed_updates': total_updates - successful_updates,
            'sources': results
        }
    
    def get_bot_ip_stats(self, bot_name: str = None) -> Dict[str, Any]:
        """Get statistics about stored IP ranges."""
        
        # Получаем статистику из памяти
        bot_stats = {}
        total_ips = 0
        
        for category, ip_set in self._ai_bot_ips.items():
            count = len(ip_set)
            bot_stats[category] = count
            total_ips += count
        
        # Показываем топ IP адреса для отладки
        sample_ips = {}
        for category, ip_set in self._ai_bot_ips.items():
            sample_ips[category] = list(ip_set)[:5]  # Первые 5 IP
        
        return {
            'total_ip_ranges': total_ips,
            'active_ip_ranges': total_ips,  # Все IP активны
            'inactive_ip_ranges': 0,
            'bot_statistics': bot_stats,
            'sample_ips': sample_ips,  # Для отладки
            'storage_type': 'database_and_memory',
            'last_updates': {}
        }
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Check if IP address is valid."""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            try:
                ipaddress.ip_network(ip, strict=False)
                return True
            except ValueError:
                return False
    
    def _log_update(self, bot_name: str, update_type: str, changes_count: int,
                   source_url: str = None, error_message: str = None,
                   duration_seconds: int = None) -> IPRangeUpdateLog:
        """Log IP range update operation."""
        
        log_entry = IPRangeUpdateLog(
            bot_name=bot_name,
            update_type=update_type,
            changes_count=changes_count,
            source_url=source_url,
            error_message=error_message,
            duration_seconds=duration_seconds
        )
        
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        
        return log_entry
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """Clean up old update logs."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count = self.db.query(IPRangeUpdateLog).filter(
            IPRangeUpdateLog.created_at < cutoff_date
        ).delete()
        
        self.db.commit()
        return deleted_count
    
    def update_chatgpt_ips_from_crawlers_info(self, bot_name: str = 'ChatGPT-User') -> Dict[str, Any]:
        """Update ChatGPT IP addresses from crawlers-info.de database."""
        
        try:
            print("🔄 Fetching fresh ChatGPT IP addresses from crawlers-info.de...")
            
            # Fetch data from crawlers-info.de
            url = "https://crawlers-info.de/bots_info/973bdf5bbc8784a0b8204b9ca4aa5aae"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            print(f"✅ Got response from crawlers-info.de: {response.status_code}")
            
            # Parse IP addresses from the HTML content
            # Look for IP addresses in the "IP addresses:" section
            import re
            
            # Find the section from 'IP addresses:' to 'Countries:'
            start_marker = 'IP addresses:'
            end_marker = 'Countries:'
            
            start_pos = response.text.find(start_marker)
            end_pos = response.text.find(end_marker)
            
            if start_pos != -1 and end_pos != -1:
                ip_section_text = response.text[start_pos:end_pos]
                print(f"📄 Found IP addresses section from position {start_pos} to {end_pos}")
                
                # Extract IP addresses only from this section
                ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                found_ips = re.findall(ip_pattern, ip_section_text)
                
                # Filter out some common non-IP patterns and validate
                chatgpt_ips = []
                for ip in found_ips:
                    if self._is_valid_ip(ip) and not any(x in ip for x in ['0.0.0.0', '127.0.0', '255.255.255']):
                        chatgpt_ips.append(ip)
            else:
                print("❌ Could not find 'IP addresses:' section")
                chatgpt_ips = []
            
            print(f"🔍 Found {len(chatgpt_ips)} ChatGPT IP addresses from crawlers-info.de")
            
            # Display sample of found IPs
            sample_ips = chatgpt_ips[:10]
            print(f"📋 Sample IPs: {sample_ips}")
            
            # Обновляем в памяти
            self._ai_bot_ips['ChatGPT User'] = set(chatgpt_ips)
            
            changes_count = 0
            
            # Добавляем новые IP в базу данных
            for ip in chatgpt_ips:
                if self.add_ip_address(
                    bot_name=bot_name,
                    ip_address=ip,
                    source_type='crawlers_info',
                    source_url='https://crawlers-info.de/bots_info/973bdf5bbc8784a0b8204b9ca4aa5aae'
                ):
                    changes_count += 1
            
            # Логируем обновление
            self._log_update(
                bot_name=bot_name,
                update_type='manual_update',
                changes_count=changes_count,
                source_url='https://crawlers-info.de/bots_info/973bdf5bbc8784a0b8204b9ca4aa5aae'
            )
            
            return {
                'status': 'success',
                'bot_name': bot_name,
                'ips_added': changes_count,
                'total_ips': len(chatgpt_ips),
                'storage_status': 'Updated both memory and database',
                'source': 'crawlers-info.de'
            }
            
        except Exception as e:
            error_details = f"Failed to update ChatGPT IPs: {str(e)}"
            self._log_update(
                bot_name=bot_name,
                update_type='manual_update',
                changes_count=0,
                source_url='https://crawlers-info.de/bots_info/973bdf5bbc8784a0b8204b9ca4aa5aae',
                error_message=error_details
            )
            
            return {
                'status': 'error',
                'bot_name': bot_name,
                'error': str(e),
                'storage_status': 'Failed to update'
            }
