# Nano Cortex Editor for macOS

This v1.19.1+mac.7 snapshot contains the installed editor HTML, macOS launcher source, effect pictures, and font license. The active page is [Index V3.0.html](../Index%20V3.0.html). The legacy root index remains available separately.

Build on macOS with `./mac-app/build.sh` (AppleScript compiler and code signing tools required). Install the resulting app from `build/`, or pass a different, unused `.app` path to the build script. At runtime install Google Chrome in Applications and have Python 3 available. The app starts its own local HTTP server and opens Chrome with a dedicated profile. Quit the editor from its Dock icon to close its editor window. Chrome can reuse permission for an already authorized Nano. Disconnect pauses retries, and Connect reconnects to the remembered device.

NanOS 2.3.0 adds Poly Octaver, Wham and Chief OC2 in Pre FX 1, and Blossom (ST) and Shimmer in Post FX 3. The Tempo button appears enabled after the connected device reports compatible firmware. Changes in the metronome dialog are sent when you press Apply.

Model IDs, control metadata and TempoScreen framing are adapted from [DrD85/nano-cortex-editor](https://github.com/DrD85/nano-cortex-editor), distributed under MIT. The installed app snapshot and this source backup do not contain Chrome profile data or Nano Cortex presets. Use Cortex Cloud for device preset backups.
