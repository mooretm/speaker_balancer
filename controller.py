""" Speaker Balancer. 

    App to balance lab speakers using a sound level meter.
    Also useful for troubleshooting speakers. 

    Written by: Travis M. Moore
    Created: June 09, 2022
"""

###########
# Imports #
###########
# Standard library
import datetime
import json
import logging.config
import logging.handlers
import os
import sys
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from threading import Thread
from tkinter import messagebox

# Third party
import markdown

# Custom
try:
    sys.path.append(os.environ['TMPY'])
except KeyError:
    sys.path.append('C:\\Users\\MooTra\\Code\\Python')
import app_assets
import menus
import models
import setup
import tmpy
import views
from tmpy import tkgui

##########
# Logger #
##########
logger = logging.getLogger(__name__)

def setup_logging(NAME):
    """ Create output log file path. 
        Import and update logging config JSON file.
        Apply config to logger.
    """
    # Create logging output file path based on app name
    flat_name = tmpy.functions.helper_funcs.flatten_text(NAME)
    _app_with_ext = flat_name + '.log.jsonl'
    filename = os.path.join(Path.home(), flat_name, _app_with_ext)

    # Specify logging config file path
    try:
        config_file = os.path.join(
            os.environ['TMPY'],
            'tmpy',
            'logger',
            'logger_config.json'
        )
    except KeyError:
        config_file = tmpy.logger.LOGGER_CONFIG_JSON

    # Import and update logging config file
    with open(config_file) as f_in:
        config = json.load(f_in)
        # Update output file location based on app name
        config['handlers']['file']['filename'] = filename
        # Pass in custom JSONFormatter
        config['formatters']['json']['()'] = tmpy.logger.JSONFormatter

    # Apply logging config
    logging.config.dictConfig(config)

