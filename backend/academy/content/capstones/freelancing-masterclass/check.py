"""Execute the delivered pilot and challenge mismatched promises, labels and data."""
import json,shutil,tempfile
from pathlib import Path
from engagement import deliver
ROOT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as folder:
 root=Path(folder);inputs=root/'client';shutil.copytree(ROOT/'client',inputs)
 report=deliver(inputs,root/'valid')
 assert report['restore_readback'] and report['scoped_local_handover']
 assert report['semantic_client_acceptance']=='not_performed' and not report['real_client_deployment']
 assert report['projected_minutes_saved']==90
 for name,change in [('offer.json',lambda data:data['promises'].append('automatic publication')),('acceptance.json',lambda data:data[0].update(text='Invented policy')),('changes.json',lambda data:data[0].update(decision='included')),('data-policy.json',lambda data:data['approved_fields'].append('private_email'))]:
  original=(inputs/name).read_text();data=json.loads(original);change(data);(inputs/name).write_text(json.dumps(data))
  try:deliver(inputs,root/name)
  except ValueError:pass
  else:raise AssertionError(name+' did not block invalid delivery')
  (inputs/name).write_text(original)
print('PASS: actual pilot, three acceptance cases, isolated restore; scope, false labels, extra data and unapproved change counterexamples blocked; human acceptance remains untested')
