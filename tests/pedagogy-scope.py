"""Engineering briefs appear only where relevant; module identities match their teaching."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from academy.pedagogy import displayed_contract, program_contract
for slug in ['freelancing-masterclass','terminal-tutor','library-phase-00']:
    assert displayed_contract(slug,'01 · anything') is None
    assert program_contract(slug,['01 · anything']) is None
modules=['01 · Contracts and streaming','02 · Concurrency and recovery','03 · Providers and evidence','04 · Context and persistence','05 · Evaluation and service boundaries','06 · Integrated delivery']
course=program_contract('python-for-ai',modules)
assert len(course['modules'])==6
assert len({c['scenario'] for c in course['modules']})==6
for item in course['modules']:
    assert 'three synthetic policies' not in str(item)
    assert 'bounded agent' not in str(item)
    assert len(item['pillars'])==3
assert course['modules'][2]['family']=='adapter'
assert course['modules'][3]['family']=='retrieval'
assert course['modules'][5]['family']=='deployment'
assert 'HTTPX' in course['modules'][2]['pillars'][1]['application']
for slug in ['ai-agent-bootcamp','ai-workshops','ai-engineering-12-week','genai-accelerator']:
    assert program_contract(slug,['a taught engineering module']) is not None
print('PASS selective engineering brief and six Python-specific module contracts')
