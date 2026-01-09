"""
Minimal Streamlit UI for Market Analytics System

Academic project UI for data upload, analysis, and visualization.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.ingestion import read_csv_file
from core.validator import validate_and_clean
from core.orchestrator import run_all_agents
from llm.summarizer import summarize_agent_results

# Page configuration
st.set_page_config(
    page_title="Market Analytics System",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Market Analytics System")
st.markdown("**Academic Project** - Upload CSV data for market analysis")

# CSV Upload
st.header("📁 Data Upload")
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

if uploaded_file is not None:
    try:
        # Save uploaded file temporarily
        temp_path = Path("temp_upload.csv")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Ingest and validate
        df = read_csv_file(str(temp_path))
        st.success(f"✅ File loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Preview
        with st.expander("Preview Data"):
            st.dataframe(df.head(10))
        
        # Validate and clean
        cleaned_df = validate_and_clean(df, cleaning_strategy="drop_rows", remove_dupes=True)
        st.info(f"✅ Validated: {len(cleaned_df)} rows after cleaning")
        
        # LLM Summary option
        enable_llm = st.checkbox("Enable AI Summary", value=False)
        
        # Run analysis
        if st.button("🚀 Run Analysis", type="primary"):
            with st.spinner("Running analytical agents..."):
                results = run_all_agents(cleaned_df)
            
            st.success("✅ Analysis complete!")
            
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
            
            brand_result = results["agents"]["brand"]
            brand_data = brand_result["results"]["top_brands"]
            
            # Table
            brands_df = pd.DataFrame(brand_data)
            st.dataframe(brands_df[["brand", "count", "confidence"]])
            
            # Bar chart
            fig = px.bar(brands_df, x="brand", y="count", title="Brand Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            # Pricing Metrics
            st.header("💰 Pricing Analysis")
            pricing_result = results["agents"]["pricing"]
            stats = pricing_result["results"]["price_statistics"]
            optimal = pricing_result["results"]["optimal_price_range"]
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Min Price", f"${stats['min_price']:.2f}")
            col2.metric("Max Price", f"${stats['max_price']:.2f}")
            col3.metric("Mean Price", f"${stats['mean_price']:.2f}")
            col4.metric("Median Price", f"${stats['median_price']:.2f}")
            
            st.metric("Optimal Range", f"${optimal['optimal_range_min']:.2f} - ${optimal['optimal_range_max']:.2f}")
            
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
            st.dataframe(features_df[["feature", "count", "confidence"]])
            
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
            
            gap_result = results["agents"]["gap"]
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
            
            # Prepare export data
            export_data = {
                "timestamp": results["timestamp"],
                "total_records": results["total_records"],
                "agent_outputs": [
                    results["agents"]["brand"],
                    results["agents"]["pricing"],
                    results["agents"]["feature"],
                    results["agents"]["gap"]
                ]
            }
            
            # Add LLM summary if available
            if results.get('llm_summary'):
                export_data["llm_summary"] = results['llm_summary']
            else:
                export_data["llm_summary"] = None
            
            # Create JSON string
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            # Generate filename
            filename = f"market_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Download button
            st.download_button(
                label="📥 Download Results (JSON)",
                data=json_str,
                file_name=filename,
                mime="application/json"
            )
            
            # Also save to reports directory
            reports_dir = project_root / "reports"
            reports_dir.mkdir(exist_ok=True)
            report_path = reports_dir / filename
            
            try:
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                st.caption(f"Results also saved to: {report_path}")
            except Exception as e:
                st.caption(f"Note: Could not save to reports directory: {str(e)[:100]}")
            
            # Cleanup temp file
            try:
                temp_path.unlink()
            except:
                pass
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
