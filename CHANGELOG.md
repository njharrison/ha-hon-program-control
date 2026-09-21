# Changelog

## 0.3.2

- Fix Preset Name starting with an invalid empty value when its minimum length was 1.
- Explicitly expose Preset Name as a normal editable text control.

## 0.3.1

- Replace the three individual Extra Rinse switches with one Extra Rinses control.
- Extra Rinses offers 0 through the number of rinse stages supported by the selected program.
- The combined control maps back to hOn's underlying extraRinse1, extraRinse2 and extraRinse3 parameters, preserving preset compatibility.

## 0.3.0

- Make presets fully dynamic: type any name and save the current wash configuration.
- Add Delete preset.
- Preserve any presets already saved by 0.2.0.
- Add controls for Prewash, Hygiene, Anti-crease, Good Night, Aqua Plus and three Extra Rinse flags.
- Add Delay Time as a numeric control.
- Program-specific controls become unavailable when the selected program does not support them.
- Presets continue to capture all hOn parameters, including controls not shown in the UI.

## 0.2.0

- Add persistent wash presets: Linen, Reds, Greys, Whites and Delicate.
- Add a Preset selector and Save to preset button.
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
