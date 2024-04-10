""" Settings variables for Speaker Balancer. """

# Define dictionary items
fields = {
    # Session variables
    'num_speakers': {'type': 'int', 'value': 4},

    # Playback variables
    'duration': {'type': 'float', 'value': 3.0},
    'level': {'type': 'float', 'value': -30.0},

    # Audio device variables
    'audio_device': {'type': 'int', 'value': 999},
    'channel_routing': {'type': 'str', 'value': '1'},

    # Calibration variables
    'cal_file': {'type': 'str', 'value': 'cal_stim.wav'},
    'cal_level_dB': {'type': 'float', 'value': -30.0},
    'slm_reading': {'type': 'float', 'value': 70.0},
    'slm_offset': {'type': 'float', 'value': 100.0},

    # Presentation level variables
    'adjusted_level_dB': {'type': 'float', 'value': -25.0},
    'desired_level_dB': {'type': 'float', 'value': 75},

    # Version control variables
    'config_file_status': {'type': 'int', 'value': 0},
    'check_for_updates': {'type': 'str', 'value': 'yes'},
    'version_lib_path': {'type': 'str', 'value': r'\\starfile\Public\Temp\MooreT\Personal Files\admin\versions.xlsx'},
}
