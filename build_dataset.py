"""Build one complete, tidy CSV with every data point behind the visual.
One row = one value. Columns identify dataset, item, (for benchmarks) the run configuration,
date, value, unit, data type (measured / reported / derived) and source.
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent
COLS = ['dataset','item','model','task','gpu_model','num_gpus','max_num_seqs','date','value','unit','data_type','publisher','document','url']
rows = []
def add(dataset, item, value, unit, date, data_type, publisher, document, url, **cfg):
    rows.append(dict(dataset=dataset, item=item, value=value, unit=unit, date=date, data_type=data_type,
                     publisher=publisher, document=document, url=url, **cfg))

# 1. ML.ENERGY Leaderboard v3: every benchmark run, every scalar metric -------------
ML_URL = 'https://github.com/ml-energy/leaderboard/tree/2bdd0070186956688e1f842dc28077980fe64013/public/data/models'
METRICS = {'energy_per_request_joules':'J/response','energy_per_token_joules':'J/token','avg_output_len':'tokens/response',
           'avg_power_watts':'W','output_throughput_tokens_per_sec':'tokens/s','avg_batch_size':'requests',
           'median_itl_ms':'ms','p90_itl_ms':'ms','p95_itl_ms':'ms','p99_itl_ms':'ms'}
TASK = {'gpqa':'GPQA (long reasoning)','lm-arena-chat':'LM Arena (conversation)'}
wide = []
for p in sorted((ROOT/'raw/ml_energy').glob('Qwen__*.json')):
    obj = json.loads(p.read_text())
    for c in obj['configurations']:
        cfg = dict(model=obj['model_id'], task=TASK[obj['task']], gpu_model=c['gpu_model'],
                   num_gpus=c['num_gpus'], max_num_seqs=c['max_num_seqs'])
        for m, u in METRICS.items():
            add('ML.ENERGY Leaderboard v3 benchmark', m, c[m], u, '2025-2026 (v3 release)', 'measured',
                'ML.ENERGY', p.name, ML_URL, **cfg)
        add('ML.ENERGY Leaderboard v3 benchmark', 'gpu_energy_Wh_per_response', c['energy_per_request_joules']/3600,
            'Wh/response', '2025-2026 (v3 release)', 'derived (J / 3600)', 'author calculation', p.name, ML_URL, **cfg)
        wide.append({**cfg, **{m: c[m] for m in METRICS}, 'gpu_energy_Wh_per_response': c['energy_per_request_joules']/3600,
                     'precision': obj['weight_precision'], 'source_file': p.name})

# 2. ERCOT large-load queue -------------------------------------------------------------
T1 = ('ERCOT', 'ERCOT Update, Senate Committee on Business & Commerce (1 Apr 2026); MW by status as transcribed by Corley Energy',
      'https://www.ercot.com/files/docs/2026/04/01/ERCOT_LargeLoad_Update_April2026_B-C_-Hearing.pdf ; https://www.corleyenergy.com/ercot-large-load-queue.html')
for item, mw in [('Queue status: no studies submitted', 293651), ('Queue status: under ERCOT review', 86605),
                 ('Queue status: planning studies approved', 21343), ('Queue status: approved to energize, not operational', 3241),
                 ('Queue status: observed energized', 5778), ('Queue total (all statuses)', 410618)]:
    add('ERCOT large-load queue by status', item, mw, 'MW', '2026-03-26', 'reported', *T1)
add('ERCOT large-load queue by status', 'Data-center share of queue', 0.876, 'fraction', '2026-03-26', 'reported', 'ERCOT',
    'Board: Interconnection and Grid Analysis Update (13 Apr 2026), p.3', 'https://www.ercot.com/files/docs/2026/04/13/9-Interconnection-and-Grid-Analysis-Update.pdf')
LAT = ('Latitude Media citing ERCOT', "ERCOT's large load queue has nearly quadrupled in a single year",
       'https://www.latitudemedia.com/news/ercots-large-load-queue-has-nearly-quadrupled-in-a-single-year/')
add('ERCOT large-load queue over time', 'Queue total', 63000, 'MW', '2024-12', 'reported', *LAT)
add('ERCOT large-load queue over time', 'Queue total', 226000, 'MW', '2025-11', 'reported', *LAT)
add('ERCOT large-load queue over time', 'Queue total', 232000, 'MW', '2025-12-31', 'derived (410 GW minus 178 GW increase stated by ERCOT)', 'ERCOT',
    'Board: Interconnection and Grid Analysis Update (13 Apr 2026), p.3', 'https://www.ercot.com/files/docs/2026/04/13/9-Interconnection-and-Grid-Analysis-Update.pdf')
add('ERCOT large-load queue over time', 'Queue total', 410618, 'MW', '2026-03-26', 'reported', *T1)
add('ERCOT large-load queue over time', 'Queue total', 438000, 'MW', '2026-05', 'reported', 'ERCOT',
    'Board: Interconnection and Grid Analysis Update (May 2026), slides 1-2', 'https://www.ercot.com/files/docs/2026/05/24/8-Interconnection-and-Grid-Analysis-Update.pdf')
add('ERCOT large-load queue over time', 'New requests received in Q1 2026', 198, 'requests', '2026-Q1', 'reported', 'ERCOT',
    'Board: Interconnection and Grid Analysis Update (13 Apr 2026), p.2', 'https://www.ercot.com/files/docs/2026/04/13/9-Interconnection-and-Grid-Analysis-Update.pdf')

CON = ('ERCOT', '2025 Report on Existing and Potential Electric System Constraints and Needs (23 Dec 2025), slide 13',
       'https://www.ercot.com/files/docs/2025/12/23/2025-Report-on-Existing-and-Potential-Electric-System-Constraints-and-Needs.pdf')
add('ERCOT large-load queue over time', 'Queue total', 238600, 'MW', '2025-12-17', 'reported', *CON)
SEN = ('ERCOT', 'Senate testimony, Panel 1: Assessing the Grid (29 Jul 2026), slide 6 (as of June 2026)',
       'https://www.ercot.com/files/docs/2026/07/29/ERCOT-Senate-July-29-Panel-1-Assessing-The-Grid.pdf')
add('ERCOT large-load queue over time', 'Queue total', 474700, 'MW', '2026-06-30', 'reported', *SEN)
add('ERCOT large-load queue over time', 'Data-center share of queue', 0.902, 'fraction', '2026-06-30', 'reported', *SEN)
add('ERCOT Batch Zero screening', 'Batch Zero: eligible load (base + studied, 362 projects)', 194300, 'MW', '2026-09-03', 'derived (66.4 + 127.9 GW)',
    'ERCOT', 'Board: Batch Zero Update (Sep 2026)', 'https://www.ercot.com/files/docs/2026/09/11/14-Batch-Zero-Update.pdf')
EV = [('2025-06-20', 'Texas SB 6 signed: large loads must disclose duplicate requests and pay study fees', 'Mayer Brown (3 Jul 2025)',
       'https://www.mayerbrown.com/ja/insights/publications/2025/07/important-texas-regulatory-updates-for-data-centers'),
      ('2026-08-03', 'Gov. Abbott orders audit of every data center in the ERCOT queue', 'POWER Magazine',
       'https://www.powermag.com/abbott-orders-full-audit-of-texas-data-center-interconnection-queue-threatens-to-deny-grid-access/'),
      ('2026-09-03', 'ERCOT Batch Zero conditional classification released', 'ERCOT', 'https://www.ercot.com/files/docs/2026/09/11/14-Batch-Zero-Update.pdf')]
for d, item, pub, url in EV:
    add('Policy events', item, 1, 'event', d, 'reported', pub, item, url)

# 3. ERCOT large load actually energized ------------------------------------------------
TAC = ('ERCOT', 'Large Load Interconnection Status Update, TAC (Mar 2026)', 'https://www.ercot.com/files/docs/2026/03/12/March-TAC-Report.pdf')
OPS = ('ERCOT', 'Monthly Operational Overview (June 2026), slide 10', 'https://www.ercot.com/files/docs/2026/07/17/ERCOT-Monthly-Operational-Overview-June-2026.pdf')
add('ERCOT energized large load', 'Approved to energize (cumulative)', 9042, 'MW', '2026-03', 'reported', *TAC)
add('ERCOT energized large load', 'Observed non-simultaneous monthly peak of approved loads (date ambiguous: labelled Mar 2025 in a Mar 2026 report; not plotted)', 3883, 'MW', '2025-03', 'reported', *TAC)
add('ERCOT energized large load', 'Observed simultaneous monthly peak of approved loads', 3801, 'MW', '2025-03', 'reported', *TAC)
OPS8 = ('ERCOT', 'Monthly Operational Overview (August 2025), large-load slide', 'https://www.ercot.com/files/docs/2025/09/22/ERCOT-Monthly-Operational-Overview-August-2025.pdf')
OPS10 = ('ERCOT', 'Monthly Operational Overview (October 2025), large-load slide', 'https://www.ercot.com/files/docs/2025/11/17/ERCOT-Monthly-Operational-Overview-October-2025.pdf')
add('ERCOT energized large load', 'Approved to energize (cumulative)', 7502, 'MW', '2025-08', 'reported', *OPS8)
add('ERCOT energized large load', 'Observed non-simultaneous monthly peak of approved loads', 3694, 'MW', '2025-08', 'reported', *OPS8)
add('ERCOT energized large load', 'Observed non-simultaneous monthly peak of approved loads', 3960, 'MW', '2025-11', 'reported', *OPS10)
add('ERCOT energized large load', 'Approved to energize (cumulative)', 8926, 'MW', '2026-06', 'reported', *OPS)
add('ERCOT energized large load', 'Observed non-simultaneous monthly peak of approved loads', 3966, 'MW', '2026-06', 'reported', *OPS)
add('ERCOT energized large load', 'Large load expected to energize in Q4 2026', 3898, 'MW', '2026-Q4', 'reported', 'ERCOT',
    'Board: Interconnection and Grid Analysis Update (May 2026), slide 7 (sum of zones)', 'https://www.ercot.com/files/docs/2026/05/24/8-Interconnection-and-Grid-Analysis-Update.pdf')

# 4. ERCOT Batch Zero screening (context) ---------------------------------------------------
BZ = ('ERCOT', 'Board: Batch Zero Update (Sep 2026)', 'https://www.ercot.com/files/docs/2026/09/11/14-Batch-Zero-Update.pdf')
for item, gw in [('Batch Zero: base load (204 projects)', 66.4), ('Batch Zero: studied load (158 projects)', 127.9),
                 ('Batch Zero: excluded (373 projects)', 302.2)]:
    add('ERCOT Batch Zero screening', item, gw*1000, 'MW', '2026-09-03', 'reported', *BZ)

# 5. ERCOT peak demand records ----------------------------------------------------------
PK = ('ERCOT', 'Peak Demand Records (ranked list; 2026 unofficial until settlement)',
      'https://www.ercot.com/static-assets/data/news/content/a-peak-demand/all-time-records.htm')
for date, mw in [('2026-07-22',91089),('2023-08-10',85508),('2022-07-20',80148),('2019-08',74820),('2018-07',73473),
                 ('2016-08',71110),('2015-08',69877),('2011-08',68379),('2010-08',65776),('2009-07',63400),
                 ('2005-08',60274),('2003-08',60095),('2004-08',58531),('2000-08',57606)]:
    add('ERCOT peak demand records', 'Peak demand', mw, 'MW', date, 'reported', *PK)

# 6. AI energy per prompt and usage -----------------------------------------------------
G = ('Google', 'Measuring the environmental impact of AI inference (21 Aug 2025)',
     'https://cloud.google.com/blog/products/infrastructure/measuring-the-environmental-impact-of-ai-inference')
add('AI energy per prompt (company disclosures)', 'Gemini median text prompt, full data-center boundary', 0.24, 'Wh/prompt', '2025-05', 'reported', *G)
add('AI energy per prompt (company disclosures)', 'Gemini median text prompt, active chips only', 0.10, 'Wh/prompt', '2025-05', 'reported', *G)
add('AI energy per prompt (company disclosures)', 'Reduction in energy per median Gemini prompt, May 2024 to May 2025', 33, 'x', '2025-05', 'reported', *G)
add('AI energy per prompt (company disclosures)', 'ChatGPT average query', 0.34, 'Wh/query', '2025-06-10', 'reported',
    'OpenAI (Sam Altman)', 'The Gentle Singularity', 'https://blog.samaltman.com/the-gentle-singularity')
add('AI usage', 'ChatGPT prompts per day', 2.5e9, 'prompts/day', '2025-07-21', 'reported',
    'OpenAI via TechCrunch/Axios', 'ChatGPT users send 2.5 billion prompts a day', 'https://techcrunch.com/2025/07/21/chatgpt-users-send-2-5-billion-prompts-a-day/')

df = pd.DataFrame(rows).reindex(columns=COLS)
for c in ['num_gpus','max_num_seqs']: df[c] = df[c].astype('Int64')
df.to_csv(ROOT/'data/phantom_load_dataset.csv', index=False)
print(df.groupby('dataset').size().to_string()); print('total rows', len(df))