###############
# Application #
###############
class Application(tk.Tk):
    """ Application root window. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #############
        # Constants #
        #############
        self.NAME = 'Speaker Balancer'
        self.VERSION = '4.0.1'
        self.EDITED = 'May 06, 2024'

        # Window setup
        self.withdraw() # Hide window during setup
        self.resizable(False, False)
        self.title(self.NAME)
        self.taskbar_icon = tk.PhotoImage(
            file=tkgui.shared_assets.images.LOGO_FULL_PNG
            )
        self.iconphoto(True, self.taskbar_icon)

        ######################################
        # Initialize Models, Menus and Views #
        ######################################
        # Load current settings from file
        # or load defaults if file does not exist yet
        self.settings_model = tkgui.models.SettingsModel(
            parent=self,
            settings_vars=setup.settings_vars.fields,
            app_name=self.NAME
            )
        self._load_settings()

        # Set up custom logger as soon as config dir is created
        # (i.e., after settings model has been initialized)
        setup_logging(self.NAME)
        logger.debug("Started custom logger")
        logger.debug("Initializing application")

        # Assign special quit function on window close
        self.protocol('WM_DELETE_WINDOW', self._quit)

        # Create variable dictionary
        self._vars = {
            'selected_speaker': tk.IntVar(value=None),
            'slm_reading': tk.DoubleVar(value=None),
        }

        # Create SpeakerWrangler object
        self.speakers = self._create_speakerwrangler()

        # Load calibration model
        self.calibration_model = tkgui.models.CalibrationModel(self.settings)

        # Load main view
        self.main_view = views.MainView(self, self.settings, self._vars)
        self.main_view.grid(row=5, column=5)

        # Load menus
        # Create menu settings dictionary
        self._app_info = {
            'name': self.NAME,
            'version': self.VERSION,
            'last_edited': self.EDITED
        }
        self.menu = menus.MainMenu(self, self._app_info)
        self.config(menu=self.menu)

        # Create callback dictionary
        event_callbacks = {
            # File menu
            '<<FileSettings>>': lambda _: self._show_settings_view(),
            '<<FileQuit>>': lambda _: self._quit(),

            # Tools menu
            '<<ToolsAudioSettings>>': lambda _: self._show_audio_dialog(),
            '<<ToolsCalibration>>': lambda _: self._show_calibration_dialog(),
            '<<ToolsTestOffsets>>': lambda _: self._on_test_offsets(),

            # Help menu
            '<<HelpREADME>>': lambda _: self._show_help(),
            '<<HelpChangelog>>': lambda _: self._show_changelog(),

            # Settings window
            '<<SettingsSubmit>>': lambda _: self._save_settings(),

            # Calibration window
            '<<CalPlay>>': lambda _: self.play_calibration_file(),
            '<<CalStop>>': lambda _: self.stop_audio(),
            '<<CalibrationSubmit>>': lambda _: self._calc_offset(),

            # Audio settings window
            '<<AudioViewSubmit>>': lambda _: self._save_settings(),

            # Main View
            '<<MainPlay>>': lambda _: self._on_play(),
            '<<MainStop>>': lambda _: self.stop_audio(),
            '<<MainSubmit>>': lambda _: self._on_submit(),
            '<<MainSave>>': lambda _: self._on_save(),
        }

        # Bind callbacks to sequences
        logger.debug("Binding callbacks to controller")
        for sequence, callback in event_callbacks.items():
            self.bind(sequence, callback)

        ###################
        # Version Control #
        ###################
        # Check for updates
        if self.settings['check_for_updates'].get() == 'yes':
            _filepath = self.settings['version_lib_path'].get()
            u = tkgui.models.VersionModel(_filepath, self.NAME, self.VERSION)
            if u.status == 'mandatory':
                logger.critical("This version: %s", self.VERSION)
                logger.critical("Mandatory update version: %s", u.new_version)
                messagebox.showerror(
                    title="New Version Available",
                    message="A mandatory update is available. Please install " +
                        f"version {u.new_version} to continue.",
                    detail=f"You are using version {u.app_version}, but " +
                        f"version {u.new_version} is available."
                )
                logger.critical("Application failed to initialize")
                self.destroy()
                return
            elif u.status == 'optional':
                messagebox.showwarning(
                    title="New Version Available",
                    message="An update is available.",
                    detail=f"You are using version {u.app_version}, but " +
                        f"version {u.new_version} is available."
                )
            elif u.status == 'current':
                pass
            elif u.status == 'app_not_found':
                messagebox.showerror(
                    title="Update Check Failed",
                    message="Cannot retrieve version number!",
                    detail=f"'{self.NAME}' does not exist in the version library."
                 )
            elif u.status == 'library_inaccessible':
                messagebox.showerror(
                    title="Update Check Failed",
                    message="The version library is unreachable!",
                    detail="Please check that you have access to Starfile."
                )

        # Center main window
        self.center_window()

        # Initialization successful
        logger.info('Application initialized successfully')

    #####################
    # General Functions #
    #####################
    def center_window(self):
        """ Center the root window. """
        logger.debug("Centering root window after drawing widgets")
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2
        self.geometry("+%d+%d" % (x, y))
        self.deiconify()


    def _create_filename(self):
        """ Create file name and path. """
        logger.debug("Creating file name with date stamp")
        datestamp = datetime.datetime.now().strftime("%Y_%b_%d_%H%M")
        self.filename = "speaker_offsets_" + datestamp + ".csv"


    def _create_speakerwrangler(self):
        """ Instantiate a SpeakerWrangler object and populate it with
            the specified number of speakers.
        """
        # Get specified number of speakers
        num_speakers = self.settings['num_speakers'].get()

        # Instantiate and populate SpeakerWrangler
        sw = models.SpeakerWrangler()
        for ii in range(0, num_speakers):
            sw.add_speaker(ii)
        return sw


    def _quit(self):
        """ Exit the application. """
        logger.info("User ended the session")
        self.destroy()


    ###################
    # File Menu Funcs #
    ###################
    def _show_settings_view(self):
        """ Show session parameter dialog. """
        logger.debug("Calling settings view")
        views.SettingsView(self, self.settings)


    ########################
    # Main View Functions #
    ########################
    def _on_play(self):
        """ Generate and present WGN. """
        logger.debug("Play button pressed")
        # Save latest duration and level values
        logger.debug("Saving provided level and duration values")
        self._save_settings()

        # Generate WGN
        logger.debug("Generating white Gaussian noise")
        FS = 48000
        _wgn = tmpy.tmsignals.wgn(dur=self.settings['duration'].get(), fs=FS)

        # Present WGN
        self.present_audio(
            audio=_wgn, 
            pres_level=self.settings['level'].get(),
            sampling_rate=FS
        )


    def _on_submit(self):
        """ Save SLM Reading value and update Speaker object. """
        logger.debug("Submit button pressed")
        # Get current values
        current_speaker = self._vars['selected_speaker'].get()
        slm_level = self._vars['slm_reading'].get()

        # Calculate speaker offset
        try:
            self.speakers.calc_offset(
                channel=current_speaker, 
                slm_level=slm_level
            )
            self.main_view.update_offset_labels(
                channel=current_speaker,
                offset=self.speakers.speaker_list[current_speaker].offset
            )
        except TypeError as e:
            msg = "Please start with channel 1 to create a reference level!"
            logger.exception(msg)
            messagebox.showwarning(
                title="Invalid Reference Level",
                message=msg,
                detail=e
            )
        
        # Show feedback
        logger.info("%s", 
                    self.speakers.speaker_list[current_speaker].__dict__
                    )


    def _on_save(self):
        """ Create dictionary with channels and offsets.
            Save dictionary to CSV. 
        """
        logger.debug("Attempting to create offset file")
        # Check for missing offsets (i.e., speakers that weren't balanced)
        missing_offsets = self.speakers.check_for_missing_offsets()
        if missing_offsets:
            missing = [int(val)+1 for val in missing_offsets]
            missing = str(missing)[1:-1]
            resp = messagebox.askyesno(
                title="Missing Value",
                message="Do you want to proceed with missing offsets?",
                detail=f"Speakers with missing offsets: {missing}"
            )
            if not resp:
                return
  
        # Create offsets dictionary
        offset_dict = self.speakers.get_data()

        # Create file name
        self._create_filename()

        # Call filehandler save function
        logger.debug("Attempting to save file")
        try:
            self.mycsv = tmpy.readwrite.CSVFile(
                filepath=self.filename, 
                data=offset_dict, 
                file_browser=True
            )
        except PermissionError as e:
            logger.exception(e)
            messagebox.showerror(
                title="Access Denied",
                message="Data not saved! Cannot write to file!",
                detail=e
            )
            return
        except OSError as e:
            logger.exception(e)
            messagebox.showerror(
                title="File Not Found",
                message="Cannot find file or directory!",
                detail=e
            )
            return


    ###########################
    # Settings View Functions #
    ###########################
    def _load_settings(self):
        """ Load parameters into self.settings dict. """
        # Variable types
        vartypes = {
        'bool': tk.BooleanVar,
        'str': tk.StringVar,
        'int': tk.IntVar,
        'float': tk.DoubleVar
        }

        # Create runtime dict from settingsmodel fields
        self.settings = dict()
        for key, data in self.settings_model.fields.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.settings[key] = vartype(value=data['value'])
        logger.debug("Loaded settings model fields into " +
            "running settings dict")


    def _save_settings(self, *_):
        """ Save current runtime parameters to file. """
        logger.debug("Calling settings model set and save funcs")
        for key, variable in self.settings.items():
            self.settings_model.set(key, variable.get())
            self.settings_model.save()


    ########################
    # Tools Menu Functions #
    ########################
    def _on_test_offsets(self):
        """ Start automated offset test thread. """
        logger.debug("Beginning automated offset test")
        # Delete existig instances of thread object
        try:
            del self.t
            logger.debug("Deleted thread instance")
        except AttributeError:
            pass

        # Create and call Thread instance
        try:
            logger.debug("Creating and calling new thread")
            self.t = Thread(target=self._on_test_offsets_thread)
            self.t.start()
        except:
            logger.critical("Failed to start audio thread!")
            return


    def _on_test_offsets_thread(self):
        """ Automatically step through all speakers. """
        logger.debug("New thread for looping through speakers")
        # Get number of speakers/channels
        num_speakers = self.settings['num_speakers'].get()

        # Update mainview: START TEST
        self.main_view.start_auto_test()

        # Present WGN to each speaker for the specified duration
        for ii in range(0, num_speakers):
            logger.debug("Testing speaker %d", ii)
            # Select speaker number
            self._vars['selected_speaker'].set(ii)

            # Enable current speaker button on mainframe
            self.main_view._update_single_speaker_button_state(ii, 'enabled')

            # Routing from the audioview is saved as a string
            chan=str(ii+1)
            self.settings['channel_routing'].set(chan)

            # Start audio playback
            self._on_play()

            # Sleep for duration of playback
            time.sleep(self.settings['duration'].get())

            # Disable current speaker button
            self.main_view._update_single_speaker_button_state(ii, 'disabled')

        # Update mainview: END TEST
        self.main_view.end_auto_test()


    def _show_audio_dialog(self):
        """ Show audio settings dialog. """
        logger.debug("Calling audio device window")
        tkgui.views.AudioView(self, self.settings)


    def _show_calibration_dialog(self):
        """ Display the calibration dialog window. """
        logger.debug("Calling calibration window")
        tkgui.views.CalibrationView(self, self.settings)


    ################################
    # Calibration Dialog Functions #
    ################################
    def play_calibration_file(self):
        """ Load calibration file and present. """
        logger.debug("Play calibration file called")
        # Get calibration file
        try:
            self.calibration_model.get_cal_file()
        except AttributeError:
            logger.exception("Cannot find internal calibration file!")
            messagebox.showerror(
                title="File Not Found",
                message="Cannot find internal calibration file!",
                detail="Please use a custom calibration file."
            )
        # Present calibration signal
        self.present_audio(
            audio=Path(self.calibration_model.cal_file), 
            pres_level=self.settings['cal_level_dB'].get()
        )


    def _calc_offset(self):
        """ Calculate offset based on SLM reading. """
        # Calculate new presentation level
        self.calibration_model.calc_offset()
        # Save level - this must be called here!
        self._save_settings()


    def _calc_level(self, desired_spl):
        """ Calculate new dB FS level using slm_offset. """
        # Calculate new presentation level
        self.calibration_model.calc_level(desired_spl)
        # Save level - this must be called here!
        self._save_settings()

    #######################
    # Help Menu Functions #
    #######################
    def _show_help(self):
        """ Create html help file and display in default browser. """
        logger.debug("Calling README file (will open in browser)")
        # Read markdown file and convert to html
        with open(app_assets.README.README_MD, 'r') as f:
            text = f.read()
            html = markdown.markdown(text)

        # Create html file for display
        with open(app_assets.README.README_HTML, 'w') as f:
            f.write(html)

        # Open README in default web browser
        webbrowser.open(app_assets.README.README_HTML)


    def _show_changelog(self):
        """ Create html CHANGELOG file and display in default browser. """
        logger.debug("Calling CHANGELOG file (will open in browser)")
        # Read markdown file and convert to html
        with open(app_assets.CHANGELOG.CHANGELOG_MD, 'r') as f:
            text = f.read()
            html = markdown.markdown(text)

        # Create html file for display
        with open(app_assets.CHANGELOG.CHANGELOG_HTML, 'w') as f:
            f.write(html)

        # Open CHANGELOG in default web browser
        webbrowser.open(app_assets.CHANGELOG.CHANGELOG_HTML)


    ###################
    # Audio Functions #
    ###################
    def _create_audio_object(self, audio, **kwargs):
        # Create audio object
        try:
            self.a = tmpy.audio_handlers.AudioPlayer(
                audio=audio,
                **kwargs
            )
        except FileNotFoundError:
            logger.exception("Cannot find audio file!")
            messagebox.showerror(
                title="File Not Found",
                message="Cannot find the audio file!",
                detail="Go to File>Session to specify a valid audio path."
            )
            self._show_settings_view()
            return
        except tmpy.audio_handlers.audio_exceptions.InvalidAudioType:
            raise
        except tmpy.audio_handlers.audio_exceptions.MissingSamplingRate:
            raise


    def _format_routing(self, routing):
        """ Convert space-separated string to list of ints
            for speaker routing.
        """
        logger.debug("Formatting channel routing string as list")
        routing = routing.split()
        routing = [int(x) for x in routing]
        return routing
    

    def _play(self, pres_level):
        """ Format channel routing, present audio and catch exceptions. """
        # Attempt to present audio
        try:
            self.a.play(
                level=pres_level,
                device_id=self.settings['audio_device'].get(),
                routing=self._format_routing(
                    self.settings['channel_routing'].get())
            )
        except tmpy.audio_handlers.InvalidAudioDevice as e:
            logger.exception("Invalid audio device: %s", e)
            messagebox.showerror(
                title="Invalid Device",
                message="Invalid audio device! Go to Tools>Audio Settings " +
                    "to select a valid audio device.",
                detail = e
            )
            # Open Audio Settings window
            self._show_audio_dialog()
        except tmpy.audio_handlers.InvalidRouting as e:
            logger.exception("Invalid routing: %s", e)
            messagebox.showerror(
                title="Invalid Routing",
                message="Speaker routing must correspond with the " +
                    "number of channels in the audio file! Go to " +
                    "Tools>Audio Settings to update the routing.",
                detail=e
            )
            # Open Audio Settings window
            self._show_audio_dialog()
        except tmpy.audio_handlers.Clipping:
            logger.exception("Clipping has occurred - aborting!")
            messagebox.showerror(
                title="Clipping",
                message="The level is too high and caused clipping.",
                detail="The waveform will be plotted when this message is " +
                    "closed for visual inspection."
            )
            self.a.plot_waveform("Clipped Waveform")


    def present_audio(self, audio, pres_level, **kwargs):
        # Load audio
        try:
            self._create_audio_object(audio, **kwargs)
        except tmpy.audio_handlers.InvalidAudioType as e:
            logger.exception("Invalid audio format: %s", e)
            messagebox.showerror(
                title="Invalid Audio Type",
                message="The audio type is invalid!",
                detail=f"{e} Please provide a Path or ndarray object."
            )
            return
        except tmpy.audio_handlers.MissingSamplingRate as e:
            logger.exception("Missing sampling rate: %s", e)
            messagebox.showerror(
                title="Missing Sampling Rate",
                message="No sampling rate was provided!",
                detail=f"{e} Please provide a Path or ndarray object."
            )
            return

        # Play audio
        self._play(pres_level)


    def stop_audio(self):
        """ Stop audio playback. """
        logger.debug("User stopped audio playback")
        try:
            self.a.stop()
        except AttributeError:
            logger.debug("Stop called, but there is no audio object!")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
