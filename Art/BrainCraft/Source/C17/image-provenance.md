# C17 moss surface

Generated using the built-in image-generation tool. The generated PNG was copied
unchanged to `Art/BrainCraft/Textures/T_C17_Moss_BaseColor.png` and is consumed by
the native `M_Craft_C17_Moss` material. This is a generated color texture with
some illustrated shading, not a scanned or calibrated PBR material set.

Original generated file: `exec-34771284-6758-4351-bc3c-cf64e685bd82.png`.

## Final prompt

Use case: stylized-concept. Asset type: a production-ready seamless square BASE
COLOR texture for a high-quality stylized 3D adventure game's welcoming zen
garden, quality inspiration The Legend of Zelda: Breath of the Wild. Create one
square, edge-to-edge orthographic top-down material texture, showing fine dense
cushion moss, very small clover-like ground leaves and tiny fine leaf litter.
Natural restrained sage, olive, yellow-green and deep blue-green hues, with subtle
warm earth visible between the moss cushions (no more than 15 percent earth).
Art-directed, gently hand-painted but crisp and richly resolved tiny moss fronds
and botanical structure, broad softly varying colonies at several scales. A calm
sophisticated material with readable fine detail, NOT smeared noise or flat green
paint. Seamless tiling on both axes, similar activity and luminance at all four
edges. Uniform diffuse neutral lighting, albedo-only: no baked cast shadows, no
ambient-occlusion black outlines, no directional sunlight, no highlights, no
perspective, no large leaves, no flowers, no stones, no buildings, no objects, no
text, no diagrams, no labels, no frame. The image is ONLY the material surface,
intended to wrap actual modeled terrain and to receive dynamic lighting in Unreal
Engine.

## Shading research

[Epic's bump-mapping documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/bump-mapping-without-tangent-space-in-unreal-engine)
describes the 2-by-2 screen derivative artifacts in low-quality bump normals.
The new moss shader evaluates texture heights at separate positions on the
surface; terrain also receives bounded physical mesh relief. This does not prove
the final material is visually accepted. Native images and movement checks are
required.
