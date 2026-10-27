---
id: M3-ENV-11
title: "A close-range Pemakar plume (it was built for 900 m; inside 300 m its billows facet and go black)"
role: environment
status: doing
owner_session: "env-art"
depends_on: [M3-ENV-09]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Follow-up to M3-ENV-09, from its worker. The Pemakar plume (`plume_vent` and the plume billows, with
`env_ash_plume.gdshader`) was built to read at 900 m. Inside about 300 m, which covers the Ashcrown zone and its
crater loggia, its billows show sharp facets and their shaded side goes near-black. The Ashcrown worker dropped
its crater-loggia view because of it.

## Acceptance criteria
- [ ] A near plume: a denser close LOD or a softer near piece, and a shader treatment so the shaded side keeps
      some value, built in the Pemakar or Ashcrown job.
- [ ] Ashcrown's crater-loggia view restored and viewed. No existing Pemakar or Ashcrown baseline drifts unless
      the plume is in frame; any re-approval is viewed and has a stated reason.
- [ ] Lights near any fog volume keep `light_volumetric_fog_energy = 0`.

## Review log
