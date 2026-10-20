"""公開準備の再現コマンド。保存済み入力を使い、各処理のログ・終了コードを残す。"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / 'publication'


def main():
    OUT.mkdir(exist_ok=True)
    commands = [
        [sys.executable, 'build_trip_calendar.py'],
        [sys.executable, 'build_publication.py'],
        ['node', 'render_publication.mjs'],
        [sys.executable, 'verify_publication.py'],
    ]
    execution = {'started_at_utc':datetime.now(timezone.utc).isoformat(), 'steps':[], 'status':'running'}
    with (OUT/'run.log').open('w',encoding='utf-8') as log:
        for command in commands:
            recorded_command = ['python', *command[1:]] if command[0] == sys.executable else command
            log.write('$ '+' '.join(recorded_command)+'\n')
            log.flush()
            result = subprocess.run(command,cwd=BASE,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            log.write(result.stdout+'\n')
            print(result.stdout,end='')
            execution['steps'].append({'command':recorded_command,'exit_code':result.returncode})
            if result.returncode:
                execution['status']='failed'
                break
        else:
            execution['status']='passed'
    execution['finished_at_utc']=datetime.now(timezone.utc).isoformat()
    execution['sha256']={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='execution.json'}
    for name in ['run_publication_review.py','render_publication.mjs']:
        execution['sha256'][name]=hashlib.sha256((BASE/name).read_bytes()).hexdigest()
    (OUT/'execution.json').write_text(json.dumps(execution,ensure_ascii=False,indent=2)+'\n')
    if execution['status']!='passed':
        raise SystemExit(1)


if __name__=='__main__':
    main()
