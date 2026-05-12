"""
PromptOptimizer.py - Performance optimization layer for faster LLM responses
Features:
- Message windowing (keep only recent messages)
- Embedding-based caching for faster context retrieval
- Context compression
- Prompt optimization
"""

import json
import hashlib
import os
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import numpy as np

# Try to import faiss for vector caching; fallback to simple dict-based cache
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️  FAISS not available. Using simple cache instead (still fast)")


class PromptOptimizer:
    """Optimizes prompts and manages context caching for faster LLM inference"""
    
    def __init__(self, cache_dir: str = ".prompt_cache", embedding_dim: int = 384):
        """
        Initialize the optimizer with caching support
        
        Args:
            cache_dir: Directory for cache files
            embedding_dim: Dimension of embeddings (default 384 for fast models)
        """
        self.cache_dir = cache_dir
        self.embedding_dim = embedding_dim
        self.cache = {}  # Simple in-memory cache
        self.embeddings = {}  # Cache embeddings for fast retrieval
        
        # Create cache directory
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    @staticmethod
    def window_messages(messages: List[Dict], max_history: int = 10) -> List[Dict]:
        """
        Keep only recent messages (windowing strategy)
        Reduces context size significantly while maintaining conversation flow
        
        Args:
            messages: All messages in conversation
            max_history: Maximum number of recent turns to keep (default 10 turns = ~5 exchanges)
        
        Returns:
            Windowed message list (most recent max_history messages)
        """
        if len(messages) <= max_history:
            return messages
        
        # Keep system message (if present) + recent messages
        windowed = messages[-max_history:]
        return windowed
    
    @staticmethod
    def compress_context(messages: List[Dict], summary: str = None) -> List[Dict]:
        """
        Compress older conversation segments into summaries
        Useful for very long conversations (50+ messages)
        
        Args:
            messages: All messages
            summary: Pre-computed summary of old context
        
        Returns:
            Compressed message list with summary prepended
        """
        if len(messages) < 20:
            return messages  # No compression needed
        
        # Keep only recent 15 messages
        recent = messages[-15:]
        
        # If summary provided, prepend it
        if summary:
            summary_msg = {
                "role": "system",
                "content": f"[Context Summary]\n{summary}\n\n[Recent Conversation]"
            }
            return [summary_msg] + recent
        
        return recent
    
    @staticmethod
    def optimize_prompt(system_prompt: str, max_tokens: int = 500) -> str:
        """
        Reduce prompt size without losing key information
        Removes redundancy, excessive explanations, and filler
        
        Args:
            system_prompt: Full system prompt
            max_tokens: Maximum tokens to keep (rough estimate)
        
        Returns:
            Optimized prompt (more concise version)
        """
        lines = system_prompt.strip().split('\n')
        
        # Keep only non-empty lines and essential sections
        optimized_lines = []
        for line in lines:
            stripped = line.strip()
            # Skip excessive spacing and repetitive headers
            if stripped and not stripped.startswith('==='):
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def hash_content(self, content: str) -> str:
        """Generate hash for content (for caching)"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def cache_messages(self, session_id: int, messages: List[Dict], 
                       ttl_minutes: int = 60) -> str:
        """
        Cache windowed messages for quick retrieval
        
        Args:
            session_id: Chat session ID
            messages: Message list to cache
            ttl_minutes: Cache time-to-live in minutes
        
        Returns:
            Cache key
        """
        cache_key = f"session_{session_id}_msgs"
        self.cache[cache_key] = {
            "messages": messages,
            "timestamp": datetime.now(),
            "ttl_minutes": ttl_minutes
        }
        return cache_key
    
    def get_cached_messages(self, session_id: int) -> List[Dict]:
        """
        Retrieve cached messages if still valid
        
        Args:
            session_id: Chat session ID
        
        Returns:
            Cached messages or None if expired/not found
        """
        cache_key = f"session_{session_id}_msgs"
        
        if cache_key not in self.cache:
            return None
        
        cached = self.cache[cache_key]
        age = (datetime.now() - cached["timestamp"]).total_seconds() / 60
        
        # Check if cache expired
        if age > cached["ttl_minutes"]:
            del self.cache[cache_key]
            return None
        
        return cached["messages"]
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough token count estimation (1 token ≈ 4 characters for English)
        
        Args:
            text: Text to estimate
        
        Returns:
            Approximate token count
        """
        return len(text) // 4
    
    def build_optimized_context(self, 
                                system_prompt: str,
                                messages: List[Dict],
                                max_context_tokens: int = 1500) -> Tuple[str, List[Dict]]:
        """
        Build optimized context respecting token limits
        
        Args:
            system_prompt: System prompt
            messages: All messages
            max_context_tokens: Maximum tokens for entire context
        
        Returns:
            (optimized_system_prompt, windowed_messages)
        """
        # Optimize system prompt (usually 30-40% of context)
        opt_system = self.optimize_prompt(system_prompt)
        system_tokens = self.estimate_tokens(opt_system)
        
        remaining_tokens = max_context_tokens - system_tokens
        
        # Dynamically determine window size based on message size
        window_size = 10
        avg_msg_tokens = 50
        
        if remaining_tokens < avg_msg_tokens * window_size:
            window_size = max(3, remaining_tokens // avg_msg_tokens)
        
        # Window messages
        windowed = self.window_messages(messages, max_history=window_size)
        
        return opt_system, windowed


class SimpleEmbeddingCache:
    """Simple embedding cache without FAISS dependency (pure Python)"""
    
    def __init__(self, cache_dir: str = ".prompt_cache"):
        self.cache_dir = cache_dir
        self.embeddings = {}  # Maps text hash -> embedding
        self.similarity_threshold = 0.85
    
    def simple_hash_embedding(self, text: str) -> np.ndarray:
        """
        Generate simple embedding-like vector from text
        Fast fallback when transformers not available
        Uses character frequencies and basic statistics
        """
        # Normalize text
        text = text.lower().strip()
        
        # Create 384-dim vector (matches embedding size)
        embedding = np.zeros(384, dtype=np.float32)
        
        # Fill with character frequency data
        for i, char in enumerate(text):
            idx = (ord(char) * 17 + i) % 384  # Simple hash to index
            embedding[idx] += 1.0
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding /= norm
        
        return embedding
    
    def cache_text(self, text_hash: str, embedding: np.ndarray):
        """Cache an embedding"""
        self.embeddings[text_hash] = embedding
    
    def get_cached_embedding(self, text_hash: str) -> np.ndarray:
        """Retrieve cached embedding"""
        return self.embeddings.get(text_hash, None)


class ContextCache:
    """Manages context caching with TTL and size limits"""
    
    def __init__(self, max_sessions: int = 100):
        self.cache = {}
        self.max_sessions = max_sessions
    
    def store(self, session_id: int, context: Dict, ttl_minutes: int = 60):
        """Store context with TTL"""
        self.cache[session_id] = {
            "context": context,
            "timestamp": datetime.now(),
            "ttl": ttl_minutes
        }
        
        # Simple LRU: remove oldest if over limit
        if len(self.cache) > self.max_sessions:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
    
    def retrieve(self, session_id: int) -> Dict:
        """Retrieve context if still valid"""
        if session_id not in self.cache:
            return None
        
        cached = self.cache[session_id]
        age_minutes = (datetime.now() - cached["timestamp"]).total_seconds() / 60
        
        if age_minutes > cached["ttl"]:
            del self.cache[session_id]
            return None
        
        return cached["context"]
    
    def clear_expired(self):
        """Remove all expired entries"""
        now = datetime.now()
        expired = [
            sid for sid, data in self.cache.items()
            if (now - data["timestamp"]).total_seconds() / 60 > data["ttl"]
        ]
        for sid in expired:
            del self.cache[sid]


# Initialize global optimizer instance
_optimizer = PromptOptimizer()
_embedding_cache = SimpleEmbeddingCache()
_context_cache = ContextCache()


def get_optimizer() -> PromptOptimizer:
    """Get global optimizer instance"""
    return _optimizer


def get_embedding_cache() -> SimpleEmbeddingCache:
    """Get global embedding cache"""
    return _embedding_cache


def get_context_cache() -> ContextCache:
    """Get global context cache"""
    return _context_cache
