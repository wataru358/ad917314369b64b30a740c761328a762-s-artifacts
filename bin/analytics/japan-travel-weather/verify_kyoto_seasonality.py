"""DuckDBの計算を、標準ライブラリのcalendar/csvで独立に再計算する。"""
import calendar
import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

BASE = Path(__file__).resolve().parent
DATA = BASE / 'data' / 'processed'
checks = 0


def require(condition, message):
    global checks
    checks += 1
    if not condition:
        raise ValueError(message)


def close(actual, expected, message):
    require(math.isclose(float(actual), expected, rel_tol=1e-12, abs_tol=1e-12), message)


def read(name):
    with (DATA / name).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def keyed(rows, fields, expected):
    result = {tuple(r[k] for k in fields): r for r in rows}
    require(len(rows) == len(result) and set(result) == expected, f'キー不一致: {fields}')
    return result


def main():
    raw = read('kyoto_tourism_monthly_2023_2025.csv')
    keyed(raw, ('year', 'month'), {(str(y), str(m)) for y in (2023, 2024, 2025) for m in range(1, 13)})
    fields = {'visitors': 'visitors_thousands', 'day_visitors': 'day_visitors_thousands',
              'guest_nights': 'guest_nights_thousands'}
    lodging = {(int(r['year']), int(r['month'])): float(r['demand_ratio'])
               for r in read('accommodation_demand_yearly_2023_2025.csv') if r['prefecture'] == '京都府'}
    weather = {int(r['start_month']): r for r in read('weather_accommodation_56_regions.csv')
               if r['destination_id'] == 'kyoto'}
    require(len(lodging) == 36 and len(weather) == 12, '比較元の件数が違います')
    oracle, raw_by_key = {}, {}
    for r in raw:
        year, month = int(r['year']), int(r['month'])
        days, year_days = calendar.monthrange(year, month)[1], 365 + calendar.isleap(year)
        require(r['source_report_year'] == ('2024' if year == 2023 else '2025'), '採用版が違います')
        require(r['source_sha256'] == digest(BASE / 'data/tourism/kyoto' / r['source_file']), '原本ハッシュ不一致')
        for metric, field in fields.items():
            annual = sum(int(q[field]) for q in raw if int(q['year']) == year)
            value = (int(r[field]) / days) / (annual / year_days)
            oracle[year, month, metric] = value
            raw_by_key[year, month, metric] = r
    files = {
        'kyoto_tourism_ratios_yearly.csv': (108, ('year', 'month', 'metric')),
        'kyoto_seasonality_comparison.csv': (36, ('month', 'metric')),
        'kyoto_seasonality_summary.csv': (3, ('metric',)),
        'kyoto_seasonality_yearly_peaks.csv': (9, ('year', 'metric')),
        'kyoto_seasonality_monthly_overview.csv': (12, ('month',)),
        'kyoto_seasonality_comparison_2024_2025.csv': (36, ('month', 'metric')),
    }
    output = {name: read(name) for name in files}
    for name, (count, keys) in files.items():
        rows = output[name]
        require(len(rows) == count, f'{name}: 行数不一致')
        require(len({tuple(r[k] for k in keys) for r in rows}) == count, f'{name}: キー重複')
    for r in output['kyoto_tourism_ratios_yearly.csv']:
        year, month, metric = int(r['year']), int(r['month']), r['metric']
        value = oracle[year, month, metric]
        close(r['tourism_ratio'], value, '年別比率不一致')
        close(r['lodging_ratio'], lodging[year, month], '同年の府宿泊比率不一致')
        close(r['ratio_gap'], value - lodging[year, month], '年別比率差不一致')
        for field, expected in raw_by_key[year, month, metric].items():
            require(r[field] == expected, f'原本情報の不一致: {field}')
    for year in (2023, 2024, 2025):
        for metric in fields:
            close(sum(oracle[year, m, metric] * calendar.monthrange(year, m)[1]
                      for m in range(1, 13)) / (365 + calendar.isleap(year)), 1, '加重平均不一致')
    monthly = {}
    for r in output['kyoto_seasonality_comparison.csv']:
        m, k = int(r['month']), r['metric']
        values = [oracle[y, m, k] for y in (2023, 2024, 2025)]
        prefecture = [lodging[y, m] for y in (2023, 2024, 2025)]
        for prefix, series in [('tourism', values), ('lodging', prefecture)]:
            for suffix, function in [('mean', mean), ('min', min), ('max', max)]:
                close(r[f'{prefix}_ratio_{suffix}'], function(series), '月別集計不一致')
        close(r['ratio_gap'], mean(values) - mean(prefecture), '月別比率差不一致')
        require(r['tourism_years_count'] == r['lodging_years_count'] == '3', '年数不一致')
        for field in ('matching_trips_pct', 'valid_trips_pct'):
            close(r[field], float(weather[m][field]), '気象値が変わっています')
        monthly[m, k] = mean(values)
    pref_mean = {m: mean(lodging[y, m] for y in (2023, 2024, 2025)) for m in range(1, 13)}
    def peaks(series):
        return ','.join(str(m) for m in range(1, 13) if series[m] == max(series.values()))
    for r in output['kyoto_seasonality_summary.csv']:
        k = r['metric']
        series = {m: monthly[m, k] for m in range(1, 13)}
        require(r['tourism_peak_months'] == peaks(series), '平均ピーク不一致')
        require(r['lodging_peak_months'] == peaks(pref_mean), '府平均ピーク不一致')
        gaps = [abs(series[m] - pref_mean[m]) for m in range(1, 13)]
        close(r['mean_absolute_gap'], mean(gaps), '平均絶対差不一致')
        close(r['max_absolute_gap'], max(gaps), '最大絶対差不一致')
        require(int(r['opposite_season_months']) == sum((series[m] - 1) * (pref_mean[m] - 1) < 0
                    for m in range(1, 13)), '方向が逆の月数不一致')
    for r in output['kyoto_seasonality_yearly_peaks.csv']:
        y, k = int(r['year']), r['metric']
        series = {m: oracle[y, m, k] for m in range(1, 13)}
        require(r['tourism_peak_months'] == peaks(series), '年別ピーク不一致')
        close(r['tourism_peak_ratio'], max(series.values()), '年別最大比率不一致')
        require(r['lodging_peak_months'] == peaks({m: lodging[y, m] for m in range(1, 13)}), '府年別ピーク不一致')
    for r in output['kyoto_seasonality_monthly_overview.csv']:
        m = int(r['month'])
        for metric in fields:
            close(r[f'{metric}_ratio'], monthly[m, metric], '横持ち表不一致')
        close(r['prefecture_lodging_ratio'], pref_mean[m], '横持ち府比率不一致')
        for field in ('matching_trips_pct', 'valid_trips_pct'):
            close(r[field], float(weather[m][field]), '横持ち気象不一致')
    for r in output['kyoto_seasonality_comparison_2024_2025.csv']:
        m, k = int(r['month']), r['metric']
        a, b = mean(oracle[y, m, k] for y in (2024, 2025)), mean(lodging[y, m] for y in (2024, 2025))
        require(r['years_count'] == '2', '感度表の年数不一致')
        close(r['tourism_ratio_mean'], a, '2年平均不一致')
        close(r['lodging_ratio_mean'], b, '2年府平均不一致')
        close(r['ratio_gap'], a - b, '2年差不一致')
    inputs = [DATA / name for name in ('kyoto_tourism_monthly_2023_2025.csv',
              'accommodation_demand_yearly_2023_2025.csv', 'weather_accommodation_56_regions.csv')]
    inputs += [BASE / 'data/tourism/kyoto' / name for name in ('honsatsu.pdf', 'R6honsatsu.pdf')]
    report = dict(status='passed', checked_at_utc=datetime.now(timezone.utc).isoformat(), checks=checks,
                  relative_tolerance=1e-12, absolute_tolerance=1e-12,
                  inputs={str(p.relative_to(BASE)): digest(p) for p in inputs},
                  outputs={name: {'rows': len(output[name]), 'sha256': digest(DATA / name)} for name in files},
                  scripts={name: digest(BASE / name) for name in ('compare_kyoto_seasonality.py', 'verify_kyoto_seasonality.py')})
    target = DATA / 'kyoto_seasonality_validation.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f'独立検算OK: {checks}チェック / 比率108行・6出力・原本ハッシュ・気象値を確認')
    print(f'保存: {target.name}')


if __name__ == '__main__':
    main()
