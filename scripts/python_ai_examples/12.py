from dataclasses import dataclass

@dataclass(frozen=True)
class Evidence:
    unit_checks: bool
    owner_probe: bool
    restart_probe: bool
    load_probe: bool
    provider_semantics: bool

local = Evidence(True, True, True, False, False)
def release_scope(evidence):
    if not (evidence.unit_checks and evidence.owner_probe and evidence.restart_probe):
        return 'blocked'
    if not (evidence.load_probe and evidence.provider_semantics):
        return 'local fixture demonstration only'
    return 'eligible for review against a documented deployment target'

assert release_scope(local) == 'local fixture demonstration only'
assert release_scope(Evidence(False,True,True,True,True)) == 'blocked'
print(release_scope(local))
# This release decision is not the project: build all files in the capstone chapter.
