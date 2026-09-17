---
name: install-silence-cutter
description: Installs the Silence Cutter plugin for Adobe Premiere Pro — automatic silence detection with waveform preview, speaker pause detection, and smart undo.
---

# Silence Cutter — Installer for Adobe Premiere Pro

You are installing the **Silence Cutter** CEP plugin for Adobe Premiere Pro.

## What the plugin does
- Detects silent segments in video using ffmpeg
- Shows a waveform with red (cut) and yellow (speaker pause) regions
- Supports auto-cut and mark-only modes
- Smart undo restores the sequence with one click

## Your tasks

### 1. Detect platform and set paths
- **Windows**: extension dir = `%APPDATA%\Adobe\CEP\extensions\SilenceCutter\`
- **Mac**: extension dir = `~/Library/Application Support/Adobe/CEP/extensions/SilenceCutter/`

Detect which platform the user is on and use the correct path.

### 2. Create directory structure
Create these directories:
```
SilenceCutter/
  CSXS/
  jsx/
  js/
  css/
```

### 3. Write all plugin files exactly as shown below

---

#### FILE: `CSXS/manifest.xml`
```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<ExtensionManifest Version="12.0"
  ExtensionBundleId="com.silencecutter.premiere"
  ExtensionBundleVersion="1.0.0"
  ExtensionBundleName="Silence Cutter">
  <ExtensionList>
    <Extension Id="com.silencecutter.premiere.panel" Version="1.0.0"/>
  </ExtensionList>
  <ExecutionEnvironment>
    <HostList>
      <Host Name="PPRO" Version="23.0"/>
      <Host Name="PPRO" Version="24.0"/>
      <Host Name="PPRO" Version="25.0"/>
      <Host Name="PPRO" Version="25.1"/>
      <Host Name="PPRO" Version="25.2"/>
      <Host Name="PPRO" Version="26.0"/>
    </HostList>
    <LocaleList>
      <Locale Code="All"/>
    </LocaleList>
    <RequiredRuntimeList>
      <RequiredRuntime Name="CSXS" Version="12.0"/>
    </RequiredRuntimeList>
  </ExecutionEnvironment>
  <DispatchInfoList>
    <Extension Id="com.silencecutter.premiere.panel">
      <DispatchInfo>
        <Resources>
          <MainPath>./index.html</MainPath>
          <CEFCommandLine>
            <Parameter>--enable-nodejs</Parameter>
            <Parameter>--mixed-context</Parameter>
          </CEFCommandLine>
        </Resources>
        <Lifecycle>
          <AutoVisible>true</AutoVisible>
        </Lifecycle>
        <UI>
          <Type>Panel</Type>
          <Menu>Silence Cutter</Menu>
          <Geometry>
            <Size>
              <Height>620</Height>
              <Width>320</Width>
            </Size>
            <MinSize>
              <Height>500</Height>
              <Width>280</Width>
            </MinSize>
          </Geometry>
        </UI>
      </DispatchInfo>
    </Extension>
  </DispatchInfoList>
</ExtensionManifest>
```

---

#### FILE: `index.html`
```html
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <title>Silence Cutter</title>
  <link rel="stylesheet" href="css/style.css" />
</head>
<body>
  <div class="container">
    <h1>✂️ Silence Cutter</h1>
    <p class="subtitle">חיתוך אוטומטי של קטעי שקט</p>

    <div class="section">
      <label>רמת שקט (dB)</label>
      <div class="row">
        <input type="range" id="noiseLevel" min="-60" max="-10" value="-35" step="1" />
        <span id="noiseLevelVal">-35 dB</span>
      </div>
    </div>

    <div class="section">
      <label>משך שקט מינימלי לחיתוך (שניות)</label>
      <div class="row">
        <input type="range" id="minDuration" min="0.1" max="5.0" value="0.5" step="0.1" />
        <span id="minDurationVal">0.5 שנ'</span>
      </div>
    </div>

    <div class="section">
      <label>ריפוד לפני/אחרי חיתוך (שניות)</label>
      <div class="row">
        <input type="range" id="padding" min="0" max="1.0" value="0.1" step="0.05" />
        <span id="paddingVal">0.1 שנ'</span>
      </div>
    </div>

    <div class="section">
      <label>הפסקת דובר — שמור שקט קצר מ- (שניות)</label>
      <div class="row">
        <input type="range" id="speakerPause" min="0" max="2.0" value="0.3" step="0.05" />
        <span id="speakerPauseVal">0.3 שנ'</span>
      </div>
      <p class="hint">שקט קצר מזה ייצבע בצהוב ולא ייחתך.</p>
    </div>

    <div class="section">
      <label>מצב פעולה</label>
      <div class="mode-toggle">
        <label class="mode-option">
          <input type="radio" name="mode" id="modeAuto" value="auto" checked />
          <span class="mode-label">
            <strong>✂️ חתוך אוטומטית</strong>
            <small>מוחק את קטעי השקט ומקרב את הקליפים</small>
          </span>
        </label>
        <label class="mode-option">
          <input type="radio" name="mode" id="modeMarkOnly" value="mark" />
          <span class="mode-label">
            <strong>📍 סמן בלבד</strong>
            <small>עושה razor cuts — אתה מחליט מה למחוק</small>
          </span>
        </label>
      </div>
    </div>

    <button id="btnAnalyze" class="btn-primary">🔍 זהה קטעי שקט</button>

    <div id="waveformSection" class="section hidden">
      <label>תצוגת גלים</label>
      <div class="waveform-wrap">
        <img id="waveformImg" src="" alt="" />
        <canvas id="waveformCanvas"></canvas>
      </div>
      <div class="waveform-legend">
        <span class="leg-cut">■ יחתך</span>
        <span class="leg-pause">■ הפסקת דובר</span>
      </div>
    </div>

    <div id="preview" class="preview hidden">
      <p id="previewText"></p>
      <button id="btnCut" class="btn-danger">✂️ חתוך הכל</button>
      <button id="btnUndo" class="btn-undo hidden">↩️ בטל חיתוכים</button>
      <button id="btnCancel" class="btn-secondary">ביטול</button>
    </div>

    <div id="status" class="status hidden"></div>
    <div class="footer"><a href="#" id="ffmpegLink" style="display:none">הורד ffmpeg</a></div>
  </div>
  <script src="js/CSInterface.js"></script>
  <script src="js/main.js"></script>
