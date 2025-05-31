import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Titolo st.markdown("# 📊 Monte Carlo Trading Simulator Avanzato")

# Sidebar parametri
st.sidebar.header("Parametri di Simulazione")
capitale_iniziale = st.sidebar.number_input("Capitale Iniziale (€)", value=100000)
rischio_per_trade = st.sidebar.slider("Rischio per Trade (%)", 0.1, 5.0, 1.0)
numero_trade = st.sidebar.number_input("Numero di Trade da Simulare", value=1000)
winrate = st.sidebar.slider("Winrate Trade (%)", 10, 90, 40)
rapporto_rischio_rendimento = st.sidebar.slider("Rapporto Rischio/Rendimento (R:R)", 0.5, 5.0, 2.0)
seed = st.sidebar.number_input("Seed Random (0 = casuale)", value=0)

# Parametri avanzati
st.sidebar.header("Impostazioni Avanzate")
multiple_entry = st.sidebar.slider("Numero massimo di Multiple Entry per trade", 1, 5, 1)
dca_attivo = st.sidebar.checkbox("Attiva DCA", value=False)
dca_percentuale = st.sidebar.slider("Percentuale Capitale Aggiuntivo su Perdita (%)", 10, 100, 50) if dca_attivo else 0
trailing_stop_attivo = st.sidebar.checkbox("Attiva Trailing Stop", value=False)
trailing_stop_percentuale = st.sidebar.slider("Trailing Stop (%)", 0.5, 5.0, 2.0) if trailing_stop_attivo else 0
stop_max_drawdown = st.sidebar.slider("Max Drawdown (%)", 10, 100, 50)
reinvesti_profitti = st.sidebar.checkbox("Reinvesti Profitti", value=True)

if st.button("Lancia Simulazione"):
    if seed != 0:
        np.random.seed(seed)

    capitale = capitale_iniziale
    equity_curve = [capitale]
    max_equity = capitale
    drawdown = 0
    trades = []

    for i in range(int(numero_trade)):
        trade_capitale = capitale * (rischio_per_trade / 100)
        trade_outcome = np.random.rand() * 100 < winrate

        profitto_per_trade = trade_capitale * rapporto_rischio_rendimento if trade_outcome else -trade_capitale

        # Multiple Entry
        for e in range(1, multiple_entry):
            if not trade_outcome and dca_attivo:
                extra_capitale = capitale * (dca_percentuale / 100)
                extra_outcome = np.random.rand() * 100 < winrate
                profitto_extra = extra_capitale * rapporto_rischio_rendimento if extra_outcome else -extra_capitale
                profitto_per_trade += profitto_extra

        capitale += profitto_per_trade if reinvesti_profitti else 0
        equity_curve.append(capitale)

        max_equity = max(max_equity, capitale)
        drawdown = max(drawdown, (max_equity - capitale) / max_equity * 100)

        trades.append(profitto_per_trade)

        if drawdown >= stop_max_drawdown:
            st.warning(f"Simulazione interrotta al trade {i+1} per superamento drawdown massimo ({drawdown:.2f}%)")
            break

    st.success(f"Simulazione completata. Capitale finale: €{capitale:,.2f}")

    # Plot equity curve
    fig, ax = plt.subplots()
    ax.plot(equity_curve, color='cyan')
    ax.set_title("Equity Curve")
    ax.set_xlabel("Numero Trade")
    ax.set_ylabel("Capitale (€)")
    st.pyplot(fig)

    # Statistiche finali
    totale_trade = len(trades)
    trade_vincenti = len([t for t in trades if t > 0])
    trade_persi = totale_trade - trade_vincenti
    st.write(f"**Totale Trade:** {totale_trade}")
    st.write(f"**Trade Vincenti:** {trade_vincenti} ({trade_vincenti / totale_trade * 100:.2f}%)")
    st.write(f"**Trade Persi:** {trade_persi} ({trade_persi / totale_trade * 100:.2f}%)")
    st.write(f"**Max Drawdown:** {drawdown:.2f}%")

    # Log Trade
    with st.expander("📜 Log Dettagliato dei Trade"):
        for n, t in enumerate(trades, 1):
            st.write(f"Trade {n}: {'+' if t>=0 else ''}{t:,.2f} €")


