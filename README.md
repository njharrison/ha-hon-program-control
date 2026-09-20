# hOn Program Control

A small Home Assistant companion integration for **gvigroux/hon**, initially
targeted at hOn **0.8.4**.

It does **not** replace hOn, log in to the hOn cloud, or modify the existing
`custom_components/hon` integration. It reuses the live hOn device and
`startProgram` command already loaded by Home Assistant.

## What v0.1 exposes

For a compatible washing machine:

- Program selector populated from the washer's actual `get_programs()` catalogue
- Temperature selector, dynamically populated for the selected program
- Spin-speed selector, dynamically populated for the selected program
- Soil/dirty-level selector when the selected program supports it
- Start selected program button

Changing the program immediately refreshes the valid parameter choices.

## Requirements

- Home Assistant
- `gvigroux/hon` installed and working
- Tested against hOn 0.8.4
- Washing machine with a `startProgram` command

## Installation with HACS

1. HACS → Integrations → three-dot menu → **Custom repositories**.
2. Add this repository:
   `https://github.com/njharrison/ha-hon-program-control`
3. Category: **Integration**.
4. Install **hOn Program Control**.
5. Restart Home Assistant.
6. Settings → Devices & services → **Add Integration** → search for
   **hOn Program Control**.
7. Select the washing machine.

The new controls are attached to the existing hOn washing-machine device.

## Safety / scope

This is an experimental companion integration. The **Start selected program**
button sends a real start command to the appliance. Verify the selected
program, temperature and spin speed before pressing it.

v0.1 deliberately exposes only a small set of common controls. More
program-specific parameters (prewash, hygiene, extra rinses, anti-crease,
Acqua Plus, etc.) can be added after the core dynamic-selection path has been
tested.

## Why this exists

hOn 0.8.4 already downloads a structured catalogue of programs and their valid
parameters. Its **Get programs details** button renders that catalogue as
persistent notifications. This integration exposes the same in-memory data as
normal Home Assistant entities instead.
