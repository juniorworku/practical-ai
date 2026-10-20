import type {ModulePedagogy} from './types'
/** A module-specific teaching brief, also used before imported reference readings. */
export default function EngineeringContract({contract}:{contract:ModulePedagogy}) {
 return <section className="engineering-contract" aria-label={`Engineering practice: ${contract.module}`}>
  <span className="eyebrow">BUILD · MEASURE · OPERATE</span>
  <h3>Apply this module to {contract.scenario}</h3>
  <p>{contract.software_first}</p>
  <dl>{contract.pillars.map(p=><div key={p.name}><dt>{p.name}</dt><dd>{p.application}</dd></div>)}</dl>
  <h4>Production and failure work</h4><p>{contract.operations}</p>
  <p>{contract.evaluation_note}</p>
  <details><summary>Module release evidence</summary><p>{contract.deliverable}</p><ul>{contract.release_gates.map(g=><li key={g}>{g}</li>)}</ul><p>Record what you actually tested. Simulated results and unchecked submissions do not establish production readiness.</p></details>
 </section>
}
