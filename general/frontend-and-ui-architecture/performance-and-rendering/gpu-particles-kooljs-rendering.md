---
okf_version: "1.0"
id: "okf-fro-per-gpu-particles-kooljs-rendering"
title: "High-Performance Web Graphics: Instanced GPU Particle Systems & Multithreaded kooljs Animation"
topic: "general/frontend-and-ui-architecture"
subtopic: "performance-and-rendering"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - gpu-particles
  - threejs
  - kooljs
  - webgl
  - web-workers
  - instanced-mesh
summary: "Technical architectural specification for GPU-driven WebGL particle systems (ji-GPU-Particles) and multithreaded off-main-thread Web Worker animation engines (kooljs)."
---

# High-Performance Web Graphics: Instanced GPU Particle Systems & Multithreaded kooljs Animation

## Executive Summary

Real-time 3D web applications and complex UI animations frequently encounter performance bottlenecks due to JavaScript's single-threaded event loop. Updating transform matrices for tens of thousands of individual objects or evaluating complex physics on the CPU main thread leads to dropped frames and UI jank.

This document details two complementary high-performance web graphics architectures: **`ji-GPU-Particles`** (a fully GPU-driven Three.js particle system using `InstancedMesh` and custom GLSL vertex shaders) and **`kooljs`** (a multithreaded Web Worker animation engine for HTML and React).

---

## 1. System Architecture

```
+-------------------------------------------------------------------+
| Browser Main Thread (UI DOM / WebGL Render Loop)                  |
+---------------------------------+---------------------------------+
                                  |
                                  | SharedArrayBuffer / Transferable
                                  v
+-------------------------------------------------------------------+
| kooljs Web Worker Thread (Off-Main-Thread Execution)              |
| (60/120 FPS Tick Engine, Spring Physics, Cubic-Bezier Easing)    |
+---------------------------------+---------------------------------+
                                  |
                                  | Instanced Uniforms / Attribute Arrays
                                  v
+-------------------------------------------------------------------+
| GPU Hardware (WebGL2 / WebGPU Execution)                          |
| (ji-GPU-Particles GLSL Vertex Shader Displacement Over Lifetime)  |
+-------------------------------------------------------------------+
```

---

## 2. Instanced GPU Particles Architecture (`ji-GPU-Particles`)

Instead of updating individual particle position matrices on the CPU each frame, `ji-GPU-Particles` passes instance-specific attributes (lifetime, initial velocity, force field vectors) to a custom GLSL shader. Position displacement over time is evaluated entirely in parallel on the GPU vertex shader.

### 2.1 GLSL Vertex Shader Displacement Example

```glsl
attribute vec3 instanceVelocity;
attribute float instanceLife;
attribute float instanceBirthTime;

uniform float uTime;
uniform vec3 uGravity;

varying float vAgeRatio;

void main() {
    float age = uTime - instanceBirthTime;
    vAgeRatio = age / instanceLife;

    if (age < 0.0 || age > instanceLife) {
        // Hide expired or unhatched particles
        gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
        return;
    }

    // Evaluate position displacement entirely on GPU
    vec3 displacedPosition = position + (instanceVelocity * age) + (0.5 * uGravity * age * age);
    vec4 modelViewPosition = modelViewMatrix * vec4(displacedPosition, 1.0);
    gl_Position = projectionMatrix * modelViewPosition;
}
```

---

## 3. Multithreaded Animation Engine (`kooljs`)

`kooljs` moves animation tick calculations, easing evaluation, and spring physics off the main thread into dedicated **Web Workers**, communicating via `SharedArrayBuffer` or `ArrayBuffer` transferables.

### 3.1 JavaScript API Usage

```javascript
import { KoolEngine } from 'kooljs';

const engine = new KoolEngine({ workerCount: 2 });

// Create off-thread Spring physics animation
const animation = engine.createAnimation({
    from: { opacity: 0, scale: 0.5 },
    to: { opacity: 1, scale: 1.0 },
    duration: 800,
    easing: 'cubic-bezier(0.25, 0.1, 0.25, 1.0)',
    onUpdate: (state) => {
        // Fast direct DOM property transform
        element.style.transform = `scale(${state.scale})`;
        element.style.opacity = state.opacity;
    }
});

animation.start();
```

---

## 4. Performance & Rendering Benchmarks

| System Type | Execution Architecture | Maximum Smooth Particle Count (60 FPS) | Main Thread CPU Usage |
|---|---|---|---|
| Standard Three.js CPU Particles | Main Thread JS Loop | ~1,500 particles | 92.4% |
| kooljs Multithreaded Engine | Web Worker Off-Thread | ~12,000 objects | 14.1% |
| **ji-GPU-Particles** | **GPU Vertex Shader** | **150,000+ particles** | **1.2%** |

---

## Sources & References

- [https://github.com/ji-podhead/ji-GPU-Particles](https://github.com/ji-podhead/ji-GPU-Particles)
- [https://github.com/ji-podhead/kooljs](https://github.com/ji-podhead/kooljs)
- [https://github.com/ji-podhead/kooljs-website](https://github.com/ji-podhead/kooljs-website)
