import math
import tkinter as tk
import subprocess

from tkinter import filedialog, ttk

from config_file_handler import ConfigFileHandler


class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder='Enter text here', placeholder_color='grey', width=20, textvariable=None, *args, **kwargs):
        self.textvar = textvariable if textvariable is not None else tk.StringVar()

        super().__init__(master, textvariable=self.textvar, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        self.configure(width=width)

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

        self._add_placeholder()

    def _add_placeholder(self, event=None):
        if not self.textvar.get():
            style = ttk.Style()
            self.configure(style='Placeholder.TEntry')
            style.configure('Placeholder.TEntry', foreground=self.placeholder_color)
            self.textvar.set(self.placeholder)

    def _clear_placeholder(self, event=None):
        if self.get() == self.placeholder:
            style = ttk.Style()
            self.configure(style='Placeholder.TEntry')
            style.configure('Placeholder.TEntry', foreground='black')
            self.textvar.set('')


class Gui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('CTD Process')
        self.minsize(350, 400)

        self.config_handler = ConfigFileHandler()
        self.config = self.config_handler.config

        self.cruise_number = tk.StringVar(value=self.config['cruise_number'])
        self.base_dir = tk.StringVar(value=self.config['base_dir'])
        self.output_dir = tk.StringVar(value=self.config['output_dir'])

        self.ctd_directory = tk.StringVar(value=self.config['ctd_dir'])
        self.tracking_directory = tk.StringVar(value=self.config['tracking_dir'])
        self.ctd_file_names = tk.StringVar(value=self.config['ctd_file_names'])
        self.tracking_file_names = tk.StringVar(value=self.config['tracking_file_names'])

        self.timestamp_col = tk.StringVar(value=self.config['ctd_cols']['timestamp'])
        self.temperature_col = tk.StringVar(value=self.config['ctd_cols']['temperature'])
        self.depth_col = tk.StringVar(value=self.config['ctd_cols']['depth'])
        self.salinity_col = tk.StringVar(value=self.config['ctd_cols']['salinity'])
        self.oxygen_col = tk.StringVar(value=self.config['ctd_cols']['oxygen'])

        self.unix_time_col = tk.StringVar(value=self.config['tracking_cols']['unix_time'])
        self.altitude_col = tk.StringVar(value=self.config['tracking_cols']['altitude'])
        self.latitude_col = tk.StringVar(value=self.config['tracking_cols']['latitude'])
        self.longitude_col = tk.StringVar(value=self.config['tracking_cols']['longitude'])

        self.notebook = ttk.Notebook(master=self)
        self.process_bg = ttk.Frame(master=self.notebook)
        self.settings_bg = ttk.Frame(master=self.notebook)

        self.button_text = tk.StringVar(value='GO')
        self.processing_text = tk.StringVar(value='')
        self.config_save_status = tk.StringVar(value='')
        self.canvas = tk.Canvas(master=self.process_bg, width=50, height=50, bg='#e5e5e5', highlightthickness=0)
        self.processing = False

        self.columns_frame = ttk.Frame(master=self.settings_bg)
        self.ctd_columns_frame = tk.Frame(
            master=self.columns_frame,
            highlightbackground='#ccc',
            highlightthickness=1,
            highlightcolor='#ddd'
        )
        self.tracking_columns_frame = tk.Frame(
            master=self.columns_frame,
            highlightbackground='#ccc',
            highlightthickness=1,
            highlightcolor='#ddd'
        )

        self.notebook.pack()
        self.notebook.add(self.process_bg, text='Process')
        self.notebook.add(self.settings_bg, text='Settings')
        self.initialize_process_widgets()
        self.initialize_settings_widgets()
        self.set_column_widgets('CTD')

    def go_button_callback(self, go_button):
        cruise_number = self.cruise_number.get()
        base_dir = self.base_dir.get()
        output_dir = self.output_dir.get()
        process = None
        if cruise_number.startswith('EX'):
            process = subprocess.Popen([
                'EX/ex_ctd_processor.sh',
                cruise_number,
                base_dir,
                output_dir,
            ])
        elif cruise_number.startswith('NA'):
            process = subprocess.Popen([
                'NA/na_ctd_processor.sh',
                cruise_number,
                base_dir,
                f'{base_dir}/processed/dive_reports',
                output_dir,
            ])
        else:
            self.processing_text.set('Could not determine preset \nCruise number should start with "NA" or "EX"')
            return
        self.button_text.set('CANCEL')
        go_button.config(command=lambda: self.stop_button_callback(process, go_button))
        self.processing_text.set('Processing - See terminal for details')
        self.processing = True
        self.update_spinner(0)
        self.check_process(process, go_button)

    def stop_button_callback(self, process, go_button):
        process.terminate()
        self.processing = False
        self.button_text.set('GO')
        go_button.config(command=lambda: self.go_button_callback(go_button))
        self.processing_text.set('Cancelled')

    def check_process(self, process, go_button):
        if process.poll() is None:
            self.after(1000, self.check_process, process, go_button)
        else:
            exit_val = process.returncode
            self.processing = False
            self.button_text.set('GO')
            go_button.config(command=lambda: self.go_button_callback(go_button))
            if exit_val != 0:
                self.processing_text.set('Cancelled' if self.processing_text.get() == 'Cancelled' else 'Error - See terminal for details')
                return
            self.processing_text.set('Cancelled' if self.processing_text.get() == 'Cancelled' else 'Complete!')

    def get_file_path(self, path):
        file_path = filedialog.askdirectory(initialdir='/Volumes/maxarray2/varsadditional', title='Select a folder')
        path.set(file_path)

    def save_button_callback(self):
        config = {
            'cruise_number': self.cruise_number.get(),
            'base_dir': self.base_dir.get(),
            'output_dir': self.output_dir.get(),
            'ctd_dir': self.ctd_directory.get(),
            'tracking_dir': self.tracking_directory.get(),
            'ctd_file_names': self.ctd_file_names.get(),
            'tracking_file_names': self.tracking_file_names.get(),
            'ctd_cols': {
                'timestamp': self.timestamp_col.get(),
                'temperature': self.temperature_col.get(),
                'depth': self.depth_col.get(),
                'salinity': self.salinity_col.get(),
                'oxygen': self.oxygen_col.get(),
            },
            'tracking_cols': {
                'unix_time': self.unix_time_col.get(),
                'altitude': self.altitude_col.get(),
                'latitude': self.latitude_col.get(),
                'longitude': self.longitude_col.get(),
            }
        }
        if self.config_handler.save_config(config):
            self.config_save_status.set('Saved!')
        else:
            self.config_save_status.set('Error saving config')

    def update_spinner(self, angle):
        self.canvas.delete('spinner')
        if not self.processing:
            return
        x = 25 + 10 * math.cos(angle)
        y = 25 + 10 * math.sin(angle)
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='black', tags='spinner')
        self.after(30, self.update_spinner, angle + 0.1)

    def initialize_process_widgets(self):
        background = self.process_bg

        # cruise number input
        cruise_frame = ttk.Frame(master=background)
        cruise_label = ttk.Label(master=cruise_frame, text='CRUISE NUMBER', font=('Helvetica', '13', 'bold'))
        cruise_entry = PlaceholderEntry(
            placeholder='e.g. EX2306',
            master=cruise_frame,
            width=30,
            textvariable=self.cruise_number,
        )

        # base directory input
        base_directory_frame = ttk.Frame(master=background)
        base_directory_entry = ttk.Entry(
            master=base_directory_frame,
            textvariable=self.base_dir,
            width=30,
        )
        base_directory_browse_button = ttk.Button(
            master=base_directory_frame,
            text='Browse',
            command=lambda: self.get_file_path(self.base_dir),
        )
        base_directory_label = ttk.Label(
            master=base_directory_frame,
            text='BASE DIRECTORY',
            font=('Helvetica', '13', 'bold'),
        )

        # output directory input
        output_directory_frame = ttk.Frame(master=background)
        output_directory_entry = ttk.Entry(
            master=output_directory_frame,
            textvariable=self.output_dir,
            width=30,
        )
        output_directory_browse_button = ttk.Button(
            master=output_directory_frame,
            text='Browse',
            command=lambda: self.get_file_path(self.output_dir),
        )
        output_directory_label = ttk.Label(
            master=output_directory_frame,
            text='OUTPUT DIRECTORY',
            font=('Helvetica', '13', 'bold'),
        )

        # processing status
        processing_status_label = ttk.Label(
            master=self.process_bg,
            textvariable=self.processing_text,
            font=('Helvetica', '12'),
        )

        # go button
        go_button = tk.Button(
            master=background,
            textvariable=self.button_text,
            width=20,
            height=2,
            font=('Helvetica', '13', 'bold'),
            command=lambda: self.go_button_callback(go_button),
        )

        # packin
        cruise_frame.pack(pady=(5, 10), fill=tk.X)
        cruise_label.pack(side=tk.TOP, anchor='w')
        cruise_entry.pack(side=tk.TOP, anchor='w')

        base_directory_frame.pack(pady=10, fill=tk.X)
        base_directory_label.pack(anchor='w')
        base_directory_entry.pack(anchor='w')
        base_directory_browse_button.pack(anchor='w')

        output_directory_frame.pack(pady=10, fill=tk.X)
        output_directory_label.pack(anchor='w')
        output_directory_entry.pack(anchor='w')
        output_directory_browse_button.pack(anchor='w')

        go_button.pack(pady=(20, 5))
        processing_status_label.pack(pady=(0, 10))
        self.canvas.pack()

    def initialize_settings_widgets(self):
        background = self.settings_bg

        settings_label = ttk.Label(
            master=background,
            text='EX SETTINGS',
            font=('Helvetica', '14', 'bold'),
        )
        settings_sub_label = ttk.Label(
            master=background,
            text='These settings are only used for EX cruises',
            font=('Helvetica', '10'),
        )
        # ctd directory input
        ctd_directory_frame = ttk.Frame(master=background)
        ctd_directory_entry = ttk.Entry(
            master=ctd_directory_frame,
            textvariable=self.ctd_directory,
            width=30,
        )
        ctd_directory_label = ttk.Label(
            master=ctd_directory_frame,
            text='CTD DIRECTORY',
            font=('Helvetica', '12', 'bold'),
        )

        # tracking directory input
        tracking_directory_frame = ttk.Frame(master=background)
        tracking_directory_entry = ttk.Entry(
            master=tracking_directory_frame,
            textvariable=self.tracking_directory,
            width=30,
        )
        tracking_directory_label = ttk.Label(
            master=tracking_directory_frame,
            text='TRACKING DIRECTORY',
            font=('Helvetica', '12', 'bold'),
        )

        ctd_naming_frame = ttk.Frame(master=background)
        ctd_naming_label = ttk.Label(
            master=ctd_naming_frame,
            text='CTD FILE NAMES',
            font=('Helvetica', '12', 'bold'),
        )
        ctd_naming_entry = ttk.Entry(
            master=ctd_naming_frame,
            width=30,
            textvariable=self.ctd_file_names,
        )

        dive_naming_frame = ttk.Frame(master=background)
        dive_naming_label = ttk.Label(
            master=dive_naming_frame,
            text='TRACKING FILE NAMES',
            font=('Helvetica', '12', 'bold'),
        )
        dive_naming_entry = ttk.Entry(
            master=dive_naming_frame,
            width=30,
            textvariable=self.tracking_file_names,
        )

        columns_header_frame = ttk.Frame(master=self.columns_frame)
        columns_label = ttk.Label(
            master=columns_header_frame,
            text='COLUMNS',
            font=('Helvetica', '13', 'bold'),
        )
        column_combobox = ttk.Combobox(
            master=columns_header_frame,
            values=['CTD', 'Tracking'],
            width=10,
            state='readonly',
        )
        column_combobox.current(0)
        column_combobox.bind('<<ComboboxSelected>>', lambda event: self.set_column_widgets(column_combobox.get()))

        timestamp_frame = tk.Frame(master=self.ctd_columns_frame)
        timestamp_label = tk.Label(
            master=timestamp_frame,
            text='TIMESTAMP',
            font=('Helvetica', '12', 'bold'),
        )
        timestamp_entry = tk.Entry(
            master=timestamp_frame,
            width=6,
            textvariable=self.timestamp_col,
        )

        temperature_frame = tk.Frame(master=self.ctd_columns_frame)
        temperature_label = tk.Label(
            master=temperature_frame,
            text='TEMPERATURE',
            font=('Helvetica', '12', 'bold'),
        )
        temperature_entry = tk.Entry(
            master=temperature_frame,
            width=6,
            textvariable=self.temperature_col,
        )

        depth_frame = tk.Frame(master=self.ctd_columns_frame)
        depth_label = tk.Label(
            master=depth_frame,
            text='DEPTH',
            font=('Helvetica', '12', 'bold'),
        )
        depth_entry = tk.Entry(
            master=depth_frame,
            width=6,
            textvariable=self.depth_col,
        )

        salinity_frame = tk.Frame(master=self.ctd_columns_frame)
        salinity_label = tk.Label(
            master=salinity_frame,
            text='SALINITY',
            font=('Helvetica', '12', 'bold'),
        )
        salinity_entry = tk.Entry(
            master=salinity_frame,
            width=6,
            textvariable=self.salinity_col,
        )

        oxygen_frame = tk.Frame(master=self.ctd_columns_frame)
        oxygen_label = tk.Label(
            master=oxygen_frame,
            text='OXYGEN',
            font=('Helvetica', '12', 'bold'),
        )
        oxygen_entry = tk.Entry(
            master=oxygen_frame,
            width=6,
            textvariable=self.oxygen_col,
        )

        unix_time_frame = tk.Frame(master=self.tracking_columns_frame)
        unix_time_label = tk.Label(
            master=unix_time_frame,
            text='UNIX TIME',
            font=('Helvetica', '12', 'bold'),
        )
        unix_time_entry = tk.Entry(
            master=unix_time_frame,
            width=6,
            textvariable=self.unix_time_col,
        )

        altitude_frame = tk.Frame(master=self.tracking_columns_frame)
        altitude_label = tk.Label(
            master=altitude_frame,
            text='ALTITUDE',
            font=('Helvetica', '12', 'bold'),
        )
        altitude_entry = tk.Entry(
            master=altitude_frame,
            width=6,
            textvariable=self.altitude_col,
        )

        latitude_frame = tk.Frame(master=self.tracking_columns_frame)
        latitude_label = tk.Label(
            master=latitude_frame,
            text='LATITUDE',
            font=('Helvetica', '12', 'bold'),
        )
        latitude_entry = tk.Entry(
            master=latitude_frame,
            width=6,
            textvariable=self.latitude_col,
        )

        longitude_frame = tk.Frame(master=self.tracking_columns_frame)
        longitude_label = tk.Label(
            master=longitude_frame,
            text='LONGITUDE',
            font=('Helvetica', '12', 'bold'),
        )
        longitude_entry = tk.Entry(
            master=longitude_frame,
            width=6,
            textvariable=self.longitude_col,
        )

        save_button = tk.Button(
            master=background,
            text='SAVE',
            width=14,
            height=2,
            font=('Helvetica', '13', 'bold'),
            command=lambda: self.save_button_callback(),
        )

        status = ttk.Label(
            master=background,
            textvariable=self.config_save_status,
            font=('Helvetica', '12'),
        )

        # packin
        settings_label.pack(pady=(5, 0))
        settings_sub_label.pack(pady=(0, 5))

        ctd_directory_frame.pack(fill=tk.X, pady=(0, 5))
        ctd_directory_label.pack(anchor='w')
        ctd_directory_entry.pack(anchor='w')

        tracking_directory_frame.pack(fill=tk.X, pady=(0, 5))
        tracking_directory_label.pack(anchor='w')
        tracking_directory_entry.pack(anchor='w')

        ctd_naming_frame.pack(fill=tk.X, pady=(0, 5))
        ctd_naming_label.pack(anchor='w')
        ctd_naming_entry.pack(anchor='w')

        dive_naming_frame.pack(fill=tk.X, pady=(0, 5))
        dive_naming_label.pack(anchor='w')
        dive_naming_entry.pack(anchor='w')

        self.columns_frame.pack(fill=tk.X)
        columns_header_frame.pack(fill=tk.X)
        columns_label.pack(side=tk.LEFT, anchor='w')
        column_combobox.pack(side=tk.RIGHT, anchor='w')

        self.ctd_columns_frame.pack(fill=tk.X, anchor='s', ipady=5)
        self.pack_column_frame(timestamp_frame, timestamp_label, timestamp_entry, 1)
        self.pack_column_frame(temperature_frame, temperature_label, temperature_entry, 0)
        self.pack_column_frame(depth_frame, depth_label, depth_entry, 0)
        self.pack_column_frame(salinity_frame, salinity_label, salinity_entry, 0)
        self.pack_column_frame(oxygen_frame, oxygen_label, oxygen_entry, -1)
        self.pack_column_frame(unix_time_frame, unix_time_label, unix_time_entry, 1)
        self.pack_column_frame(altitude_frame, altitude_label, altitude_entry, 0)
        self.pack_column_frame(latitude_frame, latitude_label, latitude_entry, 0)
        self.pack_column_frame(longitude_frame, longitude_label, longitude_entry, -1)

        save_button.pack(pady=(5, 0))
        status.pack(pady=(0, 20))

    def set_column_widgets(self, _type):
        if _type == 'CTD':
            # set CTD columns
            self.tracking_columns_frame.pack_forget()
            self.ctd_columns_frame.pack(pady=5, fill=tk.X)
        else:
            # set tracking columns
            self.ctd_columns_frame.pack_forget()
            self.tracking_columns_frame.pack(pady=5, fill=tk.X)

    def pack_column_frame(self, frame, label, entry, pos):
        match pos:
            case 1: frame.pack(fill=tk.X, padx=10, pady=(5, 0))
            case 0: frame.pack(fill=tk.X, padx=10)
            case -1: frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        label.pack(side=tk.LEFT)
        entry.pack(side=tk.RIGHT)


if __name__ == '__main__':
    gui = Gui()
    gui.mainloop()
