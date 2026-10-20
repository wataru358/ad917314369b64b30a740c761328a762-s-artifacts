"""集計SQLを再利用せず、日別気象と宿泊Parquetから標準Pythonで検算する。

DuckDBの役割はParquetの読み出しだけ。休日の原本・境界日・公開表も照合する。
"""

import calendar
import csv
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import duckdb

BASE = Path(__file__).resolve().parent
DATA = BASE / "data/processed"
OUT = BASE / "publication"
checks = 0


def check(condition, message):
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message)


def close(a, b, message):
    check(math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-12), message)


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def rounded_percent(n, d):
    return float((Decimal(100) * n / d).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def verify_weather(con):
    by_place = defaultdict(list)
    for r in con.sql(f"SELECT destination_id,date,temp_max_c,temp_max_quality,precipitation_mm,precipitation_quality FROM '{DATA / 'jma_56_regions_daily_2016_2025.parquet'}' ORDER BY destination_id,date").fetchall():
        by_place[r[0]].append(r[1:])
    check(len(by_place) == 56, "56 destinations")
    calculated = {}
    for dest, days in by_place.items():
        check(len(days) == 3653, f"daily coverage {dest}")
        for i, day in enumerate(days):
            check(day[0] == date(2016,1,1) + timedelta(days=i), f"date continuity {dest} {i}")
        months = defaultdict(lambda: [0,0,0])
        for i in range(len(days)-3):
            trip = days[i:i+4]
            totals = months[trip[0][0].month]
            totals[0] += 1
            if not all(t is not None and p is not None and tq == pq == 8 for _,t,tq,p,pq in trip):
                continue
            totals[1] += 1
            temperatures = [d[1] for d in trip]
            rain = [d[3] for d in trip]
            # 不合格条件を直接評価。SQLの5つのカウント式は再利用しない。
            fails = (min(temperatures) < 10 or max(temperatures) >= 35
                     or sorted(temperatures)[-2] >= 30
                     or sorted(rain)[-2] >= 1 or max(rain) >= 30)
            totals[2] += not fails
        for m, counts in months.items():
            calculated[dest,m] = counts
    for row in read(OUT / "destination_months.csv"):
        key = row["destination_id"], int(row["start_month"])
        candidates, valid, matching = calculated[key]
        for col, expected in [("candidate_trips",candidates),("valid_trips",valid),("matching_trips",matching),("excluded_trips",candidates-valid)]:
            check(int(row[col]) == expected, f"{key} {col}")
        close(row["matching_trips_pct"],rounded_percent(matching,valid),f"weather percent {key}")
        close(row["valid_trips_pct"],rounded_percent(valid,candidates),f"valid percent {key}")
    return calculated


def verify_lodging(con):
    records = con.sql(f"SELECT year,month,prefecture_code,guest_nights FROM '{DATA / 'accommodation_monthly_2023_2025.parquet'}'").fetchall()
    check(len(records) == 1692, "lodging input size")
    check({(y,m,str(p).zfill(2)) for y,m,p,_ in records} == {(y,m,f'{p:02}') for y in (2023,2024,2025) for m in range(1,13) for p in range(1,48)}, "lodging input keys")
    annual = defaultdict(float)
    for y,m,p,n in records:
        annual[y,p] += n
    ratios = defaultdict(list)
    yearly = {}
    for y,m,p,n in records:
        ratio = (n / calendar.monthrange(y,m)[1]) / (annual[y,p] / (366 if calendar.isleap(y) else 365))
        ratios[str(p).zfill(2),m].append(ratio)
        yearly[y,m,str(p).zfill(2)] = ratio
    for r in read(DATA / "accommodation_demand_yearly_2023_2025.csv"):
        close(r["demand_ratio"],yearly[int(r["year"]),int(r["month"]),r["prefecture_code"]],"yearly lodging")
    for r in read(OUT / "destination_months.csv"):
        values = ratios[r["prefecture_code"],int(r["start_month"])]
        for column, value in [("demand_ratio_mean",sum(values)/3),("demand_ratio_min",min(values)),("demand_ratio_max",max(values))]:
            close(r[column],value,f"lodging {column}")


def verify_calendar():
    with (BASE / "data/calendar/syukujitsu.csv").open(encoding="cp932", newline="") as f:
        raw_rows = list(csv.reader(f))[1:]
    holidays = {date(*map(int,d.split("/"))): n for d,n in raw_rows}
    check(len(holidays) == len(raw_rows), "unique raw holidays")
    for d in [date(2019,4,30),date(2019,5,1),date(2020,7,23),date(2021,8,9),date(2026,9,22),date(2027,5,3)]:
        check(d in holidays, f"official exception fixture {d}")
    for d in [date(2020,7,20),date(2021,8,11)]:
        check(d not in holidays, f"moved holiday fixture {d}")
    metadata = json.loads((BASE / "data/calendar/source.json").read_text())
    check(hashlib.sha256((BASE / 'data/calendar/syukujitsu.csv').read_bytes()).hexdigest() == metadata['sha256'], 'raw calendar hash')
    normalized = read(OUT / "holidays_2016_2027.csv")
    check([(r['date'],r['name']) for r in normalized] == [(str(d),n) for d,n in sorted(holidays.items()) if 2016<=d.year<=2027], 'normalized holiday values')
    for r in normalized:
        check(r['source_sha256'] == metadata['sha256'] and r['source_url'] == metadata['url'], 'holiday provenance')
    for filename, first, count in [("trip_calendar_2016_2025.csv",date(2016,1,1),3650),("trip_calendar_2026_2027.csv",date(2026,1,1),727)]:
        rows = read(OUT / filename)
        check(len(rows) == count, filename)
        for i,r in enumerate(rows):
            start = first + timedelta(days=i)
            check(r["start_date"] == str(start), "calendar contiguous starts")
            check(r["end_date"] == str(start + timedelta(days=3)), "calendar end date")
            check(int(r["start_month"]) == start.month, "calendar month")
            days = {start + timedelta(days=j) for j in range(4)}
            h = days & holidays.keys()
            w = {d for d in days if d.isoweekday() in (6,7)}
            for col,value in [("holiday_days",len(h)),("weekend_days",len(w)),("weekend_or_holiday_days",len(h|w))]:
                check(int(r[col]) == value, f"calendar {col} {start}")
            check(r['holiday_dates'] == '|'.join(map(str,sorted(h))), 'holiday dates')
            check(r['holiday_names'] == '|'.join(holidays[d] for d in sorted(h)), 'holiday names')
    rows = read(OUT / "trip_calendar_2016_2025.csv")
    monthly = read(OUT / "trip_calendar_monthly_2016_2025.csv")
    check(len(monthly)==12 and {int(r['start_month']) for r in monthly}==set(range(1,13)), 'calendar monthly keys')
    for r in monthly:
        trips = [t for t in rows if t['start_month']==r['start_month']]
        n = sum(int(t['holiday_days'])>0 for t in trips)
        check(int(r['candidate_trips']) == len(trips), 'calendar monthly denominator')
        check(int(r['trips_with_holiday']) == n, 'calendar monthly holiday count')
        check(int(r['trips_with_weekend']) == sum(int(t['weekend_days'])>0 for t in trips), 'calendar monthly weekends')
        close(r['trips_with_holiday_pct'],100*n/len(trips),'calendar monthly share')
    future = {r['start_date']:r for r in read(OUT / 'trip_calendar_2026_2027.csv')}
    check(future['2027-04-30']['holiday_dates']=='2027-05-03', 'cross-month holiday')
    check('2027-12-29' not in future, 'unknown 2028 boundary excluded')


def verify_publication():
    rows = read(OUT / "destination_months.csv")
    old = {(r['destination_id'],r['start_month']):r for r in read(DATA / 'weather_accommodation_56_regions.csv')}
    check(len(rows)==672 and len({(r['destination_id'],r['start_month']) for r in rows})==672,'publication keys')
    for r in rows:
        source = old[r['destination_id'],r['start_month']]
        for k,v in source.items():
            check(r[k]==v, f'unchanged input column {k}')
        scores = sorted([float(p['matching_trips_pct']) for p in rows if p['start_month']==r['start_month']], reverse=True)
        check(int(r['weather_rank'])==scores.index(float(r['matching_trips_pct']))+1,'tie-preserving rank')
    for name, cutoff in [('monthly_top3.csv',3),('monthly_leaders.csv',1)]:
        check(read(OUT / name)==[r for r in rows if int(r['weather_rank'])<=cutoff],f'{name} complete selection')
    weight_rows = read(DATA / 'score_weight_comparison.csv')
    for r in weight_rows:
        original = old[r['destination_id'],r['start_month']]
        score = float(original['matching_trips_pct'])-int(r['coefficient'])*max(float(original['demand_ratio_mean'])-1,0)
        close(r['total_score'],score,'score recomputation')
        peers = [p for p in weight_rows if p['coefficient']==r['coefficient'] and p['start_month']==r['start_month']]
        rank = 1+sum(float(p['total_score'])>score for p in peers)
        check(int(r['month_rank'])==rank,'score rank')
    for r in read(OUT/'score_policy_risks.csv'):
        group = [p for p in weight_rows if p['coefficient']==r['coefficient']]
        expected = {
            'changed_destination_months':sum(p['month_rank']!=p['weather_rank'] for p in group),
            'negative_scores':sum(float(p['total_score'])<0 for p in group),
            'zero_weather_promoted':sum(float(p['matching_trips_pct'])==0 and int(p['month_rank'])<int(p['weather_rank']) for p in group),
            'max_rank_change':max(abs(int(p['month_rank'])-int(p['weather_rank'])) for p in group),
            'months_with_changed_leader':len({p['start_month'] for p in group if (p['month_rank']=='1')!=(p['weather_rank']=='1')}),
        }
        for k,v in expected.items():
            check(int(r[k])==v,f'policy risk {k}')
    # 本文の固定した数値も出典行に照合する。
    kurashiki = old['kurashiki','11']
    check((kurashiki['matching_trips'],kurashiki['valid_trips'])==('264','296'),'article Kurashiki numerator')
    article = (OUT/'travel-article.en.md').read_text()
    check('{{' not in article and len(article.split())>1000,'complete article template')
    for r in read(OUT/'monthly_top3.csv'):
        expected = f"| {r['weather_rank']} | {r['destination_en']} | {float(r['matching_trips_pct']):.1f}% | {r['matching_trips']} / {r['valid_trips']} | {float(r['valid_trips_pct']):.1f}% | {r['prefecture_en']} | {float(r['demand_ratio_mean']):.3f} |"
        check(expected in article,'article table row')
    # 図のセルを位置から読み戻し、CSVと数値・コントラストを照合する。
    svg = ET.parse(OUT/'weather-monthly.svg').getroot()
    ns = {'s':'http://www.w3.org/2000/svg'}
    cells = [e for e in svg.findall('.//s:rect',ns) if e.get('width')=='62']
    texts = {(e.get('x'),e.get('y')):e for e in svg.findall('.//s:text',ns)}
    dests = sorted({r['destination_id'] for r in rows if r['weather_rank']=='1'}|{'tokyo','kyoto'})
    check(len(cells)==len(dests)*12,'chart cell count')
    for cell in cells:
        x,y=int(cell.get('x')),int(cell.get('y'))
        label=texts[str(x+31),str(y+22)]
        dest,month=dests[(y-108)//38],(x-214)//65+1
        close(label.text,old[dest,str(month)]['matching_trips_pct'],'chart value')
        rgb=[int(cell.get('fill')[i:i+2],16)/255 for i in (1,3,5)]
        linear=[c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4 for c in rgb]
        lum=sum(c*w for c,w in zip(linear,(0.2126,0.7152,0.0722)))
        contrast=(lum+0.05)/0.05 if label.get('fill')=='#000' else 1.05/(lum+0.05)
        check(contrast>=4.5,'chart text contrast')
    for name in ['travel-article.en.md','learning-article.en.md','README.md']:
        for target in re.findall(r'\]\(([^)]+)\)',(OUT/name).read_text()):
            if not target.startswith(('https://','http://','#')):
                check((OUT/target.split('#')[0]).is_file(),f'local link {name}: {target}')


def main():
    con = duckdb.connect()
    try:
        verify_weather(con)
        verify_lodging(con)
    finally:
        con.close()
    verify_calendar()
    verify_publication()
    baseline = json.loads((OUT/'baseline_sha256.json').read_text())
    for path,digest in baseline.items():
        check(hashlib.sha256((BASE/path).read_bytes()).hexdigest()==digest,f'preserved {path}')
    inputs = [DATA/'jma_56_regions_daily_2016_2025.parquet',DATA/'accommodation_monthly_2023_2025.parquet',DATA/'weather_accommodation_56_regions.csv',BASE/'data/calendar/syukujitsu.csv']
    artifacts = list(OUT.glob('*.csv'))+list(OUT.glob('*.svg'))+list(OUT.glob('*.md'))
    codes = [BASE/p for p in ['build_trip_calendar.py','build_publication.py','verify_publication.py','publication-travel-template.md']]
    result = {
        'status':'passed','checks':checks,'verified_at_utc':datetime.now(timezone.utc).isoformat(),
        'weather_daily_rows':204568,'destination_months':672,'lodging_months':1692,
        'preserved_existing_files':len(baseline),
        'method':'Independent Python recomputation; DuckDB used only for Parquet reading',
        'limits':'Checks establish arithmetic and file consistency, not future predictive accuracy or inference validity.',
        'sha256':{str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs+artifacts+codes},
    }
    (OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f'PASS: {checks:,} checks; weather, lodging, holidays, rankings; {len(baseline)} existing files preserved')


if __name__=='__main__':
    main()
