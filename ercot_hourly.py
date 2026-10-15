"""Process ERCOT Hourly Load Data Archive (Native Load, MW, hour ending, Central Prevailing Time).
Raw files: raw/ercot_hourly/Native_Load_YYYY.xlsx, downloaded from https://www.ercot.com/gridinfo/load/load_hist/index.html
Output: data/ercot_monthly_demand.csv
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
URL = 'https://www.ercot.com/gridinfo/load/load_hist/index.html'

def load():
    fr = []
    for f in sorted((ROOT/'raw/ercot_hourly').glob('Native_Load_*.xlsx')):
        d = pd.read_excel(f, sheet_name=0); d['source_file'] = f.name; fr.append(d)
    d = pd.concat(fr, ignore_index=True)
    s = d['Hour Ending'].astype(str)
    d['DST_repeat_hour'] = s.str.endswith('DST')          # extra hour at end of daylight saving time
    d['date'] = pd.to_datetime(s.str[:10], format='%m/%d/%Y')
    d['hour_ending'] = s.str[11:13].astype(int)
    d['month'] = d.date.dt.strftime('%Y-%m')
    assert d.ERCOT.notna().all() and (d.ERCOT > 0).all()
    zones = ['COAST','EAST','FWEST','NORTH','NCENT','SOUTH','SCENT','WEST']
    assert (d[zones].sum(axis=1) - d.ERCOT).abs().max() < 1     # zones add up to system total
    return d

if __name__ == '__main__':
    d = load()
    m = d.groupby('month').agg(hours=('ERCOT','size'), avg_demand_MW=('ERCOT','mean'), peak_demand_MW=('ERCOT','max')).reset_index()
    m.to_csv(ROOT/'data/ercot_monthly_demand.csv', index=False)
    y = d.groupby(d.date.dt.year).ERCOT.agg(['size','mean','max'])
    print(len(d), 'hours'); print(y.round(0))
