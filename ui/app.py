"""
Minimal Streamlit UI for Market Analytics System

Academic project UI for data upload, analysis, and visualization.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import json
from datetime import datetime
import os
import tempfile
import numpy as np

# #region agent log
# Debug logging setup
DEBUG_LOG_PATH = Path(__file__).parent.parent / ".cursor" / "debug.log"
def debug_log(location, message, data=None, hypothesis_id=None):
    try:
        import json as json_lib
        log_entry = {
            "timestamp": datetime.now().timestamp() * 1000,
            "location": location,
            "message": message,
            "data": data or {},
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": hypothesis_id
        }
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json_lib.dumps(log_entry) + "\n")
    except:
        pass
# #endregion

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.ingestion import read_csv_file
from core.validator import validate_and_clean
from core.orchestrator import run_all_agents
from llm.summarizer import summarize_agent_results

# Import enhanced components
from ui.components import (
    create_dashboard_summary,
    create_brand_pie_chart,
    create_price_histogram,
    create_price_boxplot,
    create_feature_bar_chart,
    create_gap_visualization,
    display_data_quality_metrics,
    create_column_mapping_sidebar,
    create_analysis_parameters_sidebar,
    create_export_options_sidebar
)
from ui.export_utils import (
    export_to_json,
    export_to_csv,
    export_to_excel,
    export_to_pdf
)

# Enable caching for expensive operations
@st.cache_data
def cached_read_csv(file_path: str):
    """Cached CSV reading."""
    return read_csv_file(file_path)

@st.cache_data
def cached_validate_and_clean(df: pd.DataFrame, cleaning_strategy: str, remove_dupes: bool):
    """Cached data validation and cleaning."""
    return validate_and_clean(df, cleaning_strategy=cleaning_strategy, remove_dupes=remove_dupes)

# Page configuration
st.set_page_config(
    page_title="Market Analytics System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling and contrast
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Metric styling with better contrast */
    .stMetric {
        background-color: transparent;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid rgba(250, 250, 250, 0.1);
    }
    
    /* Ensure text is readable */
    .stMetric > div > div {
        color: inherit !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: inherit !important;
    }
    
    .stMetric [data-testid="stMetricLabel"] {
        color: inherit !important;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        color: inherit !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
    }
    
    /* Better contrast for delta indicators */
    [data-testid="stMetricDelta"] svg {
        opacity: 1;
    }
    
    /* Table styling for better readability */
    .dataframe {
        border-collapse: collapse;
        width: 100%;
    }
    
    .dataframe th {
        background-color: rgba(250, 250, 250, 0.1);
        font-weight: bold;
        padding: 8px;
    }
    
    .dataframe td {
        padding: 8px;
    }
    
    /* Ensure buttons are visible */
    .stDownloadButton > button {
        background-color: #1f77b4;
        color: white;
        border: none;
    }
    
    .stDownloadButton > button:hover {
        background-color: #1565c0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Market Analytics System")
st.markdown("**Enhanced Analytics Dashboard** - Upload CSV data for comprehensive market analysis")

# Sidebar configuration (initialize defaults)
if 'column_mapping' not in st.session_state:
    st.session_state.column_mapping = {"brand": "brand", "price": "price", "feature": "feature"}
if 'analysis_params' not in st.session_state:
    st.session_state.analysis_params = {"top_n_brands": 10, "top_n_features": 15, "gap_threshold": -0.5}
if 'export_options' not in st.session_state:
    st.session_state.export_options = {"format": "JSON", "include_charts": False}

# CSV Upload
st.header("📁 Data Upload")
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'], help="Upload a CSV file with market data (brand, price, feature columns)")

if uploaded_file is not None:
    try:
        # Save uploaded file temporarily
        # #region agent log
        debug_log("ui/app.py:42", "Creating temp file", {"cwd": str(Path.cwd())}, "A")
        # #endregion
        temp_path = Path(tempfile.gettempdir()) / f"temp_upload_{os.getpid()}.csv"
        # #region agent log
        debug_log("ui/app.py:44", "Temp file path created", {"temp_path": str(temp_path), "exists": temp_path.exists()}, "A")
        # #endregion
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        # #region agent log
        debug_log("ui/app.py:47", "Temp file written", {"temp_path": str(temp_path), "size": temp_path.stat().st_size if temp_path.exists() else 0}, "A")
        # #endregion
        
        # Sidebar Configuration
        st.sidebar.header("⚙️ Configuration")
        
        # Ingest and validate
        with st.spinner("Loading data..."):
            df = cached_read_csv(str(temp_path))
        
        st.success(f"✅ File loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Get column mapping from sidebar
        try:
            column_mapping = create_column_mapping_sidebar(df.head(1))
            st.session_state.column_mapping = column_mapping
        except Exception as e:
            st.sidebar.warning(f"⚠️ Error reading column headers: {str(e)}")
            # Fallback to defaults with auto-detection
            column_mapping = {"brand": "brand", "price": "price", "feature": "feature"}
            if df is not None and len(df.columns) >= 3:
                # Try to auto-detect columns
                brand_col = next((c for c in df.columns if 'brand' in c.lower()), df.columns[0])
                price_col = next((c for c in df.columns if 'price' in c.lower()), df.columns[1] if len(df.columns) > 1 else df.columns[0])
                feature_col = next((c for c in df.columns if 'feature' in c.lower()), df.columns[2] if len(df.columns) > 2 else df.columns[0])
                column_mapping = {
                    "brand": brand_col,
                    "price": price_col,
                    "feature": feature_col
                }
            st.session_state.column_mapping = column_mapping
        
        # Get analysis parameters from sidebar
        analysis_params = create_analysis_parameters_sidebar()
        st.session_state.analysis_params = analysis_params
        
        # Get export options
        export_options = create_export_options_sidebar()
        st.session_state.export_options = export_options
        
        # LLM Summary option
        enable_llm = st.sidebar.checkbox("Enable AI Summary", value=False, help="Generate AI-powered summary using LLM")
        
        # Cleaning strategy
        cleaning_strategy = st.sidebar.selectbox(
            "Data Cleaning Strategy",
            ["drop_rows", "drop_columns", "keep"],
            index=0,
            help="Strategy for handling missing values"
        )
        
        # Ingest and validate
        with st.spinner("Loading data..."):
            df = cached_read_csv(str(temp_path))
        
        st.success(f"✅ File loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Preview with enhanced display
        col1, col2 = st.columns([2, 1])
        with col1:
            with st.expander("📋 Preview Data", expanded=True):
                st.dataframe(df.head(20), use_container_width=True)
        
        with col2:
            with st.expander("📊 Data Statistics"):
                st.metric("Total Rows", f"{len(df):,}")
                st.metric("Total Columns", len(df.columns))
                st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Validate and clean with progress
        with st.spinner("Validating and cleaning data..."):
            cleaned_df = cached_validate_and_clean(df, cleaning_strategy=cleaning_strategy, remove_dupes=True)
        
        st.info(f"✅ Validated: {len(cleaned_df)} rows after cleaning ({len(df) - len(cleaned_df)} rows removed)")
        
        # Display data quality metrics
        display_data_quality_metrics(df, cleaned_df)
        
        # Run analysis
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("Initializing analysis...")
                progress_bar.progress(10)
                
                # #region agent log
                debug_log("ui/app.py:64", "Before run_all_agents", {
                    "cleaned_df_rows": len(cleaned_df), 
                    "cleaned_df_cols": list(cleaned_df.columns),
                    "column_mapping": column_mapping,
                    "analysis_params": analysis_params
                }, "C")
                # #endregion
                
                status_text.text("Running brand analysis...")
                progress_bar.progress(25)
                
                status_text.text("Running pricing analysis...")
                progress_bar.progress(50)
                
                status_text.text("Running feature analysis...")
                progress_bar.progress(75)
                
                status_text.text("Running gap analysis...")
                
                # Run analysis with sidebar parameters
                results = run_all_agents(
                    cleaned_df,
                    brand_column=column_mapping["brand"],
                    price_column=column_mapping["price"],
                    feature_column=column_mapping["feature"],
                    top_n_brands=analysis_params["top_n_brands"],
                    top_n_features=analysis_params["top_n_features"],
                    gap_threshold=analysis_params["gap_threshold"]
                )
                
                # #region agent log
                debug_log("ui/app.py:66", "After run_all_agents", {
                    "results_keys": list(results.keys()) if results else None, 
                    "has_agents": "agents" in results if results else False
                }, "C")
                # #endregion
                
                progress_bar.progress(100)
                status_text.text("Analysis complete!")
                st.success("✅ Analysis complete!")
                
                # Store results in session state
                st.session_state['analysis_results'] = results
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Error during analysis: {str(e)}")
                # #region agent log
                debug_log("ui/app.py:error", "Analysis error", {"error": str(e)}, "E")
                # #endregion
                results = None
                
            if results:
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Dashboard Summary
                create_dashboard_summary(results)
            
                # Brand Analysis
                st.header("🏷️ Brand Analysis")
                
                # Explanation expander
                with st.expander("ℹ️ About Brand Analysis", expanded=False):
                    st.markdown("""
                    **Brand Analysis** shows the distribution of products across different brands in your dataset.
                    
                    **Confidence Score:** 
                    - Shows what percentage of total products belong to each brand
                    - Formula: `(Brand count) / (Total products) × 100`
                    - Higher confidence = more market share
                    
                    **Example:** If Samsung has 15 products out of 100 total, confidence = 15%
                    """)
                
                # #region agent log
                debug_log("ui/app.py:84", "Before accessing brand_result", {"results_has_agents": "agents" in results, "agents_keys": list(results.get("agents", {}).keys()) if results and "agents" in results else []}, "C")
                # #endregion
                brand_result = results["agents"]["brand"]
                # #region agent log
                debug_log("ui/app.py:86", "After accessing brand_result", {"brand_result_keys": list(brand_result.keys()) if brand_result else None, "has_results": "results" in brand_result if brand_result else False}, "C")
                # #endregion
                brand_data = brand_result["results"]["top_brands"]
                # #region agent log
                debug_log("ui/app.py:88", "Before creating brands_df", {"brand_data_type": type(brand_data).__name__, "brand_data_length": len(brand_data) if isinstance(brand_data, list) else "N/A"}, "D")
                # #endregion
                
                # Table
                brands_df = pd.DataFrame(brand_data)
                # #region agent log
                debug_log("ui/app.py:89", "After creating brands_df", {"brands_df_columns": list(brands_df.columns), "brands_df_shape": brands_df.shape}, "D")
                # #endregion
                try:
                    st.dataframe(brands_df[["brand", "count", "confidence"]], use_container_width=True)
                except KeyError as e:
                    # #region agent log
                    debug_log("ui/app.py:92", "KeyError accessing brands_df columns", {"error": str(e), "available_columns": list(brands_df.columns)}, "D")
                    # #endregion
                    raise
                
                # Enhanced visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Bar chart
                    fig_bar = px.bar(brands_df, x="brand", y="count", title="Brand Distribution")
                    fig_bar.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    # Pie chart
                    fig_pie = create_brand_pie_chart(brands_df)
                    st.plotly_chart(fig_pie, use_container_width=True)
            
                # Pricing Metrics
                st.header("💰 Pricing Analysis")
                # #region agent log
                debug_log("ui/app.py:97", "Before accessing pricing_result", {"results_has_agents": "agents" in results}, "C")
                # #endregion
                pricing_result = results["agents"]["pricing"]
                stats = pricing_result["results"]["price_statistics"]
                optimal = pricing_result["results"]["optimal_price_range"]
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Min Price", f"${stats['min_price']:.2f}", help="Lowest price in dataset")
                col2.metric("Max Price", f"${stats['max_price']:.2f}", help="Highest price in dataset")
                col3.metric("Mean Price", f"${stats['mean_price']:.2f}", help="Average price")
                col4.metric("Median Price", f"${stats['median_price']:.2f}", help="Middle price value")
                
                col5, col6 = st.columns(2)
                with col5:
                    st.metric("Optimal Range", f"${optimal['optimal_range_min']:.2f} - ${optimal['optimal_range_max']:.2f}", 
                             help="Q1 to Q3 price range (optimal pricing zone)")
                with col6:
                    st.metric("Standard Deviation", f"${stats.get('std_price', 0):.2f}",
                             help="Price variability measure")
                
                # Enhanced pricing visualizations
                # Extract prices from cleaned_df for visualization
                try:
                    price_column = column_mapping["price"]
                    prices = cleaned_df[price_column].dropna().tolist()
                    
                    col7, col8 = st.columns(2)
                    with col7:
                        fig_hist = create_price_histogram(prices, "Price Distribution Histogram")
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    with col8:
                        fig_box = create_price_boxplot(prices, "Price Distribution Box Plot")
                        st.plotly_chart(fig_box, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not create price visualizations: {str(e)}")
            
                # Feature Analysis
                st.header("🔧 Feature Analysis")
                
                # Explanation expander
                with st.expander("ℹ️ About Feature Analysis", expanded=False):
                    st.markdown("""
                    **Feature Analysis** identifies the most common product features in your dataset.
                    
                    **Confidence Score:**
                    - Shows what percentage of products contain each feature
                    - Formula: `(Feature count) / (Total products) × 100`
                    - Higher confidence = more popular/common feature
                    
                    **Example:** If "5G" appears in 75 products out of 100, confidence = 75%
                    """)
                
                feature_result = results["agents"]["feature"]
                features = feature_result["results"]["top_features"]
                
                # Display as text/table
                features_df = pd.DataFrame(features)
                # #region agent log
                debug_log("ui/app.py:130", "After creating features_df", {"features_df_columns": list(features_df.columns), "features_df_shape": features_df.shape}, "D")
                # #endregion
                try:
                    st.dataframe(features_df[["feature", "count", "confidence"]], use_container_width=True)
                except KeyError as e:
                    # #region agent log
                    debug_log("ui/app.py:132", "KeyError accessing features_df columns", {"error": str(e), "available_columns": list(features_df.columns)}, "D")
                    # #endregion
                    raise
                
                # Enhanced feature visualization
                fig_feature = create_feature_bar_chart(features_df, horizontal=True)
                st.plotly_chart(fig_feature, use_container_width=True)
            
            # Gap Analysis
            st.header("🔍 Market Gap Analysis")
            
            # Explanation expander
            with st.expander("ℹ️ What is Gap Analysis?", expanded=False):
                st.markdown("""
                **Market Gap Analysis** identifies opportunities where certain brand-feature combinations are underrepresented in the market.
                
                **What does it mean?**
                - It finds when a large brand has very few products with a common feature
                - This indicates a potential market opportunity to add more products with that feature
                
                **Example:** 
                - If Samsung (large brand with 20 products) only has 1 product with "5G+OLED+128GB"
                - But this feature combination appears in 30 products overall
                - Then Samsung is missing a market opportunity!
                """)
            
            # #region agent log
            debug_log("ui/app.py:150", "Before accessing gap_result", {"results_has_agents": "agents" in results}, "C")
            # #endregion
            gap_result = results["agents"]["gap"]
            # #region agent log
            debug_log("ui/app.py:152", "After accessing gap_result", {"gap_result_keys": list(gap_result.keys()) if gap_result else None, "has_results": "results" in gap_result if gap_result else False}, "C")
            # #endregion
            gaps = gap_result["results"]["top_gaps"]
            total_combinations = gap_result["results"]["total_combinations"]
            gaps_count = gap_result["results"]["identified_gaps_count"]
            confidence = gap_result.get("confidence", 0.0)
            threshold = gap_result["results"].get("gap_threshold", -0.5)
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Combinations Analyzed", f"{total_combinations}")
            col2.metric("Gaps Identified", f"{gaps_count}")
            col3.metric("Confidence", f"{confidence*100:.1f}%")
            
            # Confidence explanation
            with st.expander("ℹ️ What is Confidence?", expanded=False):
                st.markdown(f"""
                **Confidence = {confidence*100:.1f}%**
                
                **Meaning:**
                - Confidence shows how much of your data was successfully analyzed
                - Formula: `(Valid brand-feature combinations) / (Total records) × 100`
                - **Higher is better** - means more data was usable
                
                **Your score:** {confidence*100:.1f}% of records contributed to gap analysis
                """)
            
            # Gap Score explanation
            with st.expander("ℹ️ Understanding Gap Score", expanded=False):
                st.markdown(f"""
                **Gap Score** measures how underrepresented a brand-feature combination is.
                
                **Formula:** `(Observed - Expected) / Expected`
                
                **How to interpret:**
                - **Negative scores** = Gap (underrepresented)
                - **Score ≤ {threshold}** = Significant gap (flagged)
                - **Score = 0** = Matches expectation perfectly
                - **Positive scores** = Overrepresented (strength, not a gap)
                
                **Gap Score Examples:**
                - **-0.84** = 84% below expected (major gap - big opportunity!)
                - **-0.50** = 50% below expected (threshold for flagging)
                - **-0.25** = 25% below expected (slightly low, not flagged)
                - **0.00** = Exactly as expected (balanced)
                - **+0.50** = 50% above expected (overrepresented - strength)
                
                **Calculation Example:**
                - Samsung has 17 products (large brand)
                - "5G+OLED+128GB" appears in 38 products total (common feature)
                - **Expected:** ~6.3 products (if independent)
                - **Observed:** 1 product
                - **Gap Score:** (1 - 6.3) / 6.3 = **-0.84** (84% gap!)
                """)
            
            if gaps:
                st.subheader("📋 Identified Market Gaps")
                st.info(f"Found **{gaps_count}** significant gap(s) where brands are underrepresented in feature combinations.")
                
                # Gap visualization
                gap_viz = create_gap_visualization(gaps, top_n=10)
                if gap_viz:
                    st.plotly_chart(gap_viz, use_container_width=True)
                
                # Display gaps in a better format
                for i, gap in enumerate(gaps, 1):
                    with st.container():
                        gap_pct = abs(gap['gap_score'] * 100)
                        
                        # Color code based on severity
                        if gap['gap_score'] <= -0.7:
                            severity = "🔴 **Major Gap**"
                            severity_desc = "(Very large opportunity - 70%+ below expected)"
                        elif gap['gap_score'] <= -0.6:
                            severity = "🟠 **Significant Gap**"
                            severity_desc = "(Large opportunity - 60%+ below expected)"
                        else:
                            severity = "🟡 **Moderate Gap**"
                            severity_desc = "(Noticeable opportunity - 50%+ below expected)"
                        
                        st.markdown(f"""
                        **Gap #{i}: {severity}** {severity_desc}
                        """)
                        
                        # Create columns for better layout
                        gap_col1, gap_col2 = st.columns([2, 1])
                        
                        with gap_col1:
                            st.markdown(f"""
                            - **Brand:** `{gap['brand']}`
                            - **Feature Combination:** `{gap['feature']}`
                            - **Gap Score:** `{gap['gap_score']:.4f}` ({gap_pct:.1f}% below expected)
                            """)
                        
                        with gap_col2:
                            st.markdown(f"""
                            **Observed:** {gap['observed_count']} product(s)  
                            **Expected:** {gap['expected_count']:.1f} product(s)  
                            **Difference:** -{gap['expected_count'] - gap['observed_count']:.1f} products
                            """)
                        
                        # Interpretation
                        st.markdown(f"""
                        💡 **Interpretation:** {gap['brand']} is **{gap_pct:.0f}% below** the expected number of products 
                        with the feature combination "{gap['feature']}". This represents a potential market opportunity 
                        to add approximately **{max(1, int(gap['expected_count'] - gap['observed_count']))} more product(s)** 
                        with this combination.
                        """)
                        
                        st.divider()
            else:
                st.info("✅ No significant market gaps identified. The market appears well-balanced - all brand-feature combinations are distributed as expected.")
            
            # LLM Summary
            st.header("🤖 AI Summary")
            
            if enable_llm:
                with st.spinner("Generating AI summary..."):
                    try:
                        # Convert agent results to list format for summarizer
                        agent_outputs = [
                            results["agents"]["brand"],
                            results["agents"]["pricing"],
                            results["agents"]["feature"],
                            results["agents"]["gap"]
                        ]
                        
                        summary_result = summarize_agent_results(agent_outputs)
                        
                        if summary_result.get('status') == 'success':
                            st.success("✅ Summary generated")
                            st.markdown(summary_result['summary'])
                            results['llm_summary'] = summary_result
                        else:
                            st.warning(f"⚠️ Summary generation failed: {summary_result.get('error', 'Unknown error')[:200]}")
                            results['llm_summary'] = None
                    except Exception as e:
                        st.error(f"❌ Error generating summary: {str(e)[:200]}")
                        results['llm_summary'] = None
            else:
                st.info("ℹ️ AI summary disabled. Enable checkbox above to generate summary.")
                results['llm_summary'] = None
            
                # Store results for export
                st.session_state['analysis_results'] = results
                
                # Export Results
                st.header("💾 Export Results")
                
                export_format = export_options["format"]
                base_filename = f"market_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                col1, col2, col3, col4 = st.columns(4)
                
                try:
                    if export_format == "JSON":
                        filename = f"{base_filename}.json"
                        json_str = export_to_json(results, include_llm=bool(results.get('llm_summary')))
                        with col1:
                            st.download_button(
                                label="📥 Download JSON",
                                data=json_str,
                                file_name=filename,
                                mime="application/json",
                                use_container_width=True
                            )
                    
                    elif export_format == "CSV":
                        filename = f"{base_filename}.csv"
                        csv_str = export_to_csv(results)
                        with col2:
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv_str,
                                file_name=filename,
                                mime="text/csv",
                                use_container_width=True
                            )
                    
                    elif export_format == "Excel":
                        filename = f"{base_filename}.xlsx"
                        excel_data = export_to_excel(results, include_charts=export_options["include_charts"])
                        with col3:
                            st.download_button(
                                label="📥 Download Excel",
                                data=excel_data,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    
                    elif export_format == "PDF":
                        filename = f"{base_filename}.pdf"
                        pdf_data = export_to_pdf(results, include_charts=export_options["include_charts"])
                        with col4:
                            st.download_button(
                                label="📥 Download PDF",
                                data=pdf_data,
                                file_name=filename,
                                mime="application/pdf",
                                use_container_width=True
                            )
                    
                    # Also save JSON to reports directory
                    reports_dir = project_root / "reports"
                    reports_dir.mkdir(exist_ok=True)
                    report_path = reports_dir / f"{base_filename}.json"
                    
                    try:
                        json_str = export_to_json(results, include_llm=bool(results.get('llm_summary')))
                        with open(report_path, 'w', encoding='utf-8') as f:
                            f.write(json_str)
                        st.caption(f"✅ Results saved to: {report_path}")
                    except Exception as e:
                        st.caption(f"⚠️ Note: Could not save to reports directory: {str(e)[:100]}")
                        
                except ImportError as e:
                    st.error(f"❌ Export format requires additional packages: {str(e)}")
                    st.info("💡 Install missing packages: `pip install openpyxl reportlab`")
                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")
                
                # Cleanup temp file
                # #region agent log
                debug_log("ui/app.py:338", "Before temp file cleanup", {"temp_path": str(temp_path), "exists": temp_path.exists() if temp_path else False}, "B")
                # #endregion
                try:
                    if temp_path and temp_path.exists():
                        temp_path.unlink()
                        # #region agent log
                        debug_log("ui/app.py:341", "Temp file deleted", {"temp_path": str(temp_path)}, "B")
                        # #endregion
                except Exception as cleanup_error:
                    # #region agent log
                    debug_log("ui/app.py:343", "Temp file cleanup failed", {"temp_path": str(temp_path), "error": str(cleanup_error)}, "B")
                    # #endregion
                    pass
    
    except Exception as e:
        # #region agent log
        debug_log("ui/app.py:343", "Exception caught in main try block", {"error_type": type(e).__name__, "error_message": str(e), "temp_path": str(temp_path) if 'temp_path' in locals() else "N/A", "temp_exists": temp_path.exists() if 'temp_path' in locals() and temp_path else False}, "E")
        # #endregion
        st.error(f"❌ Error: {str(e)}")
        # #region agent log
        # Cleanup temp file on exception
        if 'temp_path' in locals() and temp_path and temp_path.exists():
            try:
                temp_path.unlink()
                debug_log("ui/app.py:349", "Temp file deleted after exception", {"temp_path": str(temp_path)}, "B")
            except:
                pass
        # #endregion