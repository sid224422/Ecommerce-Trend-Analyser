"""
UI Component Library for Market Analytics System

Reusable components for visualizations, metrics, and UI elements.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional


def create_kpi_card(title: str, value: str, delta: Optional[str] = None, 
                    delta_color: str = "normal", help_text: Optional[str] = None):
    """Create a KPI metric card with optional delta and help text."""
    col = st.columns(1)[0]
    with col:
        if help_text:
            st.metric(title, value, delta, delta_color=delta_color, help=help_text)
        else:
            st.metric(title, value, delta, delta_color=delta_color)


def create_dashboard_summary(results: Dict) -> None:
    """Create a dashboard summary section with key metrics."""
    st.header("📊 Executive Dashboard")
    
    brand_result = results["agents"]["brand"]
    pricing_result = results["agents"]["pricing"]
    feature_result = results["agents"]["feature"]
    gap_result = results["agents"]["gap"]
    
    # Calculate key metrics
    total_records = results.get("total_records", 0)
    top_brand = brand_result["results"]["top_brands"][0] if brand_result["results"]["top_brands"] else None
    pricing_stats = pricing_result["results"]["price_statistics"]
    gaps_count = gap_result["results"]["identified_gaps_count"]
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Records Analyzed",
            f"{total_records:,}",
            delta=None,
            help="Total number of valid records in the dataset"
        )
    
    with col2:
        market_leader = top_brand["brand"] if top_brand else "N/A"
        market_share = f"{top_brand['confidence']*100:.1f}%" if top_brand else "0%"
        st.metric(
            "Market Leader",
            market_leader,
            delta=market_share,
            delta_color="off",
            help="Brand with highest market share"
        )
    
    with col3:
        avg_price = pricing_stats.get("mean_price", 0)
        st.metric(
            "Average Price",
            f"${avg_price:,.2f}",
            delta=None,
            help="Mean price across all products"
        )
    
    with col4:
        st.metric(
            "Market Gaps Identified",
            f"{gaps_count}",
            delta=None,
            help="Number of significant market opportunities found"
        )
    
    # Additional summary stats
    col5, col6, col7 = st.columns(3)
    
    with col5:
        unique_brands = brand_result["results"]["total_unique_brands"]
        st.metric(
            "Unique Brands",
            f"{unique_brands}",
            delta=None,
            help="Total number of different brands in dataset"
        )
    
    with col6:
        unique_features = feature_result["results"]["total_unique_features"]
        st.metric(
            "Unique Features",
            f"{unique_features}",
            delta=None,
            help="Total number of different features identified"
        )
    
    with col7:
        price_range = pricing_stats["max_price"] - pricing_stats["min_price"]
        st.metric(
            "Price Range",
            f"${price_range:,.2f}",
            delta=None,
            help="Difference between highest and lowest prices"
        )


def create_brand_pie_chart(brands_df: pd.DataFrame) -> go.Figure:
    """Create a pie chart for brand distribution."""
    fig = px.pie(
        brands_df,
        values="count",
        names="brand",
        title="Brand Market Share Distribution",
        hole=0.4
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


def create_price_histogram(prices: List[float], title: str = "Price Distribution") -> go.Figure:
    """Create a histogram for price distribution."""
    fig = px.histogram(
        x=prices,
        nbins=30,
        title=title,
        labels={"x": "Price ($)", "y": "Frequency"}
    )
    fig.update_layout(showlegend=False)
    return fig


def create_price_boxplot(prices: List[float], title: str = "Price Distribution Box Plot") -> go.Figure:
    """Create a box plot for price distribution."""
    fig = go.Figure()
    fig.add_trace(go.Box(y=prices, name="Prices", boxmean='sd'))
    fig.update_layout(
        title=title,
        yaxis_title="Price ($)",
        showlegend=False
    )
    return fig


def create_feature_bar_chart(features_df: pd.DataFrame, horizontal: bool = True) -> go.Figure:
    """Create a bar chart for features."""
    if horizontal:
        fig = px.bar(
            features_df,
            x="count",
            y="feature",
            orientation='h',
            title="Top Features by Count",
            labels={"count": "Count", "feature": "Feature"}
        )
    else:
        fig = px.bar(
            features_df,
            x="feature",
            y="count",
            title="Top Features by Count",
            labels={"count": "Count", "feature": "Feature"}
        )
    fig.update_layout(showlegend=False)
    return fig


def create_gap_visualization(gaps: List[Dict], top_n: int = 10) -> Optional[go.Figure]:
    """Create visualization for market gaps."""
    if not gaps:
        return None
    
    # Get top N gaps
    top_gaps = sorted(gaps, key=lambda x: x['gap_score'])[:top_n]
    
    gap_df = pd.DataFrame(top_gaps)
    
    fig = px.bar(
        gap_df,
        x="gap_score",
        y="brand",
        color="gap_score",
        color_continuous_scale="Reds",
        orientation='h',
        title="Top Market Gaps (Most Significant)",
        labels={"gap_score": "Gap Score", "brand": "Brand"},
        hover_data=["feature", "observed_count", "expected_count"]
    )
    fig.update_layout(showlegend=False)
    return fig


def create_data_quality_metrics(df: pd.DataFrame) -> Dict:
    """Calculate and return data quality metrics."""
    total_rows = len(df)
    total_cols = len(df.columns)
    missing_values = df.isnull().sum().sum()
    missing_percentage = (missing_values / (total_rows * total_cols)) * 100
    duplicate_rows = df.duplicated().sum()
    duplicate_percentage = (duplicate_rows / total_rows) * 100 if total_rows > 0 else 0
    
    quality_score = 100 - (missing_percentage + duplicate_percentage)
    quality_score = max(0, min(100, quality_score))
    
    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "missing_values": missing_values,
        "missing_percentage": missing_percentage,
        "duplicate_rows": duplicate_rows,
        "duplicate_percentage": duplicate_percentage,
        "quality_score": quality_score
    }


def display_data_quality_metrics(df: pd.DataFrame, cleaned_df: pd.DataFrame) -> None:
    """Display data quality metrics before and after cleaning."""
    with st.expander("📈 Data Quality Metrics", expanded=False):
        before_metrics = create_data_quality_metrics(df)
        after_metrics = create_data_quality_metrics(cleaned_df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📥 Before Cleaning")
            st.metric(
                "Total Rows", 
                f"{before_metrics['total_rows']:,}",
                help="Total number of rows in the dataset"
            )
            
            # Missing values - lower is better
            missing_delta = f"{before_metrics['missing_percentage']:.1f}%"
            missing_color = "normal" if before_metrics['missing_percentage'] == 0 else "inverse"
            st.metric(
                "Missing Values", 
                f"{before_metrics['missing_values']:,}", 
                delta=missing_delta,
                delta_color=missing_color,
                help="Number and percentage of missing values"
            )
            
            # Duplicate rows - lower is better
            dup_delta = f"{before_metrics['duplicate_percentage']:.1f}%"
            dup_color = "normal" if before_metrics['duplicate_rows'] == 0 else "inverse"
            st.metric(
                "Duplicate Rows",
                f"{before_metrics['duplicate_rows']:,}",
                delta=dup_delta,
                delta_color=dup_color,
                help="Number and percentage of duplicate rows"
            )
            
            # Quality score - higher is better
            quality_delta = f"{before_metrics['quality_score']:.1f}/100"
            quality_color = "normal" if before_metrics['quality_score'] >= 90 else ("off" if before_metrics['quality_score'] >= 70 else "inverse")
            st.metric(
                "Quality Score",
                f"{before_metrics['quality_score']:.1f}/100",
                help="Overall data quality score (0-100)"
            )
        
        with col2:
            st.subheader("✨ After Cleaning")
            rows_removed = before_metrics['total_rows'] - after_metrics['total_rows']
            rows_delta = f"-{rows_removed}" if rows_removed > 0 else None
            st.metric(
                "Total Rows",
                f"{after_metrics['total_rows']:,}",
                delta=rows_delta,
                delta_color="inverse" if rows_removed > 0 else "off",
                help="Total number of rows after cleaning"
            )
            
            # Missing values after cleaning
            missing_after_delta = f"{after_metrics['missing_percentage']:.1f}%"
            missing_after_color = "normal" if after_metrics['missing_percentage'] == 0 else "inverse"
            st.metric(
                "Missing Values",
                f"{after_metrics['missing_values']:,}",
                delta=missing_after_delta,
                delta_color=missing_after_color,
                help="Number and percentage of missing values after cleaning"
            )
            
            # Duplicate rows after cleaning
            dup_after_delta = f"{after_metrics['duplicate_percentage']:.1f}%"
            dup_after_color = "normal" if after_metrics['duplicate_rows'] == 0 else "inverse"
            st.metric(
                "Duplicate Rows",
                f"{after_metrics['duplicate_rows']:,}",
                delta=dup_after_delta,
                delta_color=dup_after_color,
                help="Number and percentage of duplicate rows after cleaning"
            )
            
            # Quality score after cleaning
            quality_improvement = after_metrics['quality_score'] - before_metrics['quality_score']
            quality_delta_str = f"+{quality_improvement:.1f}" if quality_improvement > 0 else None
            quality_after_color = "normal" if quality_improvement > 0 else "off"
            st.metric(
                "Quality Score",
                f"{after_metrics['quality_score']:.1f}/100",
                delta=quality_delta_str,
                delta_color=quality_after_color,
                help="Overall data quality score after cleaning"
            )


def create_column_mapping_sidebar(df: pd.DataFrame) -> Dict[str, str]:
    """Auto-detect columns, only show dropdowns if needed."""
    
    columns = list(df.columns)
    
    # Auto-detect with multiple keyword matching
    brand_keywords = ['brand', 'manufacturer', 'company', 'maker', 'vendor']
    price_keywords = ['price', 'cost', 'amount', 'usd', 'dollar', 'retail']
    feature_keywords = ['feature', 'spec', 'attribute', 'specification', 'property']
    
    # Find matching columns (case-insensitive)
    brand_col = next((c for c in columns if any(kw in c.lower() for kw in brand_keywords)), None)
    price_col = next((c for c in columns if any(kw in c.lower() for kw in price_keywords)), None)
    feature_col = next((c for c in columns if any(kw in c.lower() for kw in feature_keywords)), None)
    
    # Check if all standard columns exist exactly
    has_standard_columns = (
        'brand' in columns and 
        'price' in columns and 
        'feature' in columns
    )
    
    # If all standard columns exist, use them automatically
    if has_standard_columns:
        st.sidebar.success("✅ Auto-detected: brand, price, feature")
        return {
            "brand": "brand",
            "price": "price",
            "feature": "feature"
        }
    
    # If auto-detected successfully with keywords, show confirmation
    if brand_col and price_col and feature_col:
        st.sidebar.success(f"✅ Auto-detected columns:")
        st.sidebar.caption(f"🏷️ Brand: `{brand_col}`  |  💰 Price: `{price_col}`  |  🔧 Feature: `{feature_col}`")
        return {
            "brand": brand_col,
            "price": price_col,
            "feature": feature_col
        }
    
    # Only show dropdowns if auto-detection failed
    st.sidebar.warning("⚠️ Could not auto-detect all columns. Please select manually:")
    st.sidebar.markdown("**📋 Column Mapping:**")
    
    brand_column = st.sidebar.selectbox(
        "🏷️ Brand Column",
        columns,
        index=columns.index(brand_col) if brand_col else 0,
        help="Product brands (e.g., Samsung, Apple)"
    )
    
    price_column = st.sidebar.selectbox(
        "💰 Price Column",
        columns,
        index=columns.index(price_col) if price_col else 0,
        help="Product prices (e.g., 299.99)"
    )
    
    feature_column = st.sidebar.selectbox(
        "🔧 Feature Column",
        columns,
        index=columns.index(feature_col) if feature_col else 0,
        help="Product features (e.g., 5G+OLED)"
    )
    
    return {
        "brand": brand_column,
        "price": price_column,
        "feature": feature_column
    }


def create_analysis_parameters_sidebar() -> Dict:
    """Create sidebar for analysis parameters."""
    st.sidebar.subheader("🔧 Analysis Parameters")
    
    top_n_brands = st.sidebar.slider(
        "Top N Brands",
        min_value=5,
        max_value=20,
        value=10,
        step=1,
        help="Number of top brands to analyze"
    )
    
    top_n_features = st.sidebar.slider(
        "Top N Features",
        min_value=5,
        max_value=30,
        value=15,
        step=1,
        help="Number of top features to analyze"
    )
    
    gap_threshold = st.sidebar.slider(
        "Gap Threshold",
        min_value=-1.0,
        max_value=0.0,
        value=-0.5,
        step=0.1,
        help="Threshold for identifying significant gaps (lower = more strict)"
    )
    
    return {
        "top_n_brands": top_n_brands,
        "top_n_features": top_n_features,
        "gap_threshold": gap_threshold
    }


def create_export_options_sidebar() -> Dict:
    """Create sidebar for export options."""
    st.sidebar.subheader("💾 Export Options")
    
    export_format = st.sidebar.radio(
        "Export Format",
        ["JSON", "CSV", "Excel", "PDF"],
        help="Choose the format for exporting results"
    )
    
    include_charts = st.sidebar.checkbox(
        "Include Charts",
        value=False,
        help="Include visualizations in export (for PDF/Excel)"
    )
    
    return {
        "format": export_format,
        "include_charts": include_charts
    }
