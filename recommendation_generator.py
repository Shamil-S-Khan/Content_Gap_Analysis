"""
Content Gap Analysis - Recommendation Generator
Creates detailed, actionable content recommendations with full specifications
"""

import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
import re


class RecommendationGenerator:
    """Generates detailed content recommendations from gap analysis"""
    
    def __init__(self):
        """Initialize recommendation generator"""
        self.intent_types = ['informational', 'transactional', 'navigational']
        self.media_types = ['infographic', 'video', 'screenshot', 'diagram', 'chart', 'photo']
    
    def classify_search_intent(self, keywords: List[str], title: str) -> str:
        """Classify search intent based on keywords and title"""
        
        # Transactional indicators (buying/purchasing intent)
        transactional_keywords = ['buy', 'price', 'cost', 'purchase', 'order', 'shop', 
                                 'deal', 'discount', 'coupon', 'cheap', 'best price',
                                 'pricing', 'plans', 'subscription', 'free trial']
        
        # Navigational indicators (looking for specific page/login)
        navigational_keywords = ['login', 'sign in', 'account', 'dashboard', 'portal',
                                'official', 'homepage', 'contact', 'download', 'install']
        
        # Comparison/Commercial investigation (researching before purchase)
        commercial_keywords = ['vs', 'versus', 'comparison', 'compare', 'alternative',
                              'alternatives', 'review', 'reviews', 'best', 'top',
                              'pros and cons', 'which is better']
        
        # How-to/Tutorial (learning/doing something)
        how_to_keywords = ['how to', 'guide', 'tutorial', 'step by step', 'learn',
                          'tips', 'examples', 'complete guide', 'beginner',
                          'getting started', 'setup', 'configure']
        
        # What/Why (understanding concepts)
        conceptual_keywords = ['what is', 'what are', 'why', 'definition', 'meaning',
                              'explain', 'introduction', 'overview', 'basics']
        
        # Check keywords and title
        text = (title + ' ' + ' '.join(keywords)).lower()
        
        # Priority order: transactional > commercial > navigational > how-to > conceptual > informational
        if any(kw in text for kw in transactional_keywords):
            return 'Transactional (buy/pricing)'
        elif any(kw in text for kw in commercial_keywords):
            return 'Commercial (comparison/research)'
        elif any(kw in text for kw in navigational_keywords):
            return 'Navigational (download/access)'
        elif any(kw in text for kw in how_to_keywords):
            return 'Informational (how-to/tutorial)'
        elif any(kw in text for kw in conceptual_keywords):
            return 'Informational (conceptual)'
        else:
            return 'Informational (general)'
    
    def generate_outline(self, title: str, keywords: List[str], gap_type: str) -> Dict[str, Any]:
        """Generate H1 and H2 structure for content"""
        
        # H1 is typically the title
        h1 = title
        
        # Extract main topic from title (better than generic keywords[0])
        # Remove common words and get meaningful topic
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        title_words = [w for w in title.lower().split() if w not in stop_words and len(w) > 3]
        
        # Use title words or fallback to keywords, prioritize project management terms
        pm_keywords = [k for k in keywords if k.lower() in ['gantt', 'agile', 'scrum', 'kanban', 'project', 'api', 'integration', 'workflow']]
        main_topic = pm_keywords[0].title() if pm_keywords else (title_words[0].title() if title_words else keywords[0].title())
        
        # Generate H2s based on gap type and topic
        h2s = []
        
        if gap_type == 'missing':
            # Comprehensive coverage structure
            h2s = [
                f"What is {main_topic}?",
                f"Why {main_topic} Matters for Project Management",
                f"Key Benefits of {main_topic}",
                f"How to Implement {main_topic}",
                f"Best Practices for {main_topic}",
                f"{main_topic} vs Alternatives",
                f"Common Challenges and Solutions",
                f"Getting Started with {main_topic}"
            ]
        
        elif gap_type == 'thin':
            # Depth expansion structure
            h2s = [
                f"Understanding {main_topic}",
                f"Advanced {main_topic} Features",
                f"Real-World {main_topic} Use Cases",
                f"Expert Tips for {main_topic}",
                f"Measuring {main_topic} Success",
                f"Tools and Resources"
            ]
        
        elif gap_type == 'outdated':
            # Update structure
            h2s = [
                f"What's New in {main_topic} (2025 Update)",
                f"Latest {main_topic} Trends",
                f"Updated Best Practices",
                f"New Features and Capabilities",
                f"Migration Guide",
                f"Future Roadmap"
            ]
        
        else:  # under-optimized
            # Optimization structure based on actual title context
            if 'api' in title.lower():
                h2s = [
                    "API Overview and Capabilities",
                    "Authentication and Authorization",
                    "API Endpoints and Methods",
                    "Code Examples and Integration",
                    "Rate Limits and Best Practices",
                    "Troubleshooting Common Issues"
                ]
            elif 'blog' in title.lower() or 'news' in title.lower():
                h2s = [
                    "Latest Updates and Announcements",
                    "Feature Highlights",
                    "Community Contributions",
                    "Tips and Tricks",
                    "Customer Success Stories",
                    "Upcoming Features"
                ]
            elif 'community' in title.lower() or 'customer' in title.lower():
                h2s = [
                    "Who Uses OpenProject",
                    "Success Stories and Case Studies",
                    "Community Contributions",
                    "Getting Support",
                    "Contributing to the Project",
                    "Join the Community"
                ]
            elif 'agile' in title.lower():
                h2s = [
                    "What is Agile Project Management",
                    "When to Use Agile Methods",
                    "Agile Features in OpenProject",
                    "Setting Up Agile Boards",
                    "Sprint Planning and Execution",
                    "Measuring Agile Success"
                ]
            else:
                h2s = [
                    f"Introduction to {main_topic}",
                    "Key Features and Benefits",
                    "Implementation Guide",
                    "Use Cases and Examples",
                    "Best Practices",
                    "Next Steps"
                ]
        
        return {
            'H1': h1,
            'H2': h2s[:8]  # Limit to 8 H2s
        }
    
    def suggest_media_assets(self, gap_type: str, keywords: List[str], title: str = "") -> List[str]:
        """Suggest appropriate media assets"""
        
        media_assets = []
        
        # Extract topic from keywords prioritizing PM terms
        pm_keywords = [k for k in keywords if k.lower() in ['gantt', 'agile', 'scrum', 'kanban', 'api', 'workflow', 'board']]
        topic = pm_keywords[0] if pm_keywords else keywords[0]
        
        # Context-specific hero image
        if 'api' in title.lower():
            media_assets.append("Screenshot: API documentation interface")
        elif 'gantt' in title.lower():
            media_assets.append("Screenshot: Gantt chart example")
        elif 'agile' in title.lower() or 'scrum' in title.lower():
            media_assets.append("Screenshot: Agile board with tasks")
        elif 'community' in title.lower() or 'customer' in title.lower():
            media_assets.append("Photo: Team collaboration or customer logos")
        else:
            media_assets.append(f"Hero image: {topic} overview")
        
        if gap_type == 'missing':
            media_assets.extend([
                f"Infographic: {keywords[0].title()} benefits overview",
                f"Diagram: How {keywords[0]} works",
                f"Video tutorial: Getting started with {keywords[0]}",
                f"Screenshot: {keywords[0]} interface/dashboard",
                f"Comparison chart: {keywords[0]} vs alternatives"
            ])
        
        elif gap_type == 'thin':
            media_assets.extend([
                f"Detailed infographic: {keywords[0]} process flow",
                f"Video: Advanced {keywords[0]} techniques",
                f"Multiple screenshots: Step-by-step guide",
                f"Data visualization: {keywords[0]} statistics",
                f"Expert interview video about {keywords[0]}"
            ])
        
        elif gap_type == 'outdated':
            media_assets.extend([
                f"Updated screenshot: New {keywords[0]} features",
                f"Timeline graphic: {keywords[0]} evolution",
                f"Video: What's new in {keywords[0]}",
                f"Before/after comparison images"
            ])
        
        else:  # under-optimized
            media_assets.extend([
                f"Optimized featured image with {keywords[0]}",
                f"Infographic: {keywords[0]} quick reference",
                f"Chart: {keywords[0]} performance metrics",
                f"Video embed: {keywords[0]} demonstration"
            ])
        
        return media_assets[:6]
    
    def suggest_cta(self, intent: str, gap_type: str) -> str:
        """Suggest appropriate call-to-action"""
        
        if intent == 'transactional':
            ctas = [
                "Start Your Free Trial Today",
                "Get Started Now",
                "Request a Demo",
                "See Pricing Options",
                "Contact Sales"
            ]
        elif intent == 'navigational':
            ctas = [
                "Visit Our Platform",
                "Access Your Account",
                "Explore Our Dashboard",
                "Learn More"
            ]
        else:  # informational
            ctas = [
                "Download Our Free Guide",
                "Subscribe for Updates",
                "Read Related Articles",
                "Join Our Newsletter",
                "Get Expert Insights"
            ]
        
        return ctas[0]
    
    def estimate_traffic_impact(self, impact_score: int, keywords: List[str]) -> str:
        """Estimate potential traffic impact"""
        
        # Base estimate on impact score
        if impact_score >= 80:
            monthly_visits = f"1,000-3,000"
            qualifier = "High"
        elif impact_score >= 60:
            monthly_visits = f"500-1,500"
            qualifier = "Medium-High"
        elif impact_score >= 40:
            monthly_visits = f"200-800"
            qualifier = "Medium"
        else:
            monthly_visits = f"50-300"
            qualifier = "Low-Medium"
        
        return f"{qualifier} impact: Estimated {monthly_visits} monthly organic visits"
    
    def suggest_resources(self, difficulty: str, gap_type: str) -> List[str]:
        """Suggest required resources for content creation"""
        
        resources = ["Content writer/strategist"]
        
        if difficulty == 'high':
            resources.extend([
                "Subject matter expert (SME) review",
                "Professional editor",
                "Graphic designer",
                "Video production team",
                "SEO specialist"
            ])
        elif difficulty == 'medium':
            resources.extend([
                "SME consultation",
                "Editor/proofreader",
                "Graphic designer",
                "SEO review"
            ])
        else:  # low
            resources.extend([
                "Editor/proofreader",
                "Basic graphics/stock images"
            ])
        
        if gap_type == 'thin':
            resources.append("Research analyst for competitive analysis")
        elif gap_type == 'outdated':
            resources.append("Fact-checker for updated information")
        
        return resources
    
    def generate_url_slug(self, title: str) -> str:
        """Generate SEO-friendly URL slug"""
        
        # Convert to lowercase
        slug = title.lower()
        
        # Remove special characters
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        
        # Remove multiple hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Trim hyphens from ends
        slug = slug.strip('-')
        
        # Limit length
        if len(slug) > 60:
            slug = slug[:60].rsplit('-', 1)[0]
        
        return slug
    
    def calculate_publish_priority(self, 
                                  impact_score: int,
                                  difficulty: str,
                                  gap_type: str,
                                  days_offset: int = 0) -> str:
        """Calculate suggested publish date based on priority"""
        
        # Priority calculation
        if gap_type == 'outdated':
            # Urgent: update soon
            days = 7 + days_offset
        elif impact_score >= 80 and difficulty == 'low':
            # High impact, easy wins first
            days = 14 + days_offset
        elif impact_score >= 70:
            # High impact, prioritize
            days = 21 + days_offset
        elif difficulty == 'low':
            # Quick wins
            days = 30 + days_offset
        else:
            # Standard timeline
            days = 45 + days_offset
        
        publish_date = datetime.now() + timedelta(days=days)
        return publish_date.strftime('%Y-%m-%d')
    
    def generate_recommendation(self, 
                               gap: Dict[str, Any],
                               index: int = 0) -> Dict[str, Any]:
        """Generate comprehensive recommendation from gap"""
        
        title = gap['title']
        keywords = gap['keywords'][:10]
        gap_type = gap['gap_type']
        impact_score = gap['impact_score']
        difficulty = gap['difficulty']
        
        # Classify intent
        intent = self.classify_search_intent(keywords, title)
        
        # Generate outline
        outline = self.generate_outline(title, keywords, gap_type)
        
        # Suggest media
        media_assets = self.suggest_media_assets(gap_type, keywords, title)
        
        # Suggest CTA
        cta = self.suggest_cta(intent, gap_type)
        
        # Estimate traffic
        traffic_impact = self.estimate_traffic_impact(impact_score, keywords)
        
        # Suggest resources
        resources = self.suggest_resources(difficulty, gap_type)
        
        # Generate URL slug
        slug = self.generate_url_slug(title)
        
        # Calculate publish priority
        publish_priority = self.calculate_publish_priority(impact_score, difficulty, gap_type, index * 7)
        
        # Identify competitive advantage
        competitive_advantage = f"Addresses {gap_type} gap with {gap.get('competitor_coverage', 'significant competitor coverage')}. {gap.get('reason', '')}"
        
        return {
            'title': title,
            'slug': slug,
            'target_keywords': keywords,
            'search_intent': intent,
            'impact_score': impact_score,
            'difficulty': difficulty,
            'outline': outline,
            'media_assets': media_assets,
            'cta': cta,
            'resources_needed': resources,
            'publish_priority': publish_priority,
            'traffic_impact': traffic_impact,
            'competitive_advantage': competitive_advantage,
            'gap_addressed': gap_type
        }
    
    def generate_recommendations(self, 
                                gaps: List[Dict[str, Any]],
                                min_recommendations: int = 10) -> List[Dict[str, Any]]:
        """Generate all recommendations from gaps"""
        
        recommendations = []
        
        # Ensure we have enough gaps
        gaps_to_process = gaps[:max(min_recommendations, len(gaps))]
        
        for index, gap in enumerate(gaps_to_process):
            recommendation = self.generate_recommendation(gap, index)
            recommendations.append(recommendation)
        
        # Sort by impact score and publish priority
        recommendations = sorted(
            recommendations,
            key=lambda x: (-x['impact_score'], x['publish_priority'])
        )
        
        return recommendations


def main():
    """Example usage"""
    print("Recommendation Generator initialized")
    
    # Example gap
    example_gap = {
        'title': 'Complete Guide to Content Marketing Strategy',
        'gap_type': 'missing',
        'keywords': ['content marketing', 'strategy', 'planning', 'execution', 'metrics'],
        'impact_score': 85,
        'difficulty': 'medium',
        'reason': 'Covered by 8 competitors but absent from your content',
        'competitor_coverage': '8/10 competitors'
    }
    
    generator = RecommendationGenerator()
    recommendation = generator.generate_recommendation(example_gap)
    
    print("\nExample Recommendation:")
    print(json.dumps(recommendation, indent=2))


if __name__ == "__main__":
    main()
