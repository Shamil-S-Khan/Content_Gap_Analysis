"""
Content Gap Analysis - Gap Identification and Scoring System
Identifies missing, thin, outdated, and under-optimized content with impact scoring
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter
import re


class GapAnalyzer:
    """Identifies and scores content gaps"""
    
    def __init__(self):
        """Initialize gap analysis parameters"""
        self.gap_types = ['missing', 'thin', 'outdated', 'under-optimized']
        self.difficulty_levels = ['low', 'medium', 'high']
    
    def calculate_impact_score(self, 
                              competitor_frequency: int,
                              search_volume_estimate: int = 0,
                              topic_importance: float = 0.5,
                              competitive_advantage: float = 0.5,
                              keyword_count: int = 0) -> int:
        """
        Calculate impact score (0-100) based on multiple factors
        
        Args:
            competitor_frequency: How many competitors cover this topic
            search_volume_estimate: Estimated monthly search volume (if available)
            topic_importance: Relevance to your business (0-1)
            competitive_advantage: Opportunity to differentiate (0-1)
            keyword_count: Number of keywords/opportunities in this gap
        """
        # Competitor coverage (0-35 points) - more competitors = higher impact
        comp_score = min(competitor_frequency / 5.0, 1.0) * 35
        
        # Search volume estimate (0-30 points)
        search_score = min(search_volume_estimate / 8000.0, 1.0) * 30
        
        # Business importance (0-20 points)
        importance_score = topic_importance * 20
        
        # Keyword/opportunity richness (0-15 points)
        keyword_score = min(keyword_count / 50.0, 1.0) * 15
        
        total_score = int(comp_score + search_score + importance_score + keyword_score)
        
        # Add variability bonus for competitive advantage
        if competitive_advantage > 0.7:
            total_score += 5
        
        return min(max(total_score, 15), 100)
    
    def determine_difficulty(self, 
                           word_count_needed: int,
                           research_depth: str = 'medium',
                           technical_complexity: str = 'medium',
                           resource_requirements: List[str] = None) -> str:
        """
        Determine content creation difficulty
        
        Args:
            word_count_needed: Estimated word count
            research_depth: 'low', 'medium', 'high'
            technical_complexity: 'low', 'medium', 'high'
            resource_requirements: List of required resources
        """
        score = 0
        
        # Word count factor
        if word_count_needed < 1000:
            score += 1
        elif word_count_needed < 2500:
            score += 2
        else:
            score += 3
        
        # Research depth factor
        depth_scores = {'low': 1, 'medium': 2, 'high': 3}
        score += depth_scores.get(research_depth, 2)
        
        # Technical complexity factor
        complexity_scores = {'low': 1, 'medium': 2, 'high': 3}
        score += complexity_scores.get(technical_complexity, 2)
        
        # Resource requirements factor
        if resource_requirements:
            score += min(len(resource_requirements), 3)
        
        # Determine difficulty level
        if score <= 4:
            return 'low'
        elif score <= 7:
            return 'medium'
        else:
            return 'high'
    
    def identify_missing_content(self, 
                                your_topics: List[str],
                                competitor_topics: List[Dict[str, Any]],
                                competitor_sources: List[str]) -> List[Dict[str, Any]]:
        """Identify topics competitors cover that you don't"""
        
        your_topic_set = {t.lower() for t in your_topics}  # Case-insensitive comparison
        gaps = []
        
        # Analyze competitor topics
        topic_coverage = Counter()
        topic_keywords = {}
        
        for comp_topic in competitor_topics:
            topic_words = comp_topic.get('words', [])
            for word in topic_words[:5]:  # Top 5 words per topic
                word_lower = word.lower()
                if word_lower not in your_topic_set:
                    topic_coverage[word_lower] += 1
                    if word_lower not in topic_keywords:
                        topic_keywords[word_lower] = []
                    topic_keywords[word_lower].extend(topic_words[:10])
        
        # Create gap entries for significant missing topics
        for topic, frequency in topic_coverage.most_common(20):
            related_keywords = list(set(topic_keywords[topic]))[:15]
            
            # More varied scoring based on frequency and keyword richness
            impact = self.calculate_impact_score(
                competitor_frequency=frequency,
                search_volume_estimate=frequency * 600,
                topic_importance=min(0.5 + (frequency / 10.0), 1.0),
                competitive_advantage=0.7 if frequency >= 3 else 0.5,
                keyword_count=len(related_keywords)
            )
            
            # Vary difficulty based on topic complexity
            word_estimate = 1000 + (frequency * 200)
            difficulty = self.determine_difficulty(
                word_count_needed=word_estimate,
                research_depth='high' if frequency >= 4 else 'medium',
                technical_complexity='medium'
            )
            
            gaps.append({
                'title': f"Content about {topic.title()}",
                'gap_type': 'missing',
                'keywords': related_keywords,
                'impact_score': impact,
                'difficulty': difficulty,
                'reason': f"Topic covered by {frequency} competitors but absent from your content",
                'competitor_coverage': f"{frequency}/{len(competitor_sources)} competitors"
            })
        
        return gaps
    
    def identify_thin_content(self,
                            your_documents: List[Dict[str, Any]],
                            competitor_documents: List[Dict[str, Any]],
                            similarity_threshold: float = 0.4) -> List[Dict[str, Any]]:
        """Identify topics you cover superficially compared to competitors"""
        
        gaps = []
        
        # Compare document depth (word count, keyword density, etc.)
        your_doc_by_topic = {}
        for doc in your_documents:
            keywords = doc.get('keywords', [])
            for kw in keywords[:3]:  # Primary keywords
                if kw not in your_doc_by_topic:
                    your_doc_by_topic[kw] = []
                your_doc_by_topic[kw].append(doc)
        
        comp_doc_by_topic = {}
        for doc in competitor_documents:
            keywords = doc.get('keywords', [])
            for kw in keywords[:3]:
                if kw not in comp_doc_by_topic:
                    comp_doc_by_topic[kw] = []
                comp_doc_by_topic[kw].append(doc)
        
        # Find topics where your content is thinner
        for topic in your_doc_by_topic:
            if topic in comp_doc_by_topic:
                your_avg_words = np.mean([d.get('word_count', 0) for d in your_doc_by_topic[topic]])
                comp_avg_words = np.mean([d.get('word_count', 0) for d in comp_doc_by_topic[topic]])
                
                # If competitors have significantly more content (lowered threshold to 1.3x)
                if comp_avg_words > your_avg_words * 1.3:
                    word_gap = int(comp_avg_words - your_avg_words)
                    impact = self.calculate_impact_score(
                        competitor_frequency=len(comp_doc_by_topic[topic]),
                        search_volume_estimate=word_gap * 2,
                        topic_importance=min(0.5 + (word_gap / 2000.0), 1.0),
                        competitive_advantage=0.6,
                        keyword_count=len(comp_doc_by_topic[topic])
                    )
                    
                    difficulty = self.determine_difficulty(
                        word_count_needed=word_gap,
                        research_depth='medium' if word_gap > 1000 else 'low',
                        technical_complexity='low'
                    )
                    
                    gaps.append({
                        'title': f"Expand coverage of {topic.title()}",
                        'gap_type': 'thin',
                        'keywords': [topic] + [d.get('keywords', [])[0] for d in comp_doc_by_topic[topic] if d.get('keywords')],
                        'impact_score': impact,
                        'difficulty': difficulty,
                        'reason': f"Your content ({int(your_avg_words)} words avg) is thinner than competitors ({int(comp_avg_words)} words avg)",
                        'competitor_coverage': f"{len(comp_doc_by_topic[topic])} competitor documents"
                    })
        
        return gaps[:10]  # Top 10 thin content gaps
    
    def identify_outdated_content(self,
                                 your_documents: List[Dict[str, Any]],
                                 age_threshold_days: int = 365) -> List[Dict[str, Any]]:
        """Identify content that needs updating"""
        
        gaps = []
        current_date = datetime.now()
        
        for doc in your_documents:
            timestamp = doc.get('timestamp', '')
            if timestamp:
                try:
                    doc_date = datetime.fromisoformat(timestamp)
                    age_days = (current_date - doc_date).days
                    
                    if age_days > age_threshold_days:
                        keywords = doc.get('keywords', [])[:10]
                        
                        # Higher impact for older content
                        age_multiplier = min(age_days / 365.0, 3.0)
                        impact = self.calculate_impact_score(
                            competitor_frequency=int(2 + age_multiplier),
                            search_volume_estimate=int(age_days * 5),
                            topic_importance=min(0.4 + (age_multiplier * 0.2), 1.0),
                            competitive_advantage=0.5,
                            keyword_count=len(keywords)
                        )
                        
                        difficulty = self.determine_difficulty(
                            word_count_needed=max(500, int(age_days / 2)),
                            research_depth='medium' if age_days > 730 else 'low',
                            technical_complexity='low'
                        )
                        
                        gaps.append({
                            'title': f"Update: {doc.get('title', doc.get('source', 'Unknown').split('/')[-1])}",
                            'gap_type': 'outdated',
                            'keywords': keywords,
                            'impact_score': impact,
                            'difficulty': difficulty,
                            'reason': f"Content is {age_days} days old (threshold: {age_threshold_days} days)",
                            'competitor_coverage': 'N/A - internal update'
                        })
                except:
                    continue
        
        # Sort by age and return top 10
        return sorted(gaps, key=lambda x: x['impact_score'], reverse=True)[:10]
    
    def identify_underoptimized_content(self,
                                       your_documents: List[Dict[str, Any]],
                                       competitor_keywords: List[str]) -> List[Dict[str, Any]]:
        """Identify content that exists but lacks optimization"""
        
        gaps = []
        competitor_kw_set = set(competitor_keywords)
        
        for doc in your_documents:
            your_keywords = set(doc.get('keywords', []))
            
            # Find high-value competitor keywords missing from your content
            missing_keywords = competitor_kw_set - your_keywords
            
            if len(missing_keywords) > 3:  # Lower threshold to find more gaps
                missing_count = len(missing_keywords)
                impact = self.calculate_impact_score(
                    competitor_frequency=min(int(missing_count / 5), 8),
                    search_volume_estimate=missing_count * 150,
                    topic_importance=min(0.5 + (missing_count / 100.0), 0.9),
                    competitive_advantage=0.7,
                    keyword_count=missing_count
                )
                
                # Vary difficulty based on keyword count and optimization complexity
                if missing_count > 40:
                    # Extensive optimization required
                    difficulty = self.determine_difficulty(
                        word_count_needed=1500 + (missing_count * 15),
                        research_depth='high',
                        technical_complexity='medium'
                    )
                elif missing_count > 25:
                    # Moderate optimization
                    difficulty = self.determine_difficulty(
                        word_count_needed=1000 + (missing_count * 12),
                        research_depth='medium',
                        technical_complexity='medium'
                    )
                else:
                    # Light optimization
                    difficulty = self.determine_difficulty(
                        word_count_needed=500 + (missing_count * 10),
                        research_depth='low',
                        technical_complexity='low'
                    )
                
                gaps.append({
                    'title': doc.get('title', doc.get('source', 'Unknown').split('/')[-1]),
                    'gap_type': 'under-optimized',
                    'keywords': list(missing_keywords)[:15],
                    'impact_score': impact,
                    'difficulty': difficulty,
                    'reason': f"Missing {len(missing_keywords)} high-value competitor keywords",
                    'competitor_coverage': f"{len(missing_keywords)} keyword opportunities"
                })
        
        return sorted(gaps, key=lambda x: x['impact_score'], reverse=True)[:10]
    
    def analyze_all_gaps(self,
                        your_corpus: Dict[str, Any],
                        competitor_corpus: Dict[str, Any],
                        comparison_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Comprehensive gap analysis across all categories"""
        
        all_gaps = []
        
        # Extract data
        your_docs = your_corpus.get('documents', [])
        comp_docs = competitor_corpus.get('documents', [])
        your_keywords = your_corpus.get('top_keywords', [])
        comp_keywords = competitor_corpus.get('top_keywords', [])
        your_topics = comparison_data.get('your_topics', [])
        comp_topics = comparison_data.get('competitor_topics', [])
        
        # Identify missing content
        print("Analyzing missing content...")
        missing_gaps = self.identify_missing_content(
            your_topics=your_keywords,
            competitor_topics=comp_topics,
            competitor_sources=competitor_corpus.get('competitor_sources', ['Competitor 1', 'Competitor 2', 'Competitor 3'])
        )
        all_gaps.extend(missing_gaps)
        
        # Identify thin content
        print("Analyzing thin content...")
        thin_gaps = self.identify_thin_content(your_docs, comp_docs)
        all_gaps.extend(thin_gaps)
        
        # Identify outdated content
        print("Analyzing outdated content...")
        outdated_gaps = self.identify_outdated_content(your_docs)
        all_gaps.extend(outdated_gaps)
        
        # Identify under-optimized content
        print("Analyzing under-optimized content...")
        underopt_gaps = self.identify_underoptimized_content(your_docs, comp_keywords)
        all_gaps.extend(underopt_gaps)
        
        # Sort all gaps by impact score
        all_gaps = sorted(all_gaps, key=lambda x: x['impact_score'], reverse=True)
        
        return all_gaps


def main():
    """Example usage"""
    print("Gap Analysis System initialized")
    
    # This would typically load processed corpus and comparison data
    print("Gap analyzer ready. Use analyze_all_gaps() with corpus data.")


if __name__ == "__main__":
    main()
