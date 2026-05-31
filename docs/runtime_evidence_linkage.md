***# Runtime Evidence Linkage***



***This document links runtime and replay artifacts to the project evidence layer.***



***The goal is to keep runtime evidence separate from broad claims.***



***## Evidence chain***



***runtime claim***

***→ runtime artifact***

***→ replay or benchmark output***

***→ evidence map entry***

***→ chronology entry***



***## Current linkage targets***



***### Release-control behavior***



***PoR gate***

***→ PROCEED / NEEDS\_REVIEW / SILENCE***

***→ replay outputs***

***→ docs/evidence\_map.md***



***### Deterministic replay***



***candidate capture***

***→ fixture replay***

***→ stable decision trace***

***→ evidence map***



***### Release-risk examples***



***unsafe or ambiguous candidate***

***→ gate decision***

***→ replayable result***

***→ release-risk evidence***



***### Local runtime***



***candidate generation***

***→ local gate***

***→ runtime log***

***→ replay log***

***→ evidence map***



***## Evidence rules***



***- Prefer replayable artifacts.***

***- Prefer small curated outputs over raw logs.***

***- Do not store private archives here.***

***- Do not claim complete validation from partial evidence.***

***- Keep runtime behavior separate from model quality claims.***



***## Pending links***



***- release-risk v4 replay outputs***

***- local runtime logs***

***- hosted deployment traces***

***- curated Twitter/X chronology references***

***- issue #202 / #203 progress anchors***

