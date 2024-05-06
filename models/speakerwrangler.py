""" Classes to create speaker objects and a speaker wrangler.

    Written by: Travis M. Moore
    Last edited: May 02, 2024
"""

###########
# Imports #
###########
# Standard library
import logging

# Third party
import numpy as np

##########
# Logger #
##########
logger = logging.getLogger(__name__)

###########
# Speaker #
###########
class Speaker:
    """ Speaker object with position number, offset, and 
    calibrated(boolean) attributes.
    """
    def __init__(self, channel):
        logger.debug("Initializing Speaker object")
        self.channel = channel
        self.slm_level = None
        self.offset = None
        self.calibrated = False

####################
# Speaker Wrangler #
####################
class SpeakerWrangler:
    """ Class to handle Speaker objects. """
    def __init__(self):
        logger.debug("Initializing SpeakerWrangler object")
        # Empty list to hold Speaker objects
        self.speaker_list = []

        # Reference level: channel 0 slm_level
        self.ref_level = None 


    def add_speaker(self, channel):
        """ Create new speaker obj and append to list."""
        speaker = Speaker(channel=channel)
        self.speaker_list.append(speaker)
        return speaker


    def calc_offset(self, channel, slm_level):
        """ Calculate and update offset. """
        logger.debug("Calculating offset")
        if channel == 0:
            self.ref_level = slm_level

        # Calculate offset
        try:
            offset = np.round(self.ref_level - slm_level, 1)
        except TypeError:
            raise TypeError
        
        # Update Speaker attributes
        logger.debug("Updating Speaker attributes")
        self.speaker_list[channel].slm_level = slm_level
        self.speaker_list[channel].offset = offset
        self.speaker_list[channel].calibrated = True


    def check_for_missing_offsets(self):
        """ Loop through each Speaker object and test whether the 
            .calibrated attribute is set to True.
        """
        logger.debug("Checking for missing offsets")
        missing_offsets = []
        for speaker in self.speaker_list:
            if not speaker.calibrated:
                missing_offsets.append(speaker.channel)
                msg = f"Missing offset for speaker {speaker.channel}!"
                logger.warning(msg)
        return missing_offsets


    def get_data(self):
        """ Return a dictionary of channels and offsets. """
        logger.debug("Preparing dictionary of offsets")
        channels = [speaker.channel for speaker in self.speaker_list]
        offsets = [speaker.offset for speaker in self.speaker_list]
        return dict(zip(channels, offsets))
