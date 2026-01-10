import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from main.logic import price_option, entry_price, pnl, input_table_entry
from db.migrate import run_migration
from db.repositories.input_repo import InputRepository
from db.repositories.output_repo import OutputRepository


st.set_page_config(
    page_title="Black-Scholes PnL Calculator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.call-card {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.put-card {
    background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
    margin: 10px 0;
}

.metric-label {
    font-size: 1rem;
    opacity: 0.9;
    margin-bottom: 5px;
}

.stButton>button {
    width: 100%;
    background-color: #667eea;
    color: white;
    border-radius: 5px;
    padding: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# Initialize database
@st.cache_resource
def init_database():
    try:
        run_migration()
        return True
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return False

init_database()

# Helper Functions
def generate_pnl_heatmap(entry_inputs: Dict, spot_range: np.ndarray, 
                         vol_range: np.ndarray, option_type: str = 'call'):
    """Generate PnL heatmap for call or put options"""
    pnl_matrix = np.zeros((len(vol_range), len(spot_range)))
    
    for i, vol in enumerate(vol_range):
        for j, spot in enumerate(spot_range):
            current_inputs = entry_inputs.copy()
            current_inputs['StockPrice'] = spot
            current_inputs['Volatility'] = vol
            
            pnl_result = pnl(current_inputs, entry_inputs)
            pnl_matrix[i, j] = pnl_result[f'{option_type}_pnl']
    
    return pnl_matrix

def plot_pnl_heatmap(pnl_matrix: np.ndarray, spot_range: np.ndarray, 
                      vol_range: np.ndarray, title: str):
    """Create matplotlib heatmap"""
    fig, ax = plt.subplots(figsize=(10, 8))
    

    from matplotlib.colors import LinearSegmentedColormap
    colors = ['#eb3349', '#f45c43', '#ff9a76', '#ffe5d9', '#d4edda', '#38ef7d', '#11998e']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('trading', colors, N=n_bins)

    sns.heatmap(
        pnl_matrix,
        xticklabels=np.round(spot_range, 2),
        yticklabels=np.round(vol_range, 3),
        annot=True,
        fmt=".2f",
        cmap=cmap,
        center=0,
        ax=ax,
        cbar_kws={'label': 'PnL ($)'},
        linewidth=0.5,
        linecolor="white"
    )
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Spot Price ($)', fontsize=12)
    ax.set_ylabel('Volatility (σ)', fontsize=12)
    
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    return fig

def save_calculation_to_db(entry_inputs: Dict, spot_range: np.ndarray, 
                           vol_range: np.ndarray):
    """Save calculation inputs and outputs to database"""
    try:
        input_repo = InputRepository()
        output_repo = OutputRepository()
        
        calculation_id = input_repo.create_input(entry_inputs)
        
        outputs = []
        for vol_shock in vol_range:
            for stock_shock in spot_range:
                current_inputs = entry_inputs.copy()
                current_inputs['StockPrice'] = stock_shock
                current_inputs['Volatility'] = vol_shock
                
                prices = price_option(current_inputs)
                
                outputs.append({
                    'CalculationId': calculation_id,
                    'VolatilityShock': vol_shock,
                    'StockPriceShock': stock_shock,
                    'OptionPrice': prices['call_price'],
                    'IsCall': 1
                })
                
                outputs.append({
                    'CalculationId': calculation_id,
                    'VolatilityShock': vol_shock,
                    'StockPriceShock': stock_shock,
                    'OptionPrice': prices['put_price'],
                    'IsCall': 0
                })
        
        output_repo.create_outputs_batch(calculation_id, outputs)
        return calculation_id
    except Exception as e:
        st.error(f"Failed to save to database: {e}")
        return None


with st.sidebar:
    st.title("📈 Black-Scholes PnL")
    st.write("Options Pricing & Analysis")
    
    st.markdown("---")
    st.subheader("Entry Position Parameters")
    
    entry_stock = st.number_input(
        "Entry Stock Price ($)",
        min_value=0.01,
        value=100.0,
        step=0.01,
        help="Current price of the underlying asset"
    )
    
    strike = st.number_input(
        "Strike Price ($)",
        min_value=0.01,
        value=100.0,
        step=0.01,
        help="Exercise price of the option"
    )
    
    time_to_expiry = st.number_input(
        "Time to Expiry (Years)",
        min_value=0.01,
        value=1.0,
        step=0.01,
        help="Time remaining until option expiration"
    )
    
    risk_free_rate = st.number_input(
        "Risk-Free Rate",
        min_value=0.0,
        max_value=1.0,
        value=0.05,
        step=0.01,
        format="%.4f",
        help="Annual risk-free interest rate"
    )
    
    volatility = st.number_input(
        "Entry Volatility (σ)",
        min_value=0.01,
        max_value=2.0,
        value=0.25,
        step=0.01,
        format="%.4f",
        help="Historical or implied volatility"
    )
    
    st.markdown("---")
    st.subheader("Scenario Analysis Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        spot_min = st.number_input(
            'Min Spot ($)',
            min_value=0.01,
            value=entry_stock * 0.7,
            step=0.01
        )
    with col2:
        spot_max = st.number_input(
            'Max Spot ($)',
            min_value=0.01,
            value=entry_stock * 1.3,
            step=0.01
        )
    
    col3, col4 = st.columns(2)
    with col3:
        vol_min = st.number_input(
            'Min Vol (σ)',
            min_value=0.01,
            max_value=2.0,
            value=volatility * 0.5,
            step=0.01,
            format="%.4f"
        )
    with col4:
        vol_max = st.number_input(
            'Max Vol (σ)',
            min_value=0.01,
            max_value=2.0,
            value=volatility * 1.5,
            step=0.01,
            format="%.4f"
        )
    
    heatmap_resolution = st.slider(
        'Heatmap Resolution',
        min_value=5,
        max_value=20,
        value=10,
        help="Number of points in each dimension"
    )
    
    st.markdown("---")
    save_to_db = st.checkbox("Save to Database", value=False)
    
    st.markdown("---")
    st.write("`Created by:`")
    st.markdown("**[sallahvoice]**")
    linkedin_url = "https://www.linkedin.com/in/salah-eddine-bekkari-51b588367/"
    github_url = "https://github.com/sallahvoice"
    st.markdown(
        f'<a href="{linkedin_url}" target="_blank">LinkedIn</a> | '
        f'<a href="{github_url}" target="_blank">GitHub</a>',
        unsafe_allow_html=True
    )


st.title("Black-Scholes Option Pricing & PnL Analysis")
st.markdown("""
Analyze option positions with real-time pricing, Greeks calculations, and comprehensive PnL scenarios 
across different market conditions.
""")

entry_inputs = {
    "StockPrice": entry_stock,
    "StrikePrice": strike,
    "TimeToExpiry": time_to_expiry,
    "RiskFreeRate": risk_free_rate,
    "Volatility": volatility,
}

# Calculate entry prices and Greeks
try:
    entry_prices = price_option(entry_inputs)
    
    # Display Entry Position Metrics
    st.markdown("### 📊 Entry Position Valuation")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="call-card">
            <div class="metric-label">CALL Price</div>
            <div class="metric-value">${entry_prices['call_price']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="put-card">
            <div class="metric-label">PUT Price</div>
            <div class="metric-value">${entry_prices['put_price']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Call Delta</div>
            <div class="metric-value">{entry_prices['call_delta']:.4f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Put Delta</div>
            <div class="metric-value">{entry_prices['put_delta']:.4f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Greeks table
    st.markdown("### 📐 Greeks")
    greeks_data = {
        "Metric": ["Call Delta", "Put Delta", "Gamma (Both)"],
        "Value": [
            f"{entry_prices['call_delta']:.6f}",
            f"{entry_prices['put_delta']:.6f}",
            f"{entry_prices['call_gamma']:.6f}"
        ]
    }
    st.table(pd.DataFrame(greeks_data))
    
    st.markdown("---")
    
    # PnL Heatmap Analysis
    st.markdown("### 🔥 PnL Scenario Analysis")
    st.info(
        "Explore how your position's Profit & Loss changes across different spot prices "
        "and volatility levels. Green indicates profit, red indicates loss."
    )
    
    # Generate ranges for heatmap
    spot_range = np.linspace(spot_min, spot_max, heatmap_resolution)
    vol_range = np.linspace(vol_min, vol_max, heatmap_resolution)
    
    # Generate heatmaps
    with st.spinner("Generating PnL heatmaps..."):
        call_pnl_matrix = generate_pnl_heatmap(entry_inputs, spot_range, vol_range, 'call')
        put_pnl_matrix = generate_pnl_heatmap(entry_inputs, spot_range, vol_range, 'put')
    
    # Display heatmaps side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CALL Option PnL")
        fig_call = plot_pnl_heatmap(
            call_pnl_matrix,
            spot_range,
            vol_range,
            "CALL PnL Heatmap"
        )
        st.pyplot(fig_call)
        
        st.markdown("**Statistics:**")
        st.write(f"Max PnL: ${call_pnl_matrix.max():.2f}")
        st.write(f"Min PnL: ${call_pnl_matrix.min():.2f}")
        st.write(f"Avg PnL: ${call_pnl_matrix.mean():.2f}")
    
    with col2:
        st.subheader("PUT Option PnL")
        fig_put = plot_pnl_heatmap(
            put_pnl_matrix,
            spot_range,
            vol_range,
            "PUT PnL Heatmap"
        )
        st.pyplot(fig_put)
        
        st.markdown("**Statistics:**")
        st.write(f"Max PnL: ${put_pnl_matrix.max():.2f}")
        st.write(f"Min PnL: ${put_pnl_matrix.min():.2f}")
        st.write(f"Avg PnL: ${put_pnl_matrix.mean():.2f}")
    
    if save_to_db:
        if st.button("💾 Save Calculation to Database"):
            with st.spinner("Saving to database..."):
                calc_id = save_calculation_to_db(entry_inputs, spot_range, vol_range)
                if calc_id:
                    st.success(f"✅ Calculation saved! ID: {calc_id}")
    
    st.markdown("---")
    if st.checkbox("📜 Show Recent Calculations"):
        try:
            repo = InputRepository()
            recent = repo.list_recent_inputs(limit=5)
            if recent:
                df_recent = pd.DataFrame(recent)
                st.dataframe(df_recent, use_container_width=True)
            else:
                st.info("No recent calculations found.")
        except Exception as e:
            st.error(f"Failed to load recent calculations: {e}")

except Exception as e:
    st.error(f"Calculation error: {e}")
    st.info("Please check your input parameters and try again.")