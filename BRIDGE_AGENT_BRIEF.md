# Agent brief: flash WT32-ETH01 as WiFi bridge for an Ethernet receipt printer

## Goal
Turn Shelton's Ethernet-only ESC/POS receipt printer into a WiFi-reachable one using a
**WT32-ETH01** board (ESP32-WROOM + LAN8720A PHY) running Espressif's official
**sta2eth** example (ESP-IDF, `examples/network/sta2eth`). Printer must end up reachable
on the LAN at TCP port 9100 so the `hardcopy` service (repo this brief lives in) can
print to it via `printer.network.host`.

Done means: `printf 'bridge test\n\n\n\n' | nc <bridge-ip> 9100` produces paper.

## Context
- Machine: macOS. This folder (`~/Desktop/Projects/GitHub Notification Bot`) is the
  hardcopy repo — see ARCHITECTURE.md / PLAN.md.
- Prior art considered and rejected: owenthewizard/esp32-wifi-bridge (Rust, stale since
  2024-05); NAT routers (esp32_ethernet_router, esp-iot-bridge) — printer behind NAT
  breaks direct 9100 access.
- sta2eth does L2 forwarding with MAC cloning: the printer's own MAC appears on the
  WiFi network. Its DHCP lease will look like the *printer*, not an ESP32.

## Constraints
- Work in `bridge/` inside this folder. Make it a standalone git repo; add `bridge/` to
  the hardcopy repo's `.gitignore` (don't nest-track it).
- Pin ESP-IDF to the latest **stable v5.x release tag** (verify current; v5.3+ known to
  contain sta2eth). Record the exact tag in `bridge/NOTES.md`.
- Ask the user before anything requiring hands (wiring, plugging cables, pressing
  buttons). They are comfortable with hardware.

## Steps

### 1. Toolchain
Check for an existing ESP-IDF install (`idf.py --version`, `~/esp/esp-idf`, `~/.espressif`).
The user has done ESP32-C6 projects — an install may exist. If none:
```bash
mkdir -p ~/esp && cd ~/esp
git clone -b <PINNED_TAG> --recursive --depth 1 --shallow-submodules https://github.com/espressif/esp-idf.git
cd esp-idf && ./install.sh esp32
. ./export.sh
```

### 2. Project
Copy the example out rather than building in-tree:
```bash
cp -r $IDF_PATH/examples/network/sta2eth "<this folder>/bridge/sta2eth-wt32"
cd "<this folder>/bridge/sta2eth-wt32" && git init
idf.py set-target esp32
```

### 3. Configure for WT32-ETH01 (the critical part)
Board facts (verify against the example's Kconfig via `idf.py menuconfig` — do NOT
trust option names blindly, they vary across IDF versions):

| Setting | Value |
|---|---|
| PHY | LAN8720A |
| PHY address | 1 |
| MDC / MDIO | GPIO23 / GPIO18 |
| RMII clock | **external 50 MHz oscillator → GPIO0, clock INPUT mode** |
| PHY reset GPIO | none (−1) |
| Oscillator/PHY enable | **GPIO16 — must be driven HIGH before eth init** |

Config paths in menuconfig (names approximate — verify):
- Example Configuration → wired interface = Ethernet; WiFi configuration = MANUAL
  (web page) unless creds can be baked in.
- Ethernet init (managed component `ethernet_init`, pulled via `main/idf_component.yml`):
  internal EMAC + LAN87xx, pins/addr per table.
- Component config → Ethernet → RMII clock: input on GPIO0.

**Known gotcha:** if the ethernet_init component has no "PHY power GPIO" option, GPIO16
never goes high, the oscillator stays off, and eth init fails with PHY timeout. Fix in
`main/` before eth init:
```c
gpio_set_direction(GPIO_NUM_16, GPIO_MODE_OUTPUT);
gpio_set_level(GPIO_NUM_16, 1);
vTaskDelay(pdMS_TO_TICKS(10));
```
(ethernet_init *may* expose this as a power/reset pin option = 16 — prefer that if present.)

Persist all non-default choices in `sdkconfig.defaults` so the repo is reproducible.

### 4. Build
```bash
idf.py build
```
Must complete before touching hardware. Commit the working tree now.

### 5. Wiring + flash (user does the physical part)
WT32-ETH01 has **no USB port**. Instruct the user:
- 3.3 V-logic USB-UART adapter: adapter TX → board RX0, adapter RX → board TX0, GND–GND.
- Power: 5 V pin from adapter's 5 V (board has an onboard regulator) — or 3.3 V pin,
  never both.
- Enter bootloader: tie **IO0 → GND**, then reset (pull EN low momentarily or power-cycle).
  GPIO0 doubles as the RMII clock input; this is fine — the oscillator is disabled while
  GPIO16 is low at reset.
```bash
idf.py -p /dev/cu.usbserial-* flash monitor
```
Remove the IO0–GND link and reset after flashing.

### 6. Provision WiFi
With MANUAL config mode: plug a laptop into the board's Ethernet jack, browse to
`http://wifi.settings`, enter home WiFi SSID/password (2.4 GHz only — ESP32 has no 5 GHz).
Then unplug laptop, plug in the **printer**, power-cycle the board.

### 7. Verify end-to-end
1. `idf.py monitor`: WiFi STA connected, eth link up.
2. Find the bridge on the LAN — look for the **printer's MAC** in the router's DHCP
   leases (MAC cloning; there is no "ESP32" device).
3. `nc <ip> 9100` + send text and feed bytes; confirm paper output. A cut command for
   most Epson-compatibles: `printf '\x1dVA\x10'`.
4. Update `config.yaml` in the hardcopy repo: `printer.type: network`,
   `printer.network.host: <ip>` — and remind the user to give the printer a DHCP
   reservation so the IP is stable.

### 8. Record + commit
`bridge/NOTES.md`: IDF tag, exact sdkconfig deltas, serial adapter used, bridge IP,
anything that deviated from this brief. Commit `bridge/sta2eth-wt32` (own repo);
commit the `.gitignore` + `config.yaml` touch in the hardcopy repo separately.

## Fallbacks
- sta2eth flaky with this printer (some PHYs dislike promiscuous forwarding): fall back
  to a plain **TCP proxy** firmware — ESP32 as WiFi STA, static IP 192.168.4.x link to
  printer, listen :9100, pipe bytes. ~150 lines; Rust (esp-idf-svc) or C. Loses
  discovery, keeps everything hardcopy needs.
- No time for firmware at all: any travel router / WiFi client-bridge (e.g. GL.iNet)
  in front of the printer solves this with zero code.

## Out of scope
Do not modify hardcopy's source (only `config.yaml` + `.gitignore`), do not push any
repo to GitHub, do not store WiFi credentials in git.
