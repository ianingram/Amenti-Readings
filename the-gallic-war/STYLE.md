# The Gallic War — house style

**Recipe (18 Nov 2026, Ian's choice after a side-by-side test):** every scene is drawn by Google **gemini-2.5-flash-image** through the storyboard workflow (1K; it has no native 2K). **Only face portraits are passed as references, and only for people shots. The style plate is NOT passed as an image** — it pulled the model toward a polished, commercial look; the plate now guides by description, written into the style sentence below. Nano Banana 2.1 stays for edit/repair beats. Crop 7.5% where a signature appears. This page is the rule book so the look does not drift across 22 parts, and stays distinct from Dracula (dark Victorian chiaroscuro) and A Tale of Two Cities (English narrative painting and watercolour).

## What to make the pictures about (Ian, 19 Nov 2026)
1. **The size of the forests and the trees.** Gaul and Germany are mostly uncleared: primeval oak and beech forest to every horizon, trunks of otherworldly girth, men and columns tiny among them. Caesar's own measure (Book VI): the Hercynian forest is nine days' journey across and no one had reached its end after sixty days' march. Use it in every forest, march and German scene; write "colossal ancient oaks, trunks wider than a wagon, men tiny beneath them".
2. **The beauty of Roman country.** The Province and Italy: manicured lawns, villa estates, cypress avenues, sacred groves, gardens — the cultivated world Caesar sets out from and returns to (winters in Cisalpine Gaul, the opening film, the Province in Book I). Rome itself is a separate subject, for later.

## Painters to follow
- **Jean-Léon Gérôme**: crisp academic realism, hard clear light, exact archaeological detail.
- **Lawrence Alma-Tadema**: warm stone, marble and sky; clean edges; luminous colour.
- For battle and the march: **Ernest Meissonier**'s military pictures (many small figures, true kit, wide ground), **Adolphe Yvon**.
- Not: Romantic murk, fantasy-game art, glossy "commercial" illustration, photographic realism.

## Palette and light
- Default: **brilliant Mediterranean and Gaulish daylight** — deep blue sky, towering white clouds, warm sunlit stone and earth, clear blue shadow.
- Evening: golden light, long shadows, campfires in rows.
- Night: moonlit blue with warm firelight — used sparingly, for watches and night marches.
- Storm and the Ocean coast: grey-green sea, white surf, low cloud (Books III–V).
- Faces painted, not rendered; visible but fine brushwork.

## Kit and period (58–50 BC)
- **Legionaries**: mail shirt (*lorica hamata*), **never** the later segmented plate (*lorica segmentata*); bronze **Montefortino** or Coolus helmets with cheek-guards and a short horsehair crest; **oval or long curved scutum** (not the later rectangular one); **gladius** on the right hip; **pilum**; tunics red or undyed; hob-nailed sandals (*caligae*); red military cloaks for officers.
- Standards: the silver/gold **eagle** (*aquila*), red vexilla; cornu (circular horn) and tuba for signals.
- **Caesar**: about 42, lean, **bald with the hair combed forward**, clean-shaven, sharp features; red general's cloak (*paludamentum*), muscled cuirass on campaign.
- **Gauls**: long hair (often limed and swept back), **moustaches**, checked or striped trousers (*bracae*), cloaks pinned at the shoulder, **gold torcs**, long iron swords, oval or hexagonal shields, horned or crested bronze helmets for chiefs only, war-trumpets (*carnyx*) with animal heads.
- **Germans** (Ariovistus, Usipetes, Suebi): fewer clothes, skins, hair knotted to the side (the Suebian knot), spears and small shields.
- **Britons** (Books IV–V): chariots, blue woad, long hair, cliffs of Dover.
- Women and children with the wagons of the Helvetii; carts with solid wheels, oxen.

## Terrain
Great oak and beech forests (the Arduenna, the Hercynian), broad rivers (Rhône, Saône, Rhine, Thames), lake Geneva and the Jura, the Alps, oppida on hills (Bibracte, Avaricum, Gergovia, Alesia), marshes, the Atlantic coast of the Veneti, the white cliffs of Britain.

## Shots
Establishing and wide shots carry the narration — armies, columns, rivers, camps, sieges are Google's strength. Close-ups only for the few moments that need a face (Divitiacus pleading, Vercingetorix surrendering). Holds ≤ ~45 s.

## Avoid
Segmented plate armour; rectangular "Hollywood" shields; Roman helmets with tall transverse crests on common soldiers; medieval castles; stirrups (none in 58 BC); horned Viking helmets; Christian or later symbols; modern faces and haircuts; text, lettering, signatures (crop 7.5% if one appears); black bars.

## The fixed style sentence (in every sheet)
> An oil painting of 58 BC, in the manner of Jean-Léon Gérôme, Lawrence Alma-Tadema and Ernest Meissonier's military pictures, painted alla prima: visible loose brushstrokes, thick impasto in the lights, thin transparent glazes in the shadows, soft lost edges away from the faces, broken colour, canvas weave showing through; brilliant Mediterranean and Gaulish daylight — deep blue sky, towering white clouds, raking sun and crisp blue shadow on warm earth and stone (at night or by fire: a single source of light, much of the picture in deep shadow); ordinary, unidealised faces, not glamorous, painted in a few planes; a candid, unposed moment, figures off-centre. Roman legionaries in mail shirts, bronze Montefortino helmets and curved oval shields; Gauls with long hair, moustaches, checked trousers, cloaks and torcs. Not an illustration, not digital art. One single painting filling the whole 16:9 frame, no text, signature, border or black bars.

The plate's look in words: a legion winding along a dusty road through a wide green valley under towering white clouds, a river and blue mountains beyond; bright warm sun, blue shadow; mail, bronze, red shields and cloaks.

## Style search (18–19 Nov 2026, Ian)
Ian wants a more stylized look (Italian Renaissance, Greco-Roman classical; gothic epic for dark scenes, after Laurens, Doré, John Martin). Two Google tests failed: painters named in words (gemini-2.5-flash-image) and real public-domain paintings as style references (Nano Banana 2.1, 2K; `art/ref/style/`). Ian: "nothing works, both are bad." **Part 1's 52 pictures remain the baseline.** The plate is NOT approved. Next route: Midjourney sets the plate and key scenes (Ian), Google only far shots and repairs.

## Reference files
- Style plate (chosen; described, not passed as an image): `art/ref/plate.jpg` (Nano Banana 2.1, 1K). Candidates kept for switching: `art/ref/plate-a.jpg`, `art/ref/plate-b.jpg`, `art/ref/plate-c.jpg`.
- Portraits (3:4): `art/ref/caesar.jpg`, `labienus.jpg`, `vercingetorix.jpg`, `ariovistus.jpg`, `divitiacus.jpg`, `dumnorix.jpg`, `divico.jpg`.
- Anchors (chosen after Part 1 is placed; later parts use plate + one anchor as style refs): listed below.

## Anchors
Chosen from Part 1 (18 Nov). Later parts pass **one** anchor as a style reference beside the face portraits, matched to the scene's light:
- **Day, landscape and the march:** `art/ep01-alps.jpg` — the legion over the Alps in snow and sun.
- **Day, people:** `art/ep01-divico-speaks.jpg` — Divico before Caesar's tribunal.
- **Night and fire:** `art/ep01-x-tent-night.jpg` — Caesar's tent among the dark rows.