</body>
</html>
```

---

#### FILE: `css/style.css`
```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system,"Segoe UI",Arial,sans-serif; background:#1e1e1e; color:#d4d4d4; font-size:13px; direction:rtl; }
.container { padding:14px; display:flex; flex-direction:column; gap:10px; }
h1 { font-size:17px; color:#fff; font-weight:600; }
.subtitle { font-size:11px; color:#888; margin-top:-6px; }
.section { background:#2a2a2a; border-radius:6px; padding:10px 12px; display:flex; flex-direction:column; gap:6px; }
.section label { font-size:12px; font-weight:600; color:#c0c0c0; }
.row { display:flex; align-items:center; gap:10px; }
input[type="range"] { flex:1; accent-color:#3b82f6; cursor:pointer; }
.row span { min-width:54px; font-size:12px; color:#3b82f6; font-weight:bold; text-align:left; }
.hint { font-size:10px; color:#666; line-height:1.4; }
button { border:none; border-radius:5px; padding:9px 14px; font-size:13px; font-weight:600; cursor:pointer; width:100%; transition:opacity 0.15s; }
button:disabled { opacity:0.5; cursor:not-allowed; }
button + button { margin-top:6px; }
.btn-primary { background:#3b82f6; color:#fff; }
.btn-primary:hover:not(:disabled) { background:#2563eb; }
.btn-danger { background:#ef4444; color:#fff; }
.btn-danger:hover:not(:disabled) { background:#dc2626; }
.btn-secondary { background:#374151; color:#d4d4d4; }
.btn-secondary:hover:not(:disabled) { background:#4b5563; }
.btn-secondary-action { background:#1e3a5f; color:#93c5fd; border:1px solid #3b82f6; }
.btn-secondary-action:hover:not(:disabled) { background:#1e4080; }
.btn-undo { background:#292524; color:#d4d4d4; border:1px solid #57534e; }
.btn-undo:hover:not(:disabled) { background:#44403c; }
.waveform-wrap { position:relative; width:100%; height:64px; border-radius:4px; overflow:hidden; background:#111; }
.waveform-wrap img { position:absolute; top:0; left:0; width:100%; height:100%; object-fit:fill; }
.waveform-wrap canvas { position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; }
.waveform-legend { display:flex; gap:12px; font-size:10px; margin-top:4px; }
.leg-cut { color:#f87171; }
.leg-pause { color:#fbbf24; }
.mode-toggle { display:flex; flex-direction:column; gap:6px; }
.mode-option { display:flex; align-items:flex-start; gap:8px; padding:8px 10px; border-radius:5px; cursor:pointer; border:1px solid transparent; transition:border-color 0.15s,background 0.15s; }
.mode-option:has(input:checked) { border-color:#3b82f6; background:#1e3a5f; }
.mode-option input[type="radio"] { margin-top:2px; accent-color:#3b82f6; flex-shrink:0; }
.mode-label { display:flex; flex-direction:column; gap:2px; }
.mode-label strong { font-size:12px; color:#e2e8f0; }
.mode-label small { font-size:10px; color:#888; }
.preview { background:#1a2a1a; border:1px solid #2d6a2d; border-radius:6px; padding:12px; display:flex; flex-direction:column; gap:6px; }
.preview p { font-size:12px; line-height:1.6; color:#d4d4d4; }
.status { padding:8px 12px; border-radius:5px; font-size:12px; line-height:1.4; }
.status.info { background:#1e3a5f; color:#93c5fd; }
.status.success { background:#14532d; color:#86efac; }
.status.error { background:#450a0a; color:#fca5a5; }
.hidden { display:none !important; }
.footer { text-align:center; font-size:10px; color:#555; padding-top:4px; }
.footer a { color:#3b82f6; text-decoration:none; }
```

---

#### FILE: `jsx/host.jsx`
Write the full contents of this file exactly as provided in the prompt context — it contains `saveSequenceState`, `restoreSequenceState`, `getSequenceInfo`, `applySilenceCuts`, `markSilences`, and all helper functions using the QE DOM approach with frame-based timecodes.

Key functions that MUST be present:
- `saveSequenceState()` — serializes all clips to JSON before cutting
- `restoreSequenceState(json)` — removes all clips and re-inserts from saved state
- `getSequenceInfo()` — returns mediaPath, clipOffset, clipSeqStart
- `applySilenceCuts(json)` — calls `app.enableQE()`, converts seconds→frames, razor+remove+shift
- `markSilences(json)` — razor only, no deletion
- `razorAllTracks(frames)` — uses `qe.project.getActiveSequence().getVideoTrackAt(t).razor(frames)`
- `isThereClipAtFrame(frames, t, type)` — checks via `clip.start.getFormatted(frameRate, 109)`
- `removeAllTracksInRange(start, end)` — uses `clip.remove(false, false)`
- `shiftTracksLeft(fromFrame, durFrames, secPerFrame)` — uses `clip.move(-amountSeconds)`

The full file content is already at:
`%APPDATA%\Adobe\CEP\extensions\SilenceCutter\jsx\host.jsx`

Copy it from there, or write it fresh based on the function signatures above.

---

#### FILE: `js/main.js`
Full Node.js/CEP panel logic. Key responsibilities:
- Find ffmpeg in common locations (`C:\ffmpeg\bin\ffmpeg.exe`, PATH, etc.)
- Call `getSequenceInfo()` via `csInterface.evalScript`
- Get media duration via `ffprobe`
- Generate waveform PNG via `ffmpeg showwavespic` filter
- Draw silence overlay on HTML5 Canvas (red = cut, yellow = speaker pause)
- Run `silencedetect` with configurable noise level and min duration
- Before auto-cut: call `saveSequenceState()` then `applySilenceCuts()`
- Show undo button after cut; call `restoreSequenceState()` on click

The full file is at:
`%APPDATA%\Adobe\CEP\extensions\SilenceCutter\js\main.js`

Copy it from there.

---

#### FILE: `js/CSInterface.js`
Copy from:
`%APPDATA%\Adobe\CEP\extensions\SilenceCutter\js\CSInterface.js`

This is the standard Adobe CSInterface library required by all CEP extensions.

---

### 4. Enable PlayerDebugMode (allows unsigned extensions)

**Windows** — run via PowerShell:
```powershell
New-ItemProperty -Path 'HKCU:\Software\Adobe\CSXS.11' -Name 'PlayerDebugMode' -Value '1' -PropertyType String -Force
New-ItemProperty -Path 'HKCU:\Software\Adobe\CSXS.12' -Name 'PlayerDebugMode' -Value '1' -PropertyType String -Force
```

**Mac** — run in Terminal:
```bash
defaults write com.adobe.CSXS.11 PlayerDebugMode 1
defaults write com.adobe.CSXS.12 PlayerDebugMode 1
```

### 5. Install ffmpeg (if not already installed)

Check if ffmpeg exists at `C:\ffmpeg\bin\ffmpeg.exe` (Windows) or via `which ffmpeg` (Mac).

**Windows** — if missing, download and install:
```powershell
Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'C:\Users\<user>\AppData\Local\Temp\ffmpeg_temp.zip' -UseBasicParsing
Expand-Archive -Path 'C:\Users\<user>\AppData\Local\Temp\ffmpeg_temp.zip' -DestinationPath 'C:\Users\<user>\AppData\Local\Temp\ffmpeg_extracted' -Force
# Find the extracted folder name dynamically, then:
New-Item -ItemType Directory -Path 'C:\ffmpeg\bin' -Force
Copy-Item '<extracted_path>\bin\ffmpeg.exe' -Destination 'C:\ffmpeg\bin\ffmpeg.exe' -Force
Copy-Item '<extracted_path>\bin\ffprobe.exe' -Destination 'C:\ffmpeg\bin\ffprobe.exe' -Force
```

**Mac** — if missing:
```bash
brew install ffmpeg
```

### 6. Verify and report

After completing all steps, confirm:
- [ ] Extension directory created with all files
- [ ] PlayerDebugMode enabled in registry/defaults
- [ ] ffmpeg available at expected path
- [ ] CSInterface.js present

Then tell the user:
> **התקנה הושלמה!**
> פתח/הפעל מחדש את Premiere Pro, ואז:
> **Window → Extensions → Silence Cutter**
>
> אם הפאנל לא מופיע — סגור לגמרי ופתח מחדש את פרימייר.
