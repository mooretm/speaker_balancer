<div style="text-align: center;">
    <img src="logo_full.png" alt="Travis Custom Logo Image" width="70"/>
</div>

<div style="text-align: center;">
    <h1>Speaker Balancer</h1>

    Written by: <b>Travis M. Moore</b>
    <br>
    Latest version: <b>Version 4.0.1</b><br>
    Originally created: <b>June 09, 2022</b><br>
    Last edited: <b>May 06, 2024</b><br><br>
</div>

---

# Description
The Speaker Balancer is a useful tool for quickly balancing lab speakers using a sound level meter. 

- Select speakers just by clicking. 

- Present a white Gaussian noise to the specified speaker. 

- Calculate offsets (using the first speaker as a reference). Easily save offsets to CSV, and monitor offsets in real time as they appear on screen. 
<br>
<br>

---

# Getting Started

## Dependencies

- Windows 10 or greater (not compatible with Mac OS)

## Installing

- This is a compiled app; the executable file is stored on Starfile at: \\starfile\Public\Temp\MooreT\Custom Software

- Simply copy the executable file and paste to a location on the local machine. 

- **DO NOT RUN FROM THE STARFILE SERVER.** This ties up the program for others, and will result in erratic app behavior. 

## First Use
- **DO NOT RUN FROM THE STARFILE SERVER.** This ties up the program for others, and will result in erratic app behavior. That's right, this statement is identical to the one above - it's just that important!

- Double-click to start the application for the first time.
<br>
<br>

---

# Main Screen
The Speaker Balancer offers all the controls you will need on a single screen for ease of use. Enjoy the sky blue band across the top of the screen - it's almost like being at the beach. 

<img src="main_window.png" alt="Main Window Image" width="500"/>

## Controls
### Playback Group
- Duration (s): The duration of the white noise in seconds

- Level (dB): The scaling factor to apply to the white noise. Adjust this level until the sound level meter reads around 70 dB A (slow). 

- Play button: Begin audio playback.

- Stop button: Stop audio playback.

### Offsets Group
- SLM Reading (dB): The value read from the sound level meter while the white noise is actively playing. 

- Calculate Offset button: Calculates an offset based off of the value from speaker 1 and stores that value. 

## Offsets
The Offsets frame displays the offsets for each speaker as they are calculated. Refer to this section while updating the RME offsets using Total Mix. 

## Speaker Number
The Speak Number group contains buttons for each speaker. Route the white noise to any speaker by clicking the appropriate button. 
<br>
<br>

---

# Tools Menu

## Audio Settings
The Audio Settings window allows you to select an audio device and assign speakers for playback. 

<b>Device Selection.</b> The Audio Settings window displays available audio devices in a table (see lower part of image below). Simply click to choose the desired device. Your selection will be highlighted in blue.<br> 
<strong>Important:</strong> DO NOT SELECT ANY DEVICE WITH "ASIO" IN THE NAME. SELECT "Analog (1-8)" WITH 8 OUTPUT CHANNELS. If there are multiple Analog (1-8) options, you will have to guess and check by selecting one, then trying the Tools>Test Offsets function. 

<b>Speaker Assignment.</b> To assign a speaker for playback, enter the speaker/channel number in the entry box (see upper part of image below). Note that you must provide a speaker for each channel in the audio file. For example, if your stimulus has eight channels, you must provide a list of eight speakers. Separate numbers with spaces when providing a list of speakers. For example: ```1 2 3 4 5 6 7 8```.

<img src="audio_settings.png" alt="Audio Settings Window" width="500"/>
<br>
<br>

---

# How to Balance Speakers
The instructions below guide you through the process of using the app to balance the speakers in a given lab. Instructions reference the different color rectangles imposed on the image below.

<img src="totalmix2.png" alt="TotalMix image" width="500"/>

1. Open TotalMix (see image above)
2. Click the Snapshot labeled "Default" (green rectangle)
3. Click the Layout Preset labeled "Default" (green rectangle)
4. Ensure channels are mapped 1-to-1 (click each channel along the bottom row [Hardware Outputs; blue rectangle], and verify that the corresponding channel along the top row [Software Playback; red rectangle] has the level slider in the 0 position)
5. Ensure all the yellow values at the bottom of the sliders along the top row [yellow rectangle] are set to 0
6. Create a new Snapshot and Layout Preset name based on the study (green rectangle)
7. Create a new Snapshot and Layout Preset from the defaults by clicking the "Store" button (the saved profiles will flash), then click on the new profile (flashing will cease)
8. Use the Speaker Balancer as described above
9. Calculated offsets will appear in the "Offsets" group at the far righthand side of the Speaker Balancer screen
10. Use the offset values from the app to update the yellow values under the sliders of the top row of channels (yellow rectangle)
11. Navigate to Tools>Test Offsets to automatically step through each speaker, checking that the sound level meter reads a constant value (within a few tenths of a dB) for all speakers
<br>
<br>

---

# Compiling from Source
```
pyinstaller --noconfirm --onefile --windowed --icon "C:/Users/MooTra/Code/Python/tmpy/tkgui/shared_assets/images/logo_icons/logo_full.ico" --add-data "C:/Users/MooTra/Code/Python/speaker_balancer/app_assets;app_assets/" --add-data "C:/Users/MooTra/Code/Python/tmpy;tmpy/" --paths "C:/Users/MooTra/Code/Python/tmpy" --hidden-import "numpy" --hidden-import "pandas" --hidden-import "sounddevice" --hidden-import "soundfile" --hidden-import "msoffcrypto" --hidden-import "idlelib"  "C:/Users/MooTra/Code/Python/speaker_balancer/controller.py"
```
<br>
<br>

---

# Contact
Please use the contact information below to submit bug reports, feature requests and any other feedback.

- Travis M. Moore: travis_moore@starkey.com
