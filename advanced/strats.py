import time
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt

from statistical_modeling.Risk_Modeling import build_risk_features, update_last_row
from statistical_modeling.risk_dashboard import plot_risk_dashboard

from pde_backtest import main as pde_main, PDEBacktest, estimate_params
from cfd_pde import solve_pde
from PDE_parameters import Params
from plotting import CMAP_PROB,TMID, plot_backtest, plot_drawdown
from models import OLSModel, MLEModel, NULLModel

from position_manager import position_manager
from data_fetcher import data_fetcher
from csv_manager import csv_manager
from config_loader import config
from logger import logger

def _out_dir(tf: str) -> Path:
    base = config.get('output', 'charts_base_directory')
    d    = Path(base) / tf
    d.mkdir(parents=True, exist_ok=True)
    return d

def _build_p_base(tp: float, sl: float) -> Params:
    p    = Params()
    p.TP =  tp
    p.SL = -sl
    return p

def _get_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Simple ATR from OHLCV DataFrame."""
    high  = df['high']
    low   = df['low']
    close = df['close'].shift(1)
    tr    = pd.concat([high - low,
                        (high - close).abs(),
                        (low  - close).abs()], axis=1).max(axis=1)
    return tr.rolling(window).mean()

def _regime_changed(last_sbar: float | None,
                     sbar_now: float,
                     threshold: float) -> bool:
    return (last_sbar is None or
            abs(sbar_now - last_sbar) >= threshold)

def _recompute_surface(df: pd.DataFrame, t: int,
                        p_base: Params, mu: float) -> tuple:
    """
    Estimate params from df[:t+1], build a new Params, solve PDE.
    Returns (surface_dict, p_new).
    """
    est             = estimate_params(df.iloc[:t+1])
    p_new           = Params()
    p_new.sigma0    = est['sigma0']
    p_new.sigma_bar = est['sigma_bar']
    p_new.eta       = est['eta']
    p_new.beta      = est['beta']
    p_new.rho       = est['rho']
    p_new.TP        = p_base.TP
    p_new.SL        = p_base.SL
    p_new.r_kill    = p_base.r_kill
    p_new.Nx        = p_base.Nx
    p_new.Ns        = p_base.Ns
    p_new.sigma_max = max(est['sigma_bar'] * 4, est['sigma0'] * 4, 8.0)

    u, x_grid, s_grid = solve_pde(p_new, mu=mu)

    surface = dict(
        u         = u,
        x_grid    = x_grid,
        s_grid    = s_grid,
        p         = p_new,
        mu        = mu,
        sigma_bar = est['sigma_bar'],
        sigma0    = est['sigma0'],
    )
    return surface, p_new


def _regenerate_charts(tf: str, df_session: pd.DataFrame,
                        surface: dict|None,
                        surface_id: int):

    out = _out_dir(tf)
    tag = f"{tf}_surface{surface_id}"
    
    if surface is not None:
        # plot the surface and save it
        xg     = surface["x_grid"]
        sg     = surface["s_grid"]
        u      = surface["u"]
        # XX, SS = np.meshgrid(xg, sg, indexing='ij')
        fig, ax = plt.subplots(figsize=(10, 6))
        im = ax.imshow(u.T, origin="lower", aspect="auto",
                       extent=[xg[0], xg[-1], sg[0], sg[-1]],
                       cmap=CMAP_PROB, vmin=0, vmax=1)
        cb = fig.colorbar(im, ax=ax, fraction=0.04)
        cb.ax.tick_params(colors=TMID, labelsize=5)
        cb.set_label("P(TP)", color=TMID, fontsize=6)
        plt.savefig(out / f'surface_{tag}.png', dpi=150)
        plt.close(fig)

    logger.log_system_event('charts_regenerated',
        f'[{tf}] surface={surface_id}')

def run_backtest(USE_MODEL = False):    
    if not data_fetcher.connect():
        raise Exception('Failed to connect to MT5')

    timeframes = config.get('trading', 'active_timeframe')
    if not isinstance(timeframes, list):
        timeframes = [timeframes]

    tp = config.get('trading', 'tp') if 'tp' in (config._config.get('trading', {})) else 5.5
    sl = config.get('trading', 'sl') if 'sl' in (config._config.get('trading', {})) else 4.0
    thresh = config.get('trading', 'thresholds') if 'thresholds' in (config._config.get('trading', {})) else {timeframes[0]:1.0}

    tf_data = {}

    for tf in timeframes:
        print(f'\n{"="*55}')
        print(f'  TIMEFRAME: {tf}')
        print(f'{"="*55}')

        # ── Fetch ─────────────────────────────────────────────────────
        print(f'  Fetching data ...')
        df = data_fetcher.fetch_data(tf)
        if df is None:
            logger.log_error(f'No data for {tf}')
            continue
        df.rename(columns={'timestamp': 'time'}, errors='ignore', inplace=True)
        print(f'  Fetched {len(df)} rows')

        # ── Features ─────────────────────────────────────────────────
        print(f'  Building features ...')
        if USE_MODEL:
            df = build_risk_features(df, tf)
        tf_data[tf] = df

        out = _out_dir(tf)
        
        # ── PDE backtest ──────────────────────────────────────────────
        print(f'  Running PDE backtest ...')
        bt, path_df = pde_main(args={
            'data'      : df.copy(),
            'tp'       : tp,
            'sl'       : sl,
            'threshold': thresh.get(tf, 1.0),
            'out'      : str(out / 'pde_backtest'), 
            'lots'     : config.get('trading').get('lots', 1),
            'symbol'   : config.get('trading').get('symbol', None),
            'strategy' : config.get('trading').get('strategy', 'always_buy'),
            'mu_model' : OLSModel()        
            })

        # ── Risk dashboard ────────────────────────────────────────────\
        if USE_MODEL:
            plot_risk_dashboard(df, tag=tf,
                                save_path=str(out / 'risk_dashboard.png'))

    data_fetcher.disconnect()
    return tf_data, bt, path_df

"""
def run_live(USE_MODEL=False):
    if not data_fetcher.connect():
        raise Exception('Failed to connect to MT5')

    timeframes = config.get('trading', 'active_timeframe')
    if isinstance(timeframes, list):
        timeframes = timeframes[0]
    assert isinstance(timeframes, str), 'active_timeframe should be a list of strings'

    max_iter      = config.get('trading', 'max_iterations')
    sleep_sec     = config.get('trading', 'update_interval_seconds')
    chart_every_n = config.get('output', 'save_charts_every_n_iterations')
    tp            = config.get('trading').get('tp', 5.5)
    sl            = config.get('trading').get('sl', 4)
    threshold     = config.get('trading', 'thresholds').get(timeframes, 1.0)
    lot_size      = config.get('trading').get('lots', 0.01)

    # ── Per-timeframe live state ──────────────────────────────────────
    live_state = {}
    tf = timeframes
    if USE_MODEL:
        out = _out_dir(tf)
        model_dir = str(out / 'pde_model')
        try:
            model, scaler, feature_cols = load_model(model_dir)
        except Exception:
            logger.log_system_event('live_init',
                f'[{tf}] No model found — training on startup data ...')
            
            df_init = data_fetcher.fetch_data(tf)

            if df_init is None:
                raise Exception(f'No data for {tf} on startup')
            
            df_init.rename(columns={'timestamp': 'time'}, errors='ignore', inplace=True)
            
            df_init = build_risk_features(df_init, tf)
            ols_main(args={
                'csv': df_init.copy(), 'tp': tp, 'sl': sl,
                'window': 10, 'gap': 10, 'out': model_dir,
            })
            model, scaler, feature_cols = load_model(model_dir)

    live_state[tf] = {
        'model'          : model if USE_MODEL else None,
        'scaler'         : scaler if USE_MODEL else None,
        'feature_cols'   : feature_cols if USE_MODEL else None,
        'p_base'         : _build_p_base(tp, sl),
        'current_surface': None,
        'last_sigma_bar' : None,
        'surface_id'     : -1,
        'bt_obj'         : None,   # lightweight PDEBacktest for chart history
        'df_session'     : pd.DataFrame(),   # grows each iteration
        'df_features'    : None
    }

    iteration = 0

    # ── Main loop ─────────────────────────────────────────────────────
    try:
        while iteration < max_iter:
            state = live_state.get(tf)
            if state is None:
                raise Exception(f'No live state for timeframe {tf}')

            # ── Fetch latest bars ─────────────────────────────────
            df, updated = data_fetcher.update_df(tf)
            if df is None or not updated:
                logger.log_system_event('no_new_data', f'[{tf}] No new data, skipping iteration')
                time.sleep(sleep_sec)
                continue
            iteration += 1
            logger.log_system_event('loop_start', f'Iteration {iteration}')
            df.rename(columns={'timestamp': 'time'}, errors='ignore', inplace=True)
            # Log latest bar to CSV
            latest = df.iloc[-1]
            csv_manager.append_bar_data(tf, latest.to_dict())

            if USE_MODEL:
                state['df_features'] = build_risk_features(df.copy(), tf)  # compute full features on first iteration to avoid issues with rolling windows and NaNs
                df = state['df_features'].copy()

            # Grow session df (used for chart regeneration)
            state['df_session'] = df.copy()

            # Current bar index and vol
            t          = len(df) - 1
            vol_series = df['close'].diff().rolling(20).std()
            sbar_series= df['close'].diff().rolling(200).std()
            sigma_now  = float(vol_series.iloc[-1]) if not vol_series.empty else 0.0
            sbar_now   = float(sbar_series.iloc[-1]) if not sbar_series.empty else 0.0

            if np.isnan(sigma_now) or np.isnan(sbar_now):
                logger.log_system_event('nan_vol', f'[{tf}] NaN vol values — skipping iteration')
                time.sleep(sleep_sec)
                continue

            # Predict mu from model
            if USE_MODEL:
                try:
                    feat    = df[state['feature_cols']].shift(1).iloc[[-1]].fillna(0)
                    mu_now  = float(state['model'].predict(
                        state['scaler'].transform(feat.values))[0])
                except Exception as e:
                    logger.log_error(f'mu prediction [{tf}]: {e}')
                    mu_now = 0.0
            else:
                y = df['close'].iloc[-10-2:-1].values
                slope = latest_slope(y, window=10)
                mu_now = slope
            # ── Vol regime check → recompute PDE ─────────────────
            if _regime_changed(state['last_sigma_bar'],sbar_now, threshold):

                # Clamp mu to keep Pe <= 2.0 so surface doesn't degenerate
                p_base     = state['p_base']
                L          = abs(p_base.TP) + abs(p_base.SL)
                sigma_est  = sbar_now if sbar_now > 0 else 1.0
                mu_max     = 2.0 * 0.5 * sigma_est**2 / L
                mu_clamped = float(np.clip(mu_now, -mu_max, mu_max))

                logger.log_system_event('regime_change',
                    f'[{tf}] sbar {state["last_sigma_bar"]} → {sbar_now:.3f}  '
                    f'mu_raw={mu_now:.4f}  mu_clamped={mu_clamped:.4f}  '
                    f'Pe_raw={abs(mu_now)*L/(0.5*sigma_est**2+1e-9):.2f}')

                surface, p_new = _recompute_surface(df, t, state['p_base'], mu_clamped)

                state['current_surface'] = surface
                state['last_sigma_bar']  = sbar_now
                state['surface_id']     += 1

                # Log stats snapshot at regime change
                position_manager.log_stats_on_regime_change(
                    timeframe  = tf,
                    surface_id = state['surface_id'],
                    sigma_bar  = sbar_now,
                    sigma0     = sigma_now,
                    mu         = mu_now,
                )

                # Regenerate all charts from session-start data
                _regenerate_charts(
                    tf         = tf,
                    df_session = state['df_session'],
                    surface     = state['current_surface'],
                    surface_id = state['surface_id'],
                )
            
            if state['current_surface'] is None:
                logger.log_system_event('no_surface', f'[{tf}] No PDE surface yet, skipping trade evaluation')
                time.sleep(sleep_sec)
                continue

            # ── Update existing position ──────────────────────────
            active = position_manager.get_active_position()

            if active is not None:
                pos_id = active['id']
                atr_ser = _get_atr(df)

                # No adaptive SL/TP so commented it out
                # position_manager.update_position(
                #     position_id = pos_id,
                #     current_bar = latest.to_dict(),
                #     atr_series  = atr_ser,
                #     timeframe   = tf,
                # )

                # Update sigma on position for adaptive SL awareness
                active['current_sigma'] = sigma_now

                # Check exit
                reason, exit_px = position_manager.check_exit_conditions(
                    pos_id, latest.to_dict())

                if reason is not None:
                    closed = position_manager.close_position(
                        position_id = pos_id,
                        exit_price  = exit_px,
                        exit_reason = reason,
                        exit_time   = datetime.now(),
                        timeframe   = tf,
                    )
                    if closed:
                        logger.log_system_event('trade_closed',
                            f'[{tf}] {reason}  pnl={closed["pnl_points"]:+.2f}')

            # ── Try to enter if no position ───────────────────────
            elif not position_manager.has_position():
                surf    = state['current_surface']
                p_base  = state['p_base']
                decision = position_manager.evaluate_entry(
                    bar_idx   = t,
                    df        = df,
                    surface   = surf,
                    sigma_now = sigma_now,
                    mu_now    = mu_now,
                    p_base    = p_base,
                )
                print(decision)
                if decision['enter']:
                    tick    = None
                    try:
                        import MetaTrader5 as mt5
                        tick = mt5.symbol_info_tick(
                            config.get('trading', 'symbol'))
                    except Exception:
                        pass

                    entry_px = (tick.ask
                                if tick and decision['direction'] == 'long'
                                else tick.bid
                                if tick
                                else float(df['close'].iloc[-1]))

                    decision['entry_price'] = entry_px
                    decision['tp_distance'] = abs(p_base.TP)
                    decision['sl_distance'] = abs(p_base.SL)
                    decision['position_size'] = lot_size
                    decision['surface_id']  = state['surface_id']
                    decision['mu_now']      = mu_now

                    pos = position_manager.create_position(
                        decision, datetime.now())

                    if pos is not None:
                        placed = position_manager.place_mt5_order(pos['id'])
                        if placed:
                            position_manager.active_positions[
                                pos['id']]['entry_p_tp'] = decision['p_tp_entry']
                            logger.log_system_event('trade_opened',
                                f'[{tf}] {decision["direction"].upper()}  '
                                f'@ {entry_px:.2f}  '
                                f'reason={decision["reason"]}')
                        else:
                            # MT5 order failed — remove internal position
                            del position_manager.active_positions[pos['id']]

            # ── Periodic chart save ───────────────────────────────
            if iteration % chart_every_n == 0:
                _regenerate_charts(
                    tf         = tf,
                    df_session = state['df_session'],
                    surface     = state['current_surface'],
                    surface_id = state['surface_id'],
                )

            time.sleep(sleep_sec)

    except KeyboardInterrupt:
        logger.log_system_event('shutdown', 'KeyboardInterrupt received')

    finally:
        # Close any open position on shutdown
        active = position_manager.get_active_position()
        if active is not None:
            logger.log_system_event('shutdown',
                'Closing active position on shutdown')
            current_tf = tf
            position_manager.close_position(
                active['id'],
                exit_price  = 0.0,   # will use live tick
                exit_reason = 'shutdown',
                exit_time   = datetime.now(),
                timeframe   = current_tf,
            )
        data_fetcher.disconnect()
        logger.log_system_event('shutdown', 'Live loop ended')

"""

if __name__ == '__main__':
    run_backtest()
    # run_live()