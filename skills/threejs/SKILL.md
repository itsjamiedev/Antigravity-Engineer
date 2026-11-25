---
name: threejs
description: Consolidated Three.js and WebGL 3D development skill covering scenes, cameras, renderers, geometry, PBR materials, lighting, shadows, HDR textures, GLTF loaders, animations, GLSL shaders, EffectComposer post-processing, and raycasting/OrbitControls interaction.
---

# Three.js & WebGL 3D Skill

Unified Progressive-Disclosure router replacing the 10 separate `threejs-*` sub-skills. Load only the topic reference(s) needed for the current task.

## Topic Router (`references/`)

| Reference File | Read When Implementing or Debugging |
| :--- | :--- |
| [references/fundamentals.md](references/fundamentals.md) | Scene graph, cameras, WebGLRenderer setup, resize loops, coordinate systems, Object3D transforms |
| [references/geometry.md](references/geometry.md) | Built-in primitives, `BufferGeometry`, custom vertex buffers, `InstancedMesh` optimization |
| [references/materials.md](references/materials.md) | PBR (`MeshStandardMaterial`, `MeshPhysicalMaterial`), basic/phong materials, transparency, material tuning |
| [references/lighting.md](references/lighting.md) | Light types, real-time shadow maps, light helpers, environment lighting / IBL |
| [references/textures.md](references/textures.md) | Texture channels, UV mapping, cubemaps, HDR environment maps, `WebGLRenderTarget`, mipmaps |
| [references/animation.md](references/animation.md) | `AnimationMixer`, GLTF skeletal clips, morph targets, procedural frame motion, crossfading |
| [references/loaders.md](references/loaders.md) | `GLTFLoader` / DRACO / KTX2 loading, `LoadingManager`, async progress, asset caching |
| [references/shaders.md](references/shaders.md) | Custom GLSL vertex/fragment shaders, `ShaderMaterial`, uniforms, `onBeforeCompile` |
| [references/postprocessing.md](references/postprocessing.md) | `EffectComposer`, bloom, depth of field, tone-mapping passes, custom screen-space passes |
| [references/interaction.md](references/interaction.md) | `Raycaster`, `OrbitControls`, pointer/touch picking, hover highlights, camera framing |

## Core Guardrails

- **Cleanup & Memory**: Always dispose geometries, materials, textures, render targets, and listeners cleanly on unmount or teardown (`dispose()`), and remove `requestAnimationFrame` / `ResizeObserver` handlers.
- **Responsive Viewport & DPI**: Cap `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))` and update camera aspect + projection matrix cleanly on resize.
- **Accessibility & Motion**: Honor `prefers-reduced-motion: reduce` by pausing or clamping continuous camera/object loops to a clear static resting frame.
