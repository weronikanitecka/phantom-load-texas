"""Figure 1 (timeline): ERCOT large-load requests vs actual Texas demand and load actually connected, with policy events.
Reads data/phantom_load_dataset.csv and data/ercot_monthly_demand.csv (from ercot_hourly.py).  Run: python timeline.py
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parent
D = pd.read_csv(ROOT/'data/phantom_load_dataset.csv'); D['value'] = pd.to_numeric(D.value, errors='coerce')
def when(s):  # 'YYYY-MM' -> mid-month; full dates as is
    return pd.Timestamp(s + '-15') if len(s) == 7 else pd.Timestamp(s)

q = D[(D.dataset=='ERCOT large-load queue over time') & (D.item=='Queue total') & (D.data_type=='reported')].copy()
q['t'] = q.date.map(when); q = q.sort_values('t'); q['gw'] = q.value/1000
c = D[(D.dataset=='ERCOT energized large load') & (D.item=='Observed non-simultaneous monthly peak of approved loads')].copy()
c['t'] = c.date.map(when); c = c.sort_values('t'); c['gw'] = c.value/1000
peak = D[(D.dataset=='ERCOT peak demand records')].value.max()/1000
bz = D[D.item.str.startswith('Batch Zero: eligible')].iloc[0]; bz_t, bz_gw = when(bz.date), bz.value/1000
excl = D[D.item.str.startswith('Batch Zero: excluded')].value.iloc[0]/1000
dc_share = D[(D.item=='Data-center share of queue') & (D.date=='2026-06-30')].value.iloc[0]
ev = D[D.dataset=='Policy events'].copy(); ev['t'] = ev.date.map(when)
M = pd.read_csv(ROOT/'data/ercot_monthly_demand.csv'); M['t'] = M.month.map(when); M['gw'] = M.peak_demand_MW/1000
M = M[M.t >= '2024-01-01']
pk24 = M[M.month.str.startswith('2024')].gw.max(); pk26 = M[M.month.str.startswith('2026')].gw.max()

BLUE, VERM, GREY, INK, MUTED = '#0072B2', '#D55E00', '#8C969D', '#1A1A1A', '#555555'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,
    'axes.spines.left':False,'axes.edgecolor':'#9AA5AD','text.color':INK,'xtick.color':'#444444','ytick.color':'#444444','pdf.fonttype':42})
fig = plt.figure(figsize=(14, 9.2), facecolor='white')
fig.text(.06, .955, 'Figure 1. Texas data-center power requests exploded; actual demand barely moved',
         fontsize=18, weight='bold', va='top')
ax = fig.add_axes([.08, .31, .84, .56])
ax.grid(axis='y', color='#E6E8EA'); ax.set_axisbelow(True); ax.tick_params(length=0, pad=7)

# events (vertical lines, like annotated timelines)
lab = {'2025-06-20': ('SB 6 signed', 535), '2026-08-03': ('Audit\nordered', 400), '2026-09-03': ('ERCOT\nscreening', 535)}
for _, e in ev.iterrows():
    ax.axvline(e.t, color='#6B7378', lw=1.2, ls=(0,(4,3)), zorder=1)
    txt, y = lab[e.date]; right = e.date in ('2026-09-03', '2025-06-20')
    ax.text(e.t + pd.Timedelta(days=6 if right else -6), y, txt, ha='left' if right else 'right', va='top', fontsize=10, color=MUTED, linespacing=1.3)

# actual Texas demand from ERCOT hourly data (monthly peak hour)
ax.plot(M.t, M.gw, color=GREY, lw=2.2, zorder=3)
ax.text(M.t.iloc[M.gw.idxmax()-M.index[0]] - pd.Timedelta(days=12), pk26 + 8, f'{pk26:.0f} GW', fontsize=11, color='#5F686E', weight='bold', ha='right', va='bottom')

# series
ax.plot(q.t, q.gw, color=VERM, lw=3, marker='o', ms=7, zorder=4)
ax.plot(c.t, c.gw, color=BLUE, lw=3, marker='o', ms=7, zorder=4)
ax.text(q.t.iloc[-1], q.gw.iloc[-1] + 14, f'{q.gw.iloc[-1]:.0f} GW', color=VERM, fontsize=12, weight='bold', ha='right', va='bottom')
ax.text(q.t.iloc[0] - pd.Timedelta(days=10), q.gw.iloc[0] + 30, f'{q.gw.iloc[0]:.0f} GW', color=VERM, fontsize=12, weight='bold', ha='center', va='bottom')
ax.text(c.t.iloc[-1] + pd.Timedelta(days=10), c.gw.iloc[-1] + 14, f'{c.gw.iloc[-1]:.0f} GW', color=BLUE, fontsize=11, weight='bold', va='bottom')

# Batch Zero outcome
ax.scatter([bz_t], [bz_gw], s=90, facecolor='white', edgecolor=VERM, lw=2.5, zorder=5)
ax.annotate('', xy=(bz_t, bz_gw + 8), xytext=(bz_t, q.gw.iloc[-1]), arrowprops=dict(arrowstyle='->', color=VERM, lw=1.6, ls='--'))
ax.text(bz_t + pd.Timedelta(days=10), bz_gw, f'{bz_gw:.0f} GW', color=VERM, fontsize=11, weight='bold', va='center')

ax.set_xlim(pd.Timestamp('2023-12-15'), pd.Timestamp('2026-11-15')); ax.set_ylim(0, 560)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,4,7,10])); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
ax.set_ylabel('Gigawatts (GW)', labelpad=8)
from matplotlib.lines import Line2D
handles = [Line2D([], [], color=VERM, lw=3, marker='o', ms=7, label='Requested to connect (large-load queue, ~90% data centers)'),
           Line2D([], [], color=GREY, lw=2.2, label='Actual Texas demand (monthly peak hour, all users)'),
           Line2D([], [], color=BLUE, lw=3, marker='o', ms=7, label='Large loads actually running'),
           Line2D([], [], color=VERM, lw=0, marker='o', ms=9, markerfacecolor='white', markeredgewidth=2.2, label="Passed ERCOT's first screening (Batch Zero)"),
           Line2D([], [], color='#6B7378', lw=1.2, ls=(0,(4,3)), label='Policy event')]
fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(.075, .245), ncol=3, frameon=False, fontsize=10.8, handlelength=2.6, columnspacing=1.8)

fig.add_artist(plt.Line2D([.06,.94],[.158,.158], color='#C9CED2', lw=1))
fig.text(.06, .146,
 f'Takeaway: Requests to connect large loads (about {dc_share:.0%} data centers) rose from {q.gw.iloc[0]:.0f} GW to {q.gw.iloc[-1]:.0f} GW in 18 months, {q.gw.iloc[-1]/pk26:.0f}\u00d7 Texas\'s record peak.\n'
 f'Actual peak demand rose only from {pk24:.0f} to {pk26:.0f} GW (2024\u20132026), and large loads actually running stayed near {c.gw.iloc[-1]:.0f} GW. Much of the queue is "phantom" load.',
 fontsize=12.3, va='top', linespacing=1.5)
fig.text(.06, .012,
 'Data sources: ERCOT (Texas grid operator). Actual demand: ERCOT Hourly Load Data Archive, native load, 32,855 hourly readings (Jan 2023 – Sep 2026), monthly peak hour. Requested load:\n'
 'ERCOT board and Texas Senate presentations (Dec 2025 – Jun 2026); Dec 2024 and Nov 2025 values as reported by Latitude Media citing ERCOT. Load actually running: ERCOT monthly operational\n'
 'reports (observed monthly peak of approved large loads, all types). Screening: ERCOT Batch Zero update (Sep 2026). Events: Texas SB 6 (Mayer Brown); governor\'s audit order (POWER Magazine).',
 fontsize=8.8, color=MUTED, linespacing=1.5)

# Export exactly the data plotted in this figure
keep = pd.concat([
    q.assign(series='Requested to connect (large-load queue)'),
    c.assign(series='Actually running (observed monthly peak of approved large loads)'),
    M.assign(series='Actual Texas demand, monthly peak hour (calculated from ERCOT hourly data)', date=M.month, item='Monthly peak hourly demand (max of hourly native load)',
             value=M.peak_demand_MW, unit='MW', data_type='derived from raw hourly data', publisher='ERCOT', document='Hourly Load Data Archive (Native Load)', url='https://www.ercot.com/gridinfo/load/load_hist/index.html'),
    D[D.item.str.startswith('Batch Zero: eligible') | D.item.str.startswith('Batch Zero: excluded')].assign(series='ERCOT Batch Zero screening'),
    D[(D.item=='Data-center share of queue') & (D.date=='2026-06-30')].assign(series='Data-center share of queue (takeaway)'),
    ev.assign(series='Policy event (vertical line)')])
out = keep[['series','date','item','value','unit','data_type','publisher','document','url']].copy()
out.loc[out.unit=='MW','value_GW'] = out.loc[out.unit=='MW','value']/1000
out.loc[out.unit=='event', ['value','unit']] = [None, None]
out = out[['series','date','item','value','unit','value_GW','data_type','publisher','document','url']]
out.to_csv(ROOT/'data/figure1_data.csv', index=False)
for ext in ['png', 'pdf']:
    fig.savefig(ROOT/f'figures/phantom_load_timeline.{ext}', dpi=220, facecolor='white')
print(q[['date','gw']].to_string(index=False)); print(c[['date','gw']].to_string(index=False))
