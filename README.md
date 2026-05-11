# Propeller Optimization Program (POP) for the Web

Version 1.1, May 2026

## Purpose

The Propeller Optimization Program (POP) for the Web is a preliminary propeller design and evaluation tool based on the Wageningen B-Series propeller curves.

POP estimates a screw propeller operating point from vessel speed, required thrust, wake fraction, immersion, water properties, blade count, pitch-diameter ratio, expanded area ratio, and diameter. It reports the usual open-water and propeller design quantities used during early-stage powering and propulsor selection.

This version is intended for preliminary naval architecture studies, course work, preservation of the original POP workflow, and comparison of propeller alternatives. It is not a substitute for model-test correlation, detailed cavitation tunnel work, class approval, or final propeller drawing development.

## Method

POP uses the Wageningen B-Series open-water characteristics to estimate:

- Advance coefficient, `J`
- Thrust coefficient, `KT`
- Torque coefficient, `KQ`
- Open-water efficiency, `Eta0`
- Propeller diameter, `D`
- Propeller pitch, `P`
- Pitch-diameter ratio, `P/D`
- Expanded area ratio, `Ae/Ao`
- Revolutions per minute, `RPM`
- Reynolds number
- Cavitation number
- Burrill loading check

For fixed-pitch propellers, the reported efficiency follows the B-Series open-water calculation. For controllable-pitch propellers, POP applies the legacy POP reduction of 2 percent to `Eta0`.

## Design Modes

### Evaluation

Use Evaluation when the main propeller particulars are already known. Enter blade count, `Ae/Ao`, `P/D`, and propeller diameter. POP solves the operating point needed to satisfy the required thrust at the stated ship speed and wake fraction.

Evaluation is useful when checking a candidate propeller against a design condition, comparing a known wheel with a target thrust, or reproducing a legacy POP case.

### Optimization

Use Optimization when the diameter is allowed to vary within a selected range. POP searches for a feasible B-Series propeller that satisfies thrust and cavitation screening while improving open-water efficiency.

Optimization is useful during early powering studies when diameter limits are known from aperture, draft, hull clearance, or machinery arrangement, but final `P/D` and `Ae/Ao` have not yet been selected.

In Optimization mode, POP automatically sweeps blade count `Z` from 3 through 7. The result panel shows the global best design plus a per-`Z` comparison table so early-stage blade-count selection becomes an output of the calculation rather than a separate user decision.

## Input Guidance

Use consistent design-condition values:

- Required thrust should be the propeller thrust demand at the selected condition.
- Ship speed should be the vessel speed through the water.
- Wake fraction should represent the effective inflow reduction at the propeller disk.
- Shaft depth should represent propeller shaft immersion below the free surface.
- Density and kinematic viscosity should match the selected water condition.
- Diameter limits should reflect hull aperture, tip clearance, draft, and arrangement constraints.

For salt water at 15 C, the default density and viscosity are suitable for many preliminary studies. Fresh water and custom water properties are also available.

## Reading the Results

The results table gives the selected propeller particulars and operating point. The open-water curve plot shows the `KT`, `10KQ`, and `Eta0` curves against advance coefficient `J`, with the current operating point marked on the curve.

Use the plot to judge whether the operating point sits in a reasonable part of the B-Series curve. Use the table to compare alternatives by diameter, pitch, expanded area ratio, rpm, efficiency, cavitation number, and Reynolds number.

Below the result table, POP renders:

- A "Notes" panel that flags tight cavitation margins, low efficiency, extreme RPM, designs pinned at the search boundaries, and the empirical controllable-pitch reduction.
- A per-`Z` table in Optimization mode that compares the optimum at each blade count, with the global best row highlighted.
- An "Out of date" badge if you edit any input after a run; it clears when you re-run.

If the optimizer cannot find a feasible design, POP returns a `no_feasible_design` error with structured hints (raise the cavitation limit, widen the diameter range, increase shaft submergence) and the closest infeasible candidate's numbers so you can decide what to change.

