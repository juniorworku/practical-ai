"""A complete fictional client delivery. Observations are produced, not prefilled passed flags."""
import argparse,csv,hashlib,json,shutil,sqlite3,time
from pathlib import Path

def fingerprint(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(root,name):return json.loads((root/name).read_text())
def deliver(root,out):
 root=root.resolve();out.mkdir(parents=True,exist_ok=True)
 offer=load(root,'offer.json');scope=load(root,'scope.json');baseline=load(root,'baseline.json');data=load(root,'data-policy.json');support=load(root,'support.json');changes=load(root,'changes.json');tests=load(root,'acceptance.json')
 if offer['client']!=scope['client'] or support['client']!=scope['client']:raise ValueError('client_identity_disagreement')
 if set(offer['promises'])-set(scope['included']):raise ValueError('offer_exceeds_scope')
 if not set(scope['acceptance_ids'])<=set(t['id'] for t in tests):raise ValueError('acceptance_missing')
 if data['approved_fields']!=['id','source','text'] or data['retention_days']!=7:raise ValueError('data_policy')
 if any(c['decision']=='included' and c['request'] not in scope['included'] for c in changes):raise ValueError('unapproved_scope_change')
 source=list(csv.DictReader((root/'requests.csv').open(newline='')))
 if any(set(row)!=set(data['approved_fields']) for row in source):raise ValueError('unapproved_data_fields')
 database=out/'pilot.sqlite3'
 if database.exists():raise FileExistsError('Use a fresh output directory; retain prior evidence.')
 with sqlite3.connect(database) as db:
  db.execute('CREATE TABLE drafts(id TEXT PRIMARY KEY,source TEXT NOT NULL,text TEXT,status TEXT NOT NULL)')
  for row in source:
   # Extract the authorized source verbatim; missing evidence routes to review.
   status='draft_for_review' if row['source']=='policy-v1' and row['text'].strip() else 'needs_source'
   db.execute('INSERT INTO drafts VALUES(?,?,?,?)',(row['id'],row['source'],row['text'] if status=='draft_for_review' else None,status))
 with sqlite3.connect(database) as db:
  actual={r[0]:{'source':r[1],'text':r[2],'status':r[3]} for r in db.execute('SELECT * FROM drafts')}
 results=[]
 for test in tests:
  got=actual.get(test['request_id']);passed=got is not None and got['status']==test['status'] and got['text']==test['text']
  results.append({'id':test['id'],'passed':passed,'actual':got})
 # Fresh destination and connection establish an actual restore, not a copied boolean.
 backup=out/'backup.sqlite3';restored=out/'restored.sqlite3';start=time.perf_counter()
 with sqlite3.connect(database) as db,sqlite3.connect(backup) as target:db.backup(target)
 shutil.copy2(backup,restored)
 with sqlite3.connect(restored) as db:restored_rows=list(db.execute('SELECT * FROM drafts ORDER BY id'))
 with sqlite3.connect(database) as db:original_rows=list(db.execute('SELECT * FROM drafts ORDER BY id'))
 recovery=restored_rows==original_rows
 restore_ms=(time.perf_counter()-start)*1000
 # Economics are an illustrative business estimate, separate from measured script time.
 projected=baseline['weekly_items']*(baseline['old_minutes']-baseline['new_review_minutes'])-baseline['weekly_maintenance_minutes']
 ready=all(r['passed'] for r in results) and recovery and support['manual_fallback']=='retain input and use approved source manually'
 report={'client':scope['client'],'engagement':'fictional_simulation','mechanical_acceptance':results,'restore_readback':recovery,'restore_ms':round(restore_ms,3),'projected_minutes_saved':projected,'projection_measured':False,'semantic_client_acceptance':'not_performed','real_client_deployment':False,'scoped_local_handover':ready,'usage_cost_usd':None,'retention_days':data['retention_days'],'context_policy':'only approved source text; no cross-client reuse','input_versions':{p.name:fingerprint(p) for p in root.iterdir() if p.is_file()}}
 (out/'acceptance-report.json').write_text(json.dumps(report,indent=2))
 (out/'client-email.md').write_text(f"# Simulated handover to {scope['client']}\n\nThe local pilot produced {len(results)} mechanical checks and an isolated restore readback of {recovery}. Human factual acceptance and real client hosting remain untested. No automatic sending or publication is included. The time-saving projection ({projected} minutes/week) is illustrative, not observed ROI.\n")
 (out/'case-study.md').write_text('# Fictional case study\n\nA source-extractive handout pilot preserves missing evidence as needs_source. It writes reviewed drafts, not published content. Consult acceptance-report.json for measured local checks, unresolved factual acceptance and illustrative business assumptions. This is a training engagement and may not be marketed as a client result.\n')
 if not ready:raise ValueError('mechanical_acceptance_failed; inspect retained report')
 return report
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--inputs',type=Path,default=Path('client'));parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();report=deliver(args.inputs,args.output);print(json.dumps({'scoped_local_handover':report['scoped_local_handover'],'client_acceptance':report['semantic_client_acceptance']}))
