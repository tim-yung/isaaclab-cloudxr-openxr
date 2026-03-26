# Isaac Lab + Isaac Sim 6 (source) + VR / OpenXR: install and patch manual

This document is a **repeatable checklist** for a workstation where Isaac Lab is paired with a **self-built Isaac Sim 6** binary, **OpenXR / CloudXR** teleop, and **air-gapped Kit extension registries**. Use it when onboarding a new machine or when an agent needs to know **exactly which files were changed** and **why**.

Paths below use **placeholders**. On this project they were:

| Role | Example path |
|------|----------------|
| Isaac Lab clone | `/home/ubuntu/IsaacLab` |
| Sim 6 build (release) | `/home/ubuntu/IsaacSim_v6/_build/linux-x86_64/release` |
| Sim 5 install (optional, separate) | your existing 5.x install (unchanged) |
| Local Kit registry mirror | `/home/ubuntu/omniverse-airgap/kit-extensions-registry-unpacked` |
| CloudXR / Isaac Teleop repo | `/home/ubuntu/Desktop/CloudXR` |

---

## 1. Why Sim 6 and two installs

- **Isaac Lab versions aligned with Sim 6** expect that runtime. **Sim 6** has been distributed as an **early / source-build** style release in many setups; a normal “download installer” may not match what Lab expects.
- **Backward compatibility:** keep **Isaac Sim 5.x** in its own directory for older projects. Install **Sim 6** separately (e.g. source build → `.../release`).
- **Isaac Lab** should point at **only one** Sim at a time via `_isaac_sim` (see below). Switching projects means switching the symlink or env, not mixing two Sim roots in one process.

---

## 2. Point Isaac Lab at Sim 6

From the Isaac Lab repo root:

```bash
cd /path/to/IsaacLab
ln -sfn /path/to/IsaacSim_v6/_build/linux-x86_64/release _isaac_sim
```

Verify:

```bash
readlink -f _isaac_sim
head -1 _isaac_sim/VERSION   # should reflect Sim 6
```

---

## 3. Python environment: `uv` and the “source two setup scripts” trick

Official flows often emphasize Conda or `isaaclab.sh -i`. Here **`uv`** was used for the Lab venv.

After creating the venv (per Isaac Lab docs), the recurring issue was: **Kit / `isaacsim` imports fail or libraries are missing** unless the **same environment variables** Sim’s own shell helpers set are applied.

**Sim release layout** contains at least:

- `setup_python_env.sh` — extends **`PYTHONPATH`** and **`LD_LIBRARY_PATH`** for Kit, bundled Python, and prebundled pip archives.
- `setup_conda_env.sh` — sets **`CARB_APP_PATH`**, **`ISAAC_PATH`**, **`EXP_PATH`**, etc.

**Practice that worked (even with `uv`):** before running `./isaaclab.sh` or `python` entrypoints, **source both** from the **same** `_isaac_sim` release directory:

```bash
source /path/to/IsaacSim_v6/_build/linux-x86_64/release/setup_python_env.sh
source /path/to/IsaacSim_v6/_build/linux-x86_64/release/setup_conda_env.sh
```

**Optional persistence:** append the same two `source` lines to your venv’s `bin/activate`, or to a small wrapper script you always use to launch teleop.

`isaaclab.sh`’s **uv** setup path already appends **`setup_conda_env.sh`** into the venv activate snippet; if anything still mis-resolves native libs or Kit Python, **`setup_python_env.sh`** is the usual missing piece.

---

## 4. “Windows still say 5.1” — expected

Several **Kit experience** files under Isaac Lab still declare metadata like `app.version = "5.1.0"` (e.g. `apps/isaaclab.python.xr.openxr.kit`). That string is **UI / packaging metadata**, not proof of which Sim binary is loaded. Trust **`_isaac_sim/VERSION`** and the actual **`release`** tree you symlinked.

---

## 5. Install Isaac Lab dependencies

From the repo (with venv active and env vars from §3):

```bash
cd /path/to/IsaacLab
./isaaclab.sh -i
```

Follow the current upstream README for CUDA / driver prerequisites.

---

## 6. Franka + hand tracking: current launch command

Official docs drift quickly; the **entry script** is:

`scripts/environments/teleoperation/teleop_se3_agent.py`

Passing **`--teleop_device handtracking`** makes `AppLauncher` set **`xr=True`**, which selects the OpenXR experience **`apps/isaaclab.python.xr.openxr.kit`** (non-headless). You do **not** need to pass `--experience` manually unless you customize it.

**Recommended task for CloudXR / Quest** (relative IK is far more stable than absolute IK in VR):

