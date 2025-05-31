import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Config pagina
st.set_page_config(page_title="Monte Carlo Trading DCA", layout="wide")

# Titolo
st.title("📊 Monte Carlo Trading Simulator con DCA e Risk Management Personalizzato")

# Parametri utente
st.sidebar.header("Parametri di Simulazione")

capital = st.sidebar.number_input("Capitale Iniziale (€)", value=100000)
risk_per_trade_pct = st.sidebar.slider("Rischio per Trade (%)", 0.1, 5.0, 1.0)
num_trades = st.sidebar.number_input("Numero di Trade da Simulare", value=1000)

winrate = st.sidebar.slider("Winrate Trade (%)", 10, 90, 40)

# Allocazione per ogni entry
entry_allocation = [0.10, 0.35, 0.55]
entry_levels = [0.0, 0.33, 0.66]  # 0%, 33%, 66% tra entry e stop

# TP/SL ratio
rr = st.sidebar.slider("Rapporto Rischio/Rendimento (R:R)", 0.5, 5.0, 2.0)

# Seed randomico per ripetibilità
seed = st.sidebar.number_input("Seed Random (0 = casuale)", value=0)

# Simulazione Monte Carlo
if st.button("Lancia Simulazione"):

    np.random.seed(seed if seed != 0 else None)

    equity = capital
    equity_curve = [capital]
    profits = []

    for _ in range(num_trades):
        trade_outcome = np.random.rand() < (winrate / 100)

        total_risk_eur = capital * (risk_per_trade_pct / 100)

        # Calcolo di quanto rischio su ogni entry
        entry_risks = [total_risk_eur * alloc for alloc in entry_allocation]

        if trade_outcome:
            # Vincita → calcolo profitto su ogni entry
            trade_profit = sum([risk * rr for risk in entry_risks])
            equity += trade_profit
            profits.append(trade_profit)
        else:
            # Perdita → tutto lo stop
            loss = total_risk_eur
            equity -= loss
            profits.append(-loss)

        equity_curve.append(equity)

    # Statistiche finali
    total_return_pct = (equity - capital) / capital * 100
    max_drawdown = np.min(equity_curve) - capital

    profit_factor = round(
        sum([p for p in profits if p > 0]) / abs(sum([p for p in profits if p < 0])), 2
    )

    simulated_winrate = round(len([p for p in profits if p > 0]) / num_trades * 100, 2)

    st.subheader("📊 Risultati Simulazione")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ritorno Totale (%)", f"{total_return_pct:.2f}%")
    col2.metric("Profit Factor", f"{profit_factor}")
    col3.metric("Max Drawdown (€)", f"{max_drawdown:.2f}")
    col4.metric("Winrate Simulato (%)", f"{simulated_winrate}")

    # Equity curve
    st.subheader("📈 Equity Curve")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(equity_curve, color="dodgerblue")
    ax.set_xlabel("Trade")
    ax.set_ylabel("Equity (€)")
    ax.grid(True)
    st.pyplot(fig)

    # Distribuzione Profitti
    st.subheader("📊 Distribuzione dei Profitti per Trade")
    fig2, ax2 = plt.subplots()
    sns.histplot(profits, bins=30, kde=True, ax=ax2, color="mediumseagreen")
    ax2.set_xlabel("Profitto per Trade (€)")
    st.pyplot(fig2)