The JSON and CSV exports preserve the numerical result. The Print button opens the browser print dialog; choose "Save as PDF" there to produce a Letter-size report with 1 inch margins.

For the calibration sources behind these numbers, open the "Methodology" panel from the top bar.

## Legacy POP Files

This version can import known legacy `.POP` files from the original Propeller Optimization Program format. Imported cases are converted into the current input fields so they can be evaluated or optimized in the web version.

The modern application does not require the original POP installation to calculate results.

## Deployment With Docker Compose

This section uses deployment terms. It is included for users who want to run POP on their own server.

### What You Need

- A server or computer with Docker installed
- Docker Compose installed
- A copy of this repository from GitHub
- A port number you want people to use in their browser

The server you choose determines the IP address or domain name. POP does not require a fixed hostname, fixed IP address, or fixed public port.

The container runs as an unprivileged user (`pop`, uid 10001), uses a pinned `python:3.12.8-slim` base image, and installs only `numpy` for runtime. NGINX rate-limits `/api/run` and strips its version header.

### Start POP On The Default Port

From the repository folder, go to the application folder:

```sh
cd POP-NEW/app
```

Start the containers:

```sh
docker-compose up --build
```

By default, POP is available on port `8080`.

Open:

```text
http://SERVER_IP:8080/
```

Replace `SERVER_IP` with the IP address or domain name of the server.

### Start POP On A Different Port

Choose a port number, for example `9090`, and start POP like this:

```sh
POP_HOST_PORT=9090 docker-compose up --build
```

Open:

```text
http://SERVER_IP:9090/
```

For a permanent local setting, copy the example environment file and edit the port number:

```sh
cp .env.example .env
```

Then edit `.env` so it contains the port you want:

```sh
POP_HOST_PORT=9090
```

After that, start POP normally:

```sh
docker-compose up --build
```

### Check That POP Is Running

In another terminal, run:

```sh
docker-compose ps
```

You should see the POP backend and NGINX containers running. You can also check:

```text
http://SERVER_IP:PORT/health
```

It should return:

```json
{"status": "ok"}
```

### HTTPS

POP runs HTTP inside Docker. If you want HTTPS, add it outside POP using the method you prefer, such as host NGINX, Caddy, Traefik, NGINX Proxy Manager, Let's Encrypt, or OpenSSL-managed certificates.

A common arrangement is:

```text
Internet browser -> HTTPS proxy -> POP HTTP port
```

For that arrangement, you may bind POP only to the server itself:

```sh
POP_HOST_PORT=127.0.0.1:8080 docker-compose up --build
```

Then configure your HTTPS proxy to forward to:

```text
http://127.0.0.1:8080
```

Do not commit private keys or certificate files. Local certificate material can be kept outside the repository, or under `POP-NEW/app/certs/`, which is ignored.

## Current Scope

POP 1.1 covers the B-Series preliminary design workflow recovered from the legacy POP materials, plus the engineering and product improvements described in `POP-NEW/CLAUDE-REVIEW-PLAN.md`. Highlights since 1.0:

- Reynolds-section chord factor switched to Carlton's published 0.75R value (no longer fitted to one case).
- Burrill back-cavitation chart digitised from Carlton (2012) Figure 9.21, replacing the previous single-point linear calibration.
- Optimizer sweeps blade count `Z = 3..7` and reports a per-`Z` comparison table.
- Optimization is numpy-vectorised; a full blade-sweep run typically completes in about 2 seconds.
- Result panel surfaces advisory notes, cavitation margin warnings, no-feasible-design hints, and a stale-result badge.
- Client-side validation mirrors the backend validator with inline field errors.
- Container runs as a non-root user with a pinned Python base; NGINX adds timeouts, rate limiting on `/api/run`, IPv6, and stripped server tokens.
- CFB legacy-import parser hardened against malformed input.
- Continuous integration runs the test suite and a container build check on every push.
- Methodology disclosure panel in the UI summarises calibration sources.

Additional validation cases should be added if more legacy POP files, printed output sheets, or independent B-Series examples become available.
