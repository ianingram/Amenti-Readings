# The Three Musketeers — house style

This book has its own look, distinct from Dracula (gothic chiaroscuro, 1893) and A Tale of Two Cities (Victorian narrative painting with English watercolour). Every picture is drawn by Google (Nano Banana 2.1) through the storyboard workflow with the **style plate** as the style reference and the **fixed style sentence** below; faces come from the **cast portraits**.

## Painters to follow
- **Ernest Meissonier** — small-figure cavalier genre, exact costume, crisp daylight.
- **Maurice Leloir** — the illustrator of the 1894 *Trois Mousquetaires*: swagger, movement, humour.
- Secondary: **Jean-Léon Gérôme** for the Louvre and court interiors; **Gerard ter Borch / Vermeer** for quiet candlelit rooms.

## Palette and light
- **Day (roads, Meung, Paris streets, La Rochelle):** warm golden sunlight, high blue sky with spring clouds, sharp clean shadows, ochre stone, oak timbering, saturated costume colour (blue, crimson, violet, buff).
- **Dusk / night (Paris, the Cardinal, Milady):** deep blue dusk at windows against warm amber candlelight; never black-on-black gothic.
- **Interiors:** candle and firelight, rich glazes, polished oak, tapestry; the Louvre in gold and cream.

## Costume and period (1625)
- Doublets, falling lace collars, slashed sleeves, breeches, bucket-top boots with spurs, wide-brimmed plumed felt hats, rapiers on leather or embroidered baldrics, cloaks over one shoulder.
- Musketeers: the **blue cassock/tabard with the silver cross**. Cardinal's Guards: red with the white cross.
- Men: moustaches and small chin tufts are period-correct (except where the portrait says otherwise: d'Artagnan only the first down of a moustache).
- **Never:** tricorn hats, powdered wigs, 18th-century coats, Napoleonic uniforms, Victorian dress, modern objects.

## Architecture
- Timber-framed provincial inns and market towns (Meung), Paris of Louis XIII: narrow lanes, tall stone houses, the old Louvre, the Pont Neuf, the Luxembourg, churches with Gothic portals.

## Avoid
- Photographic or cinematic-render look; flat commercial illustration; fantasy armour; anime faces.
- Text, lettering, signatures (crop 7.5% if one appears), borders, black bars.
- Dracula's gothic darkness and Two Cities' English watercolour.

## Recipe (18 Nov 2026, Ian's choice after a side-by-side test)
- **Model:** `gemini-2.5-flash-image` (storyboard.yml `models=gemini-2.5-flash-image`, takes=1). No `"size"` — it draws 1K only.
- **References:** face portraits only, and only for beats with people in them. **No style plate as a reference** — it pulled the model toward the polished, commercial look Ian rejected. The plate now guides by description (below).
- **Repairs:** Nano Banana 2.1 (`gemini-nano-banana-2.1`) stays for edit/repair beats.
- **Signatures:** crop 7.5% where one appears.

## Fixed style sentence (every prompt)
> An oil painting of France in 1625, in the manner of Meissonier and Maurice Leloir, painted alla prima: visible loose brushstrokes, thick impasto in the lights, thin transparent glazes in the shadows, soft lost edges away from the faces, broken colour, canvas weave showing through; a single source of light, much of the picture in deep shadow (in daylight scenes: brilliant raking sun and crisp shadow instead); ordinary, unidealised faces, not glamorous, painted in a few planes; a candid, unposed moment, figures off-centre. Exact costume of 1625: doublets, falling lace collars, wide-brimmed plumed felt hats, bucket-top boots, rapiers on baldrics; no tricorns, no wigs. Honey-coloured stone, dark timber and ochre dust by day; candle-gold against blue Paris dusk by night. Not an illustration, not digital art. One single painting filling the whole 16:9 frame, no text, signature, border or black bars.

The plate's look, written in: honey stone, dark timber and ochre dust under a raking golden sun at Meung; candle-gold against blue dusk in Paris.

### Before 18 Nov (retired)
> A seventeenth-century French narrative oil painting in the manner of Meissonier and Maurice Leloir: academic realism, exact costume of 1625 … warm candlelight and golden daylight against blue Paris dusk, rich glazes, fine brushwork. (Used for the plates, the nine portraits, and a first set of opening pictures drawn with Nano Banana 2.1 at 2K, with the plate as a style reference.)

## Reference files (`the-three-musketeers/art/ref/`)
- **Style plate (chosen):** `plate.jpg` — the inn yard at Meung, golden afternoon.
- Candidates kept so Ian can switch: `plate-b.jpg` (the same yard, airier), `plate-c.jpg` (Tréville's antechamber by candle at dusk).
- **Cast portraits (3:4):** `dartagnan.jpg`, `rochefort.jpg`, `milady.jpg`, `athos.jpg`, `porthos.jpg`, `aramis.jpg`, `richelieu.jpg`, `constance.jpg`, `treville.jpg`.

## Anchors
Chosen after chapter 1 is placed: the three best chapter-1 pictures. Later chapters describe the look in words and may pass one anchor beside the faces (never the plate).

## Every batch
Contact sheet beside the plate and the anchors (by eye; they are not passed to the model); reject anything that drifts (photographic, illustrative/commercial, wrong period); check faces against the portraits; check corners for signatures.