```bash
cd /path/to/IsaacLab
source /path/to/IsaacSim_v6/_build/linux-x86_64/release/setup_python_env.sh
source /path/to/IsaacSim_v6/_build/linux-x86_64/release/setup_conda_env.sh
# activate your uv/venv here

./isaaclab.sh -p scripts/environments/teleoperation/teleop_se3_agent.py \
  --task Isaac-Stack-Cube-Franka-IK-Rel-v0 \
  --teleop_device handtracking \
  --device cuda
```

For absolute IK (more finicky in VR):

`Isaac-Stack-Cube-Franka-IK-Abs-v0`

---

## 7. Omniverse / Kit registry failures → NGC air-gap mirror

### Symptom

Kit tries to fetch an **XR-related extension** from a **remote** `omni.kit.registry.nucleus` registry and fails (offline server, firewall, or missing public registry access).

### Fix (high level)

1. Create / use an **[NVIDIA NGC](https://catalog.ngc.nvidia.com/)** account.
2. Create an **API key** (used by the NGC CLI).
3. Install **[NGC CLI](https://org.ngc.nvidia.com/setup/installers/cli)** and run `ngc config set`.
4. Download the Kit extensions registry resource from NGC.
5. Unpack the archive somewhere permanent, e.g.  
   `/path/to/omniverse-airgap/kit-extensions-registry-unpacked`  
   You should see a layout that includes a **`v2`** directory (registry layout version).

Re-download when NVIDIA updates the bundle if extension versions no longer match your Sim build.

### 7.1 Pinned air-gap artifact used in this setup

The following resource/version is what this workstation used:

- NGC resource: `nvidia/omniverse/kit-extensions-registry`
- Version: `110.0.0`
- Download command:

```bash
ngc registry resource download-version "nvidia/omniverse/kit-extensions-registry:110.0.0"
```

If a checksum is not available from NGC for this artifact, keep reproducibility by pinning:

- the exact resource string above,
- the exact destination path used in your `.kit` registry override,
- and a post-unpack directory sanity check (below).

### 7.2 Post-unpack sanity check (no checksum required)

After unpacking, verify:

```bash
ls -la /path/to/omniverse-airgap/kit-extensions-registry-unpacked
ls -la /path/to/omniverse-airgap/kit-extensions-registry-unpacked/v2
```

At minimum, ensure the unpacked registry is non-empty and contains a `v2` directory.

---

## 8. Map the local registry into Isaac Lab (reproducible)

**File to edit:**  
`/path/to/IsaacLab/apps/isaaclab.python.xr.openxr.kit`

**Goal:** append a **local** registry **without** removing Isaac Lab’s default registries. In TOML, **`++`** on an array performs append merge in Kit configs.

Add (or merge) a block like:

```toml
[settings.exts."omni.kit.registry.nucleus".registries]
++ = [
    { name = "kit/airgap-local", url = "/path/to/omniverse-airgap/kit-extensions-registry-unpacked" },
]
```

Use a **`file://`** URL only if required by your Kit version; a plain absolute path worked in this setup.

**Important:** every machine must use **its own** absolute path, or set a symlink (e.g. `/opt/omniverse-airgap/...`) and point `url` there.

### 8.1 Recommended path stability across machines

To reduce per-machine edits, prefer a stable symlink:

- Real unpack path: machine-specific
- Stable path used by `.kit`: `/opt/omniverse-airgap/kit-extensions-registry-unpacked`

Then keep the `.kit` registry URL fixed to the stable path.

---

## 9. XR experience dependencies vs Sim 6 + air-gap contents

**File:**  
`/path/to/IsaacLab/apps/isaaclab.python.xr.openxr.kit`

Changes that mattered:

| Topic | Action |
|--------|--------|
| **`omni.kit.xr.profile.ar`** | **Remove** from `[dependencies]` if present. It is **not** bundled with Sim 6 the same way and may be **absent** from public air-gap mirrors → startup failure. |
| **Core XR** | Keep e.g. **`omni.kit.xr.core`**, **`omni.kit.xr.system.openxr`**. |
| **Start / Stop VR UI** | Add **`omni.kit.xr.ui.window.profile`** and set **`xr.ui.enabled = true`** under `[settings]`. Without this, Kit may **hide** the OpenXR runtime UI; **CloudXR** on the host still needs a sane OpenXR session flow. |
| **Hand tracking** | Enable the OpenXR hand-tracking related component toggles already present in the Sim template (e.g. `xr.openxr.components."omni.kit.xr.openxr.ext.hand_tracking".enabled`, `isaacsim.xr.openxr.hand_tracking`). |

Compare against the **upstream** `isaacsim.exp.xr.openxr.kit` inside your Sim tree when upgrading.

---

## 10. URDF importer pin vs Sim 6 (undefined symbols / wrong version)

### Symptom

Errors mentioning **`UsdPhysicsTokens`**, wrong URDF extension API, or mixed extension caches.

### Kit pin

**File:**  
`/path/to/IsaacLab/apps/isaaclab.python.kit`

- Set **`isaacsim.asset.importer.urdf`** to **`{}`** (no `exact = true` pin on **2.4.31**) so Sim **6.x** can load its shipped **3.x** importer.

### Converter logic

**File:**  
`/path/to/IsaacLab/source/isaaclab/isaaclab/sim/converters/urdf_converter.py`

- **`get_isaacsim_urdf_importer_extension_path()`** must resolve **`isaacsim.asset.importer.urdf-2.4.31`** only on **5.1 ≤ Sim < 6**, and plain **`isaacsim.asset.importer.urdf`** on **Sim 6+**.
- **`__init__`** of `UrdfConverter` enables **2.4.31** only in that same **5.1–5.x** band.

### Tests

Update any tests that assumed a fixed extension id to use **`get_isaacsim_urdf_importer_extension_path()`** (e.g. `test_urdf_converter.py`, `test_spawn_from_files.py`).

### User extension cache

If you previously ran another Sim version on the same login, delete stale URDF importer drops under:

`~/.local/share/ov/data/exts/v2/`

(remove folders named like `isaacsim.asset.importer.urdf-*` that do **not** match the current Sim), then retry.

---

## 11. NumPy vs optional humanoid retargeters (Franka teleop)

### Symptom

Importing **`isaaclab.devices.openxr.retargeters`** pulls **humanoid** modules that depend on **pinocchio** / **dex_retargeting** built against **NumPy 1.x**, while the stack uses **NumPy 2.x** → import or ABI errors.

### Fix

**File:**  
`/path/to/IsaacLab/source/isaaclab/isaaclab/devices/openxr/retargeters/__init__.py`

- Export humanoid retargeter classes via **`__getattr__` lazy imports** (or equivalent) so **Franka** configs that only need **`Se3*Retargeter`** / **`Gripper*`** never import humanoid stacks at import time.

Franka stack teleop does not need `--enable_pinocchio` unless you opt into tasks that require it.

---

## 12. CloudXR server configuration (arm control / hands)

Isaac Lab uses **OpenXR** on the **host**. The **Isaac Teleop** repo runs a **CloudXR** server that bridges the **Quest** browser client to that host.

**Env file:** see repo **`custom_cloudxr.env`**.

Critical variable for **hand tracking → `/user/hand/*`**:

```bash
NV_CXR_ENABLE_PUSH_DEVICES=0
```

Without this, hands may animate while the **arm** does not follow, because input takes a different path.

NAT / EC2 fixes: **`NV_CXR_STREAMSDK_ENABLE_ICE=0`**, fixed **`NV_CXR_MEDIA_PORT`**, client **Media Address / Port**, and security group — see **`EC2_SETUP_NOTES.md`**.

After any change to CloudXR env vars, **restart** the CloudXR server.

---

## 13. Quick “what we changed” file list

| Area | Path under `IsaacLab` (unless noted) |
|------|--------------------------------------|
| OpenXR experience + local registry + XR UI | `apps/isaaclab.python.xr.openxr.kit` |
| URDF importer pin | `apps/isaaclab.python.kit` |
| URDF Sim 5 vs 6 behavior | `source/isaaclab/isaaclab/sim/converters/urdf_converter.py` |
| Lazy humanoid retargeters | `source/isaaclab/isaaclab/devices/openxr/retargeters/__init__.py` |
| Related tests | `source/isaaclab/isaaclab/**/test_urdf_converter.py`, `test_spawn_from_files.py` (paths may vary by version) |
| CloudXR | `/path/to/CloudXR/custom_cloudxr.env` + server restart |

---

## 14. References

- [Omniverse air-gap / Kit local registry](https://docs.omniverse.nvidia.com/air-gap/latest/build.html)
- [Isaac Lab](https://github.com/isaac-sim/IsaacLab) — follow current install docs for your branch
- [Isaac Teleop / CloudXR quick start](https://nvidia.github.io/IsaacTeleop/main/getting_started/quick_start.html)
- Same repo: **`EC2_SETUP_NOTES.md`**, **`RUN_CLOUDXR_AND_FRANKA_TELEOP.md`**, **`CLOUDXR_DEBUG.md`**
