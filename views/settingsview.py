""" Settings view for Speaker Balancer. 

    Written by: Travis M. Moore
    Last edited: May 02, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import tkinter as tk
from tkinter import ttk

###########
# Logging #
###########
# Create new logger
logger = logging.getLogger(__name__)

################
# SettingsView #
################
class SettingsView(tk.Toplevel):
    """ View for setting session parameters. """
    def __init__(self, parent, settings, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        logger.debug("Initializing SettingsView")

        # Assign attributes
        self.parent = parent
        self.settings = settings

        # Window setup
        self.withdraw()
        self.resizable(False, False)
        self.title("Settings")
        self.grab_set()

        # Populate view with widgets
        self._draw_widgets()


    def _draw_widgets(self):
        """ Populate the MainView with widgets. """
        logger.debug("Drawing MainView widgets")
        #################
        # Create Frames #
        #################
        # Shared frame settings
        frame_options = {'padx': 10, 'pady': 10}
        widget_options = {'padx': 5, 'pady': 5}

        # Session info frame
        frm_session = ttk.Labelframe(self, text='Settings')
        frm_session.grid(row=5, column=5, **frame_options, sticky='nsew')

        # # Session options frame
        # frm_options = ttk.Labelframe(self, text='Stimulus Options')
        # frm_options.grid(row=10, column=5, **frame_options, sticky='nsew')

        # # Audio file browser frame
        # frm_audiopath = ttk.Labelframe(self, text="Audio File Directory")
        # frm_audiopath.grid(row=15, column=5, **frame_options, ipadx=5, 
        #     ipady=5)

        # # Matrix file browser frame
        # frm_matrixpath = ttk.Labelframe(self, text='Matrix File Path')
        # frm_matrixpath.grid(row=20, column=5, **frame_options, ipadx=5, 
        #     ipady=5)


        ################
        # Draw Widgets #
        ################
        # Number of speakers
        ttk.Label(frm_session, text="Number of Speakers:",
            ).grid(row=5, column=5, sticky='e', **widget_options)
        ttk.Entry(frm_session, width=6, 
            textvariable=self.settings['num_speakers']
            ).grid(row=5, column=10, sticky='w')
        ttk.Label(frm_session, text="(Requires restart)"
            ).grid(row=5, column=15, sticky='w', padx=5)


        # ###################
        # # Audio Directory #
        # ###################
        # # Descriptive label
        # ttk.Label(frm_audiopath, text="Path:"
        #     ).grid(row=20, column=5, sticky='e', **widget_options)

        # # Retrieve and truncate previous audio directory
        # short_audio_path = general.truncate_path(
        #     self.settings['audio_files_dir'].get()
        # )

        # # Create textvariable
        # self.audio_var = tk.StringVar(value=short_audio_path)

        # # Audio directory label
        # ttk.Label(frm_audiopath, textvariable=self.audio_var, 
        #     borderwidth=2, relief="solid", width=60
        #     ).grid(row=20, column=10, sticky='w')
        # ttk.Button(frm_audiopath, text="Browse", 
        #     command=self._get_audio_directory,
        #     ).grid(row=25, column=10, sticky='w', pady=(0, 10))


        # Submit button
        btn_submit = ttk.Button(self, text="Submit", command=self._on_submit)
        btn_submit.grid(row=40, column=5, columnspan=2, pady=(0, 10))

        # Center the session dialog window
        self.center_window()


    #############
    # Functions #
    #############
    def center_window(self):
        """ Center the TopLevel window over the root window. """
        logger.debug("Centering window over parent")
        # Get updated window size (after drawing widgets)
        self.update_idletasks()

        # Calculate the x and y coordinates to center the window
        x = self.parent.winfo_x() \
            + (self.parent.winfo_width() - self.winfo_reqwidth()) // 2
        y = self.parent.winfo_y() \
            + (self.parent.winfo_height() - self.winfo_reqheight()) // 2
        
        # Set the window position
        self.geometry("+%d+%d" % (x, y))

        # Display window
        self.deiconify()


    def _on_submit(self):
        """ Send submit event to controller and close window. """
        logger.debug("Sending 'SUBMIT' event to controller")
        self.parent.event_generate('<<SettingsSubmit>>')
        logger.debug("Destroying SettingsView instance")
        self.destroy()


if __name__ == "__main__":
    pass
