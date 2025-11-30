"""
Content Gap Analysis - Interactive Dashboard Specifications
JSON specifications for 5 dashboard visualizations with complete encoding details
"""

import json
from typing import Dict, Any


class DashboardSpecGenerator:
    """Generates JSON specifications for interactive dashboards"""
    
    def __init__(self):
        """Initialize dashboard spec generator"""
        pass
    
    def generate_gap_table_spec(self) -> Dict[str, Any]:
        """
        Specification for interactive gap analysis table
        Shows all identified gaps with filtering and sorting capabilities
        """
        return {
            "chart_type": "interactive_table",
            "title": "Content Gap Analysis Table",
            "description": "Comprehensive view of all identified content gaps with impact scores, difficulty levels, and gap types. Enables filtering and prioritization of content opportunities.",
            "data_source": "gaps",
            "columns": [
                {
                    "field": "title",
                    "header": "Gap Title",
                    "type": "string",
                    "width": "300px",
                    "sortable": True,
                    "filterable": True
                },
                {
                    "field": "gap_type",
                    "header": "Gap Type",
                    "type": "categorical",
                    "width": "120px",
                    "sortable": True,
                    "filterable": True,
                    "color_encoding": {
                        "missing": "#e74c3c",
                        "thin": "#f39c12",
                        "outdated": "#3498db",
                        "under-optimized": "#9b59b6"
                    }
                },
                {
                    "field": "impact_score",
                    "header": "Impact Score",
                    "type": "numeric",
                    "width": "120px",
                    "sortable": True,
                    "filterable": True,
                    "encoding": {
                        "type": "color_gradient",
                        "domain": [0, 100],
                        "range": ["#ecf0f1", "#27ae60"],
                        "format": "0"
                    },
                    "cell_renderer": "progress_bar"
                },
                {
                    "field": "difficulty",
                    "header": "Difficulty",
                    "type": "categorical",
                    "width": "100px",
                    "sortable": True,
                    "filterable": True,
                    "color_encoding": {
                        "low": "#2ecc71",
                        "medium": "#f39c12",
                        "high": "#e74c3c"
                    }
                },
                {
                    "field": "keywords",
                    "header": "Top Keywords",
                    "type": "array",
                    "width": "250px",
                    "renderer": "tag_list",
                    "max_display": 5
                },
                {
                    "field": "competitor_coverage",
                    "header": "Competitor Coverage",
                    "type": "string",
                    "width": "150px",
                    "sortable": True
                }
            ],
            "interactions": {
                "row_click": "show_details",
                "sort_default": {"field": "impact_score", "order": "desc"},
                "filters": ["gap_type", "difficulty"],
                "search": True,
                "export": ["csv", "json", "pdf"]
            },
            "tooltip": {
                "enabled": True,
                "fields": ["title", "reason", "impact_score", "difficulty"],
                "format": "multi_line"
            },
            "pagination": {
                "enabled": True,
                "page_size": 20,
                "show_all_option": True
            }
        }
    
    def generate_topic_heatmap_spec(self) -> Dict[str, Any]:
        """
        Specification for topic coverage heatmap
        Visualizes topic overlap between your content and competitors
        """
        return {
            "chart_type": "heatmap",
            "title": "Topic Coverage Heatmap",
            "description": "Comparative analysis of topic coverage between your organization and competitors. Darker cells indicate higher coverage intensity. Identifies topic gaps and opportunities at a glance.",
            "data_source": "topic_comparison",
            "x_field": "competitor_source",
            "y_field": "topic_label",
            "value_field": "coverage_score",
            "encoding": {
                "x": {
                    "field": "competitor_source",
                    "type": "nominal",
                    "axis": {
                        "title": "Content Source",
                        "label_angle": -45,
                        "label_align": "right"
                    }
                },
                "y": {
                    "field": "topic_label",
                    "type": "nominal",
                    "axis": {
                        "title": "Content Topic"
                    },
                    "sort": "descending"
                },
                "color": {
                    "field": "coverage_score",
                    "type": "quantitative",
                    "scale": {
                        "scheme": "viridis",
                        "domain": [0, 100],
                        "range": ["#f0f0f0", "#1a1a1a"]
                    },
                    "legend": {
                        "title": "Coverage Intensity",
                        "format": "0"
                    }
                }
            },
            "tooltip": {
                "enabled": True,
                "fields": [
                    {"field": "topic_label", "title": "Topic"},
                    {"field": "competitor_source", "title": "Source"},
                    {"field": "coverage_score", "title": "Coverage Score", "format": ".1f"},
                    {"field": "document_count", "title": "Documents"},
                    {"field": "keyword_count", "title": "Keywords"}
                ]
            },
            "dimensions": {
                "width": 800,
                "height": 600,
                "cell_size": "auto"
            },
            "interactions": {
                "cell_click": "show_topic_details",
                "zoom": True,
                "pan": True
            },
            "annotations": {
                "highlight_gaps": True,
                "gap_threshold": 30,
                "gap_indicator": "border"
            }
        }
    
    def generate_impact_chart_spec(self) -> Dict[str, Any]:
        """
        Specification for impact vs difficulty scatter plot
        Helps prioritize content based on ROI potential
        """
        return {
            "chart_type": "scatter_plot",
            "title": "Content Opportunity Matrix: Impact vs. Difficulty",
            "description": "Strategic prioritization view showing content opportunities plotted by business impact and creation difficulty. Quadrants identify quick wins (high impact, low difficulty), strategic investments (high impact, high difficulty), and low priorities.",
            "data_source": "recommendations",
            "x_field": "difficulty_numeric",
            "y_field": "impact_score",
            "encoding": {
                "x": {
                    "field": "difficulty_numeric",
                    "type": "quantitative",
                    "axis": {
                        "title": "Creation Difficulty",
                        "values": [1, 2, 3],
                        "labels": ["Low", "Medium", "High"],
                        "grid": True
                    },
                    "scale": {
                        "domain": [0.5, 3.5]
                    }
                },
                "y": {
                    "field": "impact_score",
                    "type": "quantitative",
                    "axis": {
                        "title": "Business Impact Score",
                        "grid": True
                    },
                    "scale": {
                        "domain": [0, 100]
                    }
                },
                "color": {
                    "field": "gap_type",
                    "type": "nominal",
                    "scale": {
                        "domain": ["missing", "thin", "outdated", "under-optimized"],
                        "range": ["#e74c3c", "#f39c12", "#3498db", "#9b59b6"]
                    },
                    "legend": {
                        "title": "Gap Type"
                    }
                },
                "size": {
                    "field": "keyword_count",
                    "type": "quantitative",
                    "scale": {
                        "range": [50, 400]
                    },
                    "legend": {
                        "title": "Keyword Opportunities"
                    }
                },
                "opacity": {
                    "value": 0.7
                }
            },
            "tooltip": {
                "enabled": True,
                "fields": [
                    {"field": "title", "title": "Content Title"},
                    {"field": "impact_score", "title": "Impact Score"},
                    {"field": "difficulty", "title": "Difficulty"},
                    {"field": "gap_type", "title": "Gap Type"},
                    {"field": "traffic_impact", "title": "Traffic Potential"},
                    {"field": "publish_priority", "title": "Target Date"}
                ]
            },
            "quadrants": {
                "enabled": True,
                "x_split": 2,
                "y_split": 60,
                "labels": {
                    "top_left": "Quick Wins ⭐",
                    "top_right": "Strategic Investments 🎯",
                    "bottom_left": "Low Priority",
                    "bottom_right": "Consider Carefully"
                },
                "colors": {
                    "top_left": "rgba(46, 204, 113, 0.1)",
                    "top_right": "rgba(52, 152, 219, 0.1)",
                    "bottom_left": "rgba(189, 195, 199, 0.1)",
                    "bottom_right": "rgba(241, 196, 15, 0.1)"
                }
            },
            "dimensions": {
                "width": 900,
                "height": 600
            },
            "interactions": {
                "point_click": "show_recommendation_details",
                "zoom": True,
                "brush_select": True
            }
        }
    
    def generate_model_metrics_spec(self) -> Dict[str, Any]:
        """
        Specification for ML model performance dashboard
        Shows precision, recall, F1, confusion matrix
        """
        return {
            "chart_type": "composite_metrics_dashboard",
            "title": "ML Model Performance Metrics",
            "description": "Comprehensive evaluation metrics for the content gap classification model. Displays precision, recall, F1 scores, and confusion matrix to validate model accuracy meets ≥80% threshold.",
            "data_source": "model_metrics",
            "components": [
                {
                    "component_type": "metric_cards",
                    "layout": "horizontal",
                    "cards": [
                        {
                            "title": "Accuracy",
                            "field": "accuracy",
                            "format": ".2%",
                            "threshold": 0.80,
                            "color_encoding": {
                                "above_threshold": "#27ae60",
                                "below_threshold": "#e74c3c"
                            },
                            "icon": "✓",
                            "subtitle": "Overall Classification Accuracy"
                        },
                        {
                            "title": "Precision (Macro)",
                            "field": "precision",
                            "format": ".2%",
                            "threshold": 0.75,
                            "color_encoding": {
                                "above_threshold": "#27ae60",
                                "below_threshold": "#f39c12"
                            },
                            "subtitle": "Average Precision Across Classes"
                        },
                        {
                            "title": "Recall (Macro)",
                            "field": "recall",
                            "format": ".2%",
                            "threshold": 0.75,
                            "color_encoding": {
                                "above_threshold": "#27ae60",
                                "below_threshold": "#f39c12"
                            },
                            "subtitle": "Average Recall Across Classes"
                        },
                        {
                            "title": "F1 Score (Macro)",
                            "field": "f1_macro",
                            "format": ".2%",
                            "threshold": 0.75,
                            "color_encoding": {
                                "above_threshold": "#27ae60",
                                "below_threshold": "#f39c12"
                            },
                            "subtitle": "Harmonic Mean of Precision & Recall"
                        }
                    ]
                },
                {
                    "component_type": "confusion_matrix",
                    "title": "Classification Confusion Matrix",
                    "field": "confusion_matrix",
                    "labels": ["Missing", "Thin", "Outdated", "Under-Optimized"],
                    "encoding": {
                        "color": {
                            "scheme": "blues",
                            "legend_title": "Prediction Count"
                        },
                        "text": {
                            "show_values": True,
                            "format": "0",
                            "color": "auto"
                        }
                    },
                    "annotations": {
                        "show_diagonal": True,
                        "diagonal_color": "#27ae60"
                    }
                },
                {
                    "component_type": "bar_chart",
                    "title": "Per-Class Performance",
                    "data_source": "per_class_metrics",
                    "x_field": "gap_type",
                    "y_fields": ["precision", "recall", "f1_score"],
                    "encoding": {
                        "x": {
                            "field": "gap_type",
                            "type": "nominal",
                            "axis": {"title": "Gap Type"}
                        },
                        "y": {
                            "type": "quantitative",
                            "axis": {"title": "Score", "format": ".2f"},
                            "scale": {"domain": [0, 1]}
                        },
                        "color": {
                            "field": "metric",
                            "type": "nominal",
                            "scale": {
                                "domain": ["precision", "recall", "f1_score"],
                                "range": ["#3498db", "#e74c3c", "#2ecc71"]
                            }
                        }
                    },
                    "grouped": True
                },
                {
                    "component_type": "text_list",
                    "title": "Error Analysis: False Positives",
                    "field": "false_positives",
                    "max_items": 5,
                    "style": "compact"
                },
                {
                    "component_type": "text_list",
                    "title": "Error Analysis: False Negatives",
                    "field": "false_negatives",
                    "max_items": 5,
                    "style": "compact"
                }
            ],
            "layout": {
                "type": "grid",
                "rows": 3,
                "columns": 2
            },
            "dimensions": {
                "width": 1200,
                "height": 900
            }
        }
    
    def generate_timeline_spec(self) -> Dict[str, Any]:
        """
        Specification for content publication timeline
        Shows recommended publication schedule over 90 days
        """
        return {
            "chart_type": "gantt_timeline",
            "title": "90-Day Content Publication Roadmap",
            "description": "Strategic publication schedule showing prioritized content recommendations over the next 90 days. Color-coded by gap type with impact indicators for resource planning and stakeholder alignment.",
            "data_source": "recommendations",
            "start_date_field": "publish_priority",
            "duration_field": "estimated_duration_days",
            "task_field": "title",
            "encoding": {
                "y": {
                    "field": "title",
                    "type": "nominal",
                    "axis": {
                        "title": "Content Piece",
                        "label_limit": 200
                    },
                    "sort": {"field": "publish_priority", "order": "ascending"}
                },
                "x": {
                    "field": "publish_priority",
                    "type": "temporal",
                    "axis": {
                        "title": "Publication Date",
                        "format": "%b %d, %Y",
                        "grid": True,
                        "tick_count": "week"
                    },
                    "scale": {
                        "domain_method": "auto",
                        "nice": True
                    }
                },
                "color": {
                    "field": "gap_type",
                    "type": "nominal",
                    "scale": {
                        "domain": ["missing", "thin", "outdated", "under-optimized"],
                        "range": ["#e74c3c", "#f39c12", "#3498db", "#9b59b6"]
                    },
                    "legend": {
                        "title": "Gap Type"
                    }
                },
                "size": {
                    "field": "impact_score",
                    "type": "quantitative",
                    "scale": {
                        "range": [10, 30]
                    }
                }
            },
            "tooltip": {
                "enabled": True,
                "fields": [
                    {"field": "title", "title": "Content Title"},
                    {"field": "publish_priority", "title": "Target Date", "format": "%Y-%m-%d"},
                    {"field": "gap_type", "title": "Gap Type"},
                    {"field": "impact_score", "title": "Impact Score"},
                    {"field": "difficulty", "title": "Difficulty"},
                    {"field": "resources_needed", "title": "Resources Required"},
                    {"field": "traffic_impact", "title": "Traffic Potential"}
                ]
            },
            "milestones": {
                "enabled": True,
                "auto_generate": True,
                "interval": "week",
                "labels": ["Week 1", "Week 2", "Week 3", "etc."]
            },
            "grouping": {
                "enabled": True,
                "group_by": "gap_type",
                "collapsible": True
            },
            "dimensions": {
                "width": 1200,
                "height": 800
            },
            "interactions": {
                "task_click": "show_full_recommendation",
                "drag_to_reschedule": False,
                "zoom": True,
                "filter_by_date_range": True
            },
            "annotations": {
                "today_line": {
                    "enabled": True,
                    "color": "#e74c3c",
                    "style": "dashed"
                },
                "priority_markers": {
                    "enabled": True,
                    "high_impact_threshold": 80,
                    "marker": "⭐"
                }
            }
        }
    
    def generate_all_specs(self) -> Dict[str, Any]:
        """Generate all dashboard specifications"""
        
        return {
            "gap_table": self.generate_gap_table_spec(),
            "topic_heatmap": self.generate_topic_heatmap_spec(),
            "impact_chart": self.generate_impact_chart_spec(),
            "model_metrics": self.generate_model_metrics_spec(),
            "timeline": self.generate_timeline_spec()
        }


def main():
    """Generate and save dashboard specifications"""
    
    generator = DashboardSpecGenerator()
    
    # Generate all specs
    dashboard_specs = generator.generate_all_specs()
    
    # Save to file
    output_file = 'dashboards/dashboard_specifications.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard_specs, f, indent=2, ensure_ascii=False)
    
    print(f"Dashboard specifications generated: {output_file}")
    print(f"Total dashboards: {len(dashboard_specs)}")
    
    for name, spec in dashboard_specs.items():
        print(f"\n{name}:")
        print(f"  Type: {spec['chart_type']}")
        print(f"  Title: {spec['title']}")
        print(f"  Description: {spec['description'][:100]}...")


if __name__ == "__main__":
    main()
