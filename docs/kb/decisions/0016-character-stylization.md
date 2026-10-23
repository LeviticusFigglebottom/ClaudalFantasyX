# 0016 — Hero character stylisation: painterly skin for close range; Q2 escalated

- **Status:** proposed (needs the human's answer on SPEC §16 Q2; the stylisation half can be applied now)
- **Date:** 2026-10-23
- **Roles affected:** Character, Rendering, Art, Cinematics, Lead
- **Author role:** Character Artist (M1-CHR-02)

## Context
SPEC §14 lists "procedural characters look uncanny or low quality" as a top risk. The mitigation is to prove one hero at final quality in M1, to lean on stylisation if photoreal fails (slightly painterly skin, strong silhouettes), and to record the result in an ADR. ADR 0010 built the base mesh from scratch (no MPFB). It says that if the M1-CHR-02 face review fails twice, Q2 (MPFB/MakeHuman as a topology donor) goes to the human.

M1-CHR-02 built Asha at final fidelity, entirely from code. The evidence is in [`asha_review.md`](../art/characters/asha_review.md):
- a lofted, sculpted head with loop flow, real lids and a field-baked normal map;
- separate eye shells, hair cards, costume panels, 30 face shapes and 10 visemes;
- LOD1 and Forward+ captures.

Verdict: at battle and field range (5 m and beyond, LOD1) she reads as the hero, by silhouette and palette. At dialogue range (a head-and-shoulders close-up) **the face still reads as uncanny**: a believable structure, but a stiff, slightly gaunt, mannequin-smooth face. This is the second face review to fail: the M1-CHR-01 review-sweep-B base face was the first.

## Options
1. **Keep pushing photoreal from scratch.** More sculpt terms, a second subdivision level on the face, wrinkle maps, a skin-albedo paint pass. The gap is anatomical knowledge, not technique, and every iteration is a manual numeric tune. Open-ended. Not recommended as the M1 answer.
2. **Stylise at close range, keep realistic proportions (recommended now).** Painterly skin (`painterly` around 0.6 instead of 0.2), lower pore and normal detail, and +15–20% lid aperture through the existing `lid_wide` shape. The rest of the hero stays as built. It is cheap (shader parameters and shape weights, no topology change), reversible, and it moves the face from "almost a real person" to "a painted person", which is the side of the valley SPEC §14 points at. It matches pillar 2's "beauty in decline" art direction better than a near-miss photoreal face.
3. **Stronger stylisation:** larger eyes (×1.2), a simplified nose and mouth plane, toon-ramped skin. This leaves SPEC §7.3 ("realistic adult proportions… larger eyes by about 10%") and would need a SPEC change. Kept as the fallback if option 2 still fails a human look.
4. **MPFB/MakeHuman as a topology and shape donor (SPEC §16 Q2).** It is the only option that adds the anatomical knowledge we lack. It needs the human: the assets are unreachable from this sandbox, and using them is a CC0 exception under SPEC §2 (ADR 0010).

## Decision
- **Adopt option 2 for every hero close-up now.** Dialogue, cinematic and portrait framing use `painterly` 0.6, `painterly_form` 0.3 and `detail_strength` 0.35, plus `lid_wide` 0.18 as part of the rest pose. Battle and field framing keep the as-built values (painterly 0.2), where the face is a few dozen pixels high. The side-by-side capture `asha_face_stylized_compare` is the reference: left as built, right stylised.
- **Escalate Q2 to the human** (ADR 0010's two-failure trigger). The question: may we vendor MPFB2's CC0 base mesh and targets as a topology donor, behind the existing interfaces (parameters JSON, landmarks, `DEF-*` skeleton, the asha.md §6.2 shape names)? Until the answer comes, option 2 stands, and Rhen and Toma use the same pipeline and the same close-range stylisation.
- Not decided here: changing SPEC §7.3's proportions (option 3). That needs a new ADR and a SPEC edit by the Lead.

## Consequences
- **Easier:** M1 can show a hero who is consistent across ranges without waiting on the human. The stylisation lives in shader parameters and shape weights, so Cinematics can tune it per shot, and Rendering owns the look.
- **Harder:** the close-range look now depends on the painterly path of the skin shader. At 1.0 that path reads as cel shading (character_shading.md), so the 0.6 cap matters. Art should author colour zones in the albedo (the warm nose and cheeks, the cooler jaw) to make the painted look intentional rather than a filter.
- **Watch:**
  1. Q2's answer. If yes, a new ADR supersedes ADR 0010 for the face. The body pipeline (loft field, cage, costume panels, hair, rig) stays.
  2. The first GPU review: lavapipe frames show no subsurface blur, so the skin may read softer on real hardware.
  3. Expression motion: still frames hide the stiffness that motion reveals. Lip-flap and blinks must be reviewed in a video capture before M2.
