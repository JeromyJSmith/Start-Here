"""
Ranking Engine - Ranks and scores query results
"""

from typing import List, Dict, Any
from datetime import datetime
import math

from .models import QueryResult, RankingStrategy


class RankingEngine:
    """Ranks query results based on various strategies"""
    
    async def rank(
        self,
        results: List[QueryResult],
        strategy: str = "hybrid",
        weights: Dict[str, float] = None
    ) -> List[QueryResult]:
        """Rank results based on strategy"""
        if not results:
            return results
        
        if weights is None:
            weights = {
                "relevance": 0.4,
                "recency": 0.2,
                "source_trust": 0.2,
                "user_preference": 0.2
            }
        
        if strategy == RankingStrategy.RELEVANCE:
            return self._rank_by_relevance(results)
        elif strategy == RankingStrategy.RECENCY:
            return self._rank_by_recency(results)
        else:  # HYBRID
            return self._rank_hybrid(results, weights)
    
    def _rank_by_relevance(self, results: List[QueryResult]) -> List[QueryResult]:
        """Rank by relevance score"""
        return sorted(results, key=lambda r: r.score, reverse=True)
    
    def _rank_by_recency(self, results: List[QueryResult]) -> List[QueryResult]:
        """Rank by timestamp"""
        return sorted(results, key=lambda r: r.timestamp, reverse=True)
    
    def _rank_hybrid(
        self, 
        results: List[QueryResult],
        weights: Dict[str, float]
    ) -> List[QueryResult]:
        """Hybrid ranking combining multiple factors"""
        # Calculate composite scores
        for result in results:
            # Base relevance score
            relevance_score = result.score * weights["relevance"]
            
            # Recency score (decay over time)
            age_hours = (datetime.utcnow() - result.timestamp).total_seconds() / 3600
            recency_score = math.exp(-age_hours / 168) * weights["recency"]  # Weekly decay
            
            # Source trust score
            source_trust = self._get_source_trust(result.source)
            trust_score = source_trust * weights["source_trust"]
            
            # User preference score (would be personalized in production)
            preference_score = 0.5 * weights["user_preference"]
            
            # Composite score
            result.score = relevance_score + recency_score + trust_score + preference_score
        
        return sorted(results, key=lambda r: r.score, reverse=True)
    
    def _get_source_trust(self, source: str) -> float:
        """Get trust score for source"""
        trust_scores = {
            "cognee": 0.9,      # High trust for semantic graph
            "llamacloud": 0.85, # High trust for indexed documents
            "memos": 0.8,       # Good trust for structured memory
            "memento": 0.7      # Moderate trust for key-value
        }
        return trust_scores.get(source, 0.5)