# Changelog

## 0.2.0

- Add persistent wash presets: Linen, Reds, Greys, Whites and Delicate.
- Add a Preset selector.
- Add a Save to preset button.
- Saving captures the selected hOn program and every parameter exposed by that program.
- Selecting a configured preset restores its program and saved parameter values.
- Presets persist across Home Assistant restarts.

## 0.1.3

- Put the three most recently started programs at the top of the program list.
- Recent programs are ordered most-recent-first and persist across Home Assistant restarts.
- The remainder of the program list stays alphabetical.

## 0.1.2

- Sort program names alphabetically by their display label.
- Remove a leading `iot_` prefix from displayed program names while preserving the real hOn program ID.

## 0.1.1

- Display program IDs as human-friendly title/Pascal-style labels without underscores.
- Sort spin-speed options numerically.

## 0.1.0

- Initial release.
- Dynamic program selector using the existing hOn program catalogue.
- Program-dependent temperature, spin-speed and soil-level selectors.
- Start selected program button.
- Designed as a companion to gvigroux/hon 0.8.4 without replacing or modifying it.
