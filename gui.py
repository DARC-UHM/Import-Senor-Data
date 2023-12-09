import math
import tkinter as tk
import subprocess

from tkinter import filedialog, ttk


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

        self.cruise_number = tk.StringVar(value='')
        self.source_folder = tk.StringVar(value='/Volumes/maxarray2/varsadditional')
        self.output_folder = tk.StringVar(value='/Volumes/maxarray2/varsadditional')

        self.ctd_directory = tk.StringVar(value='{BASE_DIR}/CTD')
        self.tracking_directory = tk.StringVar(value='{BASE_DIR}/Tracking')
        self.ctd_file_names = tk.StringVar(value='${cruise}_${dive}_')
        self.dive_file_names = tk.StringVar(value='${cruise}_${dive}_')

        self.notebook = ttk.Notebook(master=self)
        self.process_bg = ttk.Frame(master=self.notebook)
        self.settings_bg = ttk.Frame(master=self.notebook)

        self.button_text = tk.StringVar(value='GO')
        self.processing_text = tk.StringVar(value='')
        self.canvas = tk.Canvas(master=self.process_bg, width=50, height=50, bg='#e5e5e5', highlightthickness=0)
        self.processing = False

        self.notebook.pack()
        self.notebook.add(self.process_bg, text='Process')
        self.notebook.add(self.settings_bg, text='Settings')
        self.initialize_process_widgets()
        self.initialize_settings_widgets()

    def go_button_callback(self, go_button):
        cruise_number = self.cruise_number.get()
        source_folder = self.source_folder.get()
        output_folder = self.output_folder.get()
        process = None
        if cruise_number.startswith('EX'):
            process = subprocess.Popen([
                'EX/ex_ctd_processor.sh',
                cruise_number,
                source_folder,
                output_folder,
            ])
        elif cruise_number.startswith('NA'):
            process = subprocess.Popen([
                'NA/na_ctd_processor.sh',
                cruise_number,
                source_folder,
                f'{source_folder}/processed/dive_reports',
                output_folder,
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
            textvariable=self.source_folder,
            width=30,
        )
        base_directory_browse_button = ttk.Button(
            master=base_directory_frame,
            text='Browse',
            command=lambda: self.get_file_path(self.source_folder),
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
            textvariable=self.output_folder,
            width=30,
        )
        output_directory_browse_button = ttk.Button(
            master=output_directory_frame,
            text='Browse',
            command=lambda: self.get_file_path(self.output_folder),
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
            font=('Helvetica', '13', 'bold'),
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
            font=('Helvetica', '13', 'bold'),
        )

        naming_conventions_frame = ttk.Frame(master=background)
        ctd_naming_frame = ttk.Frame(master=naming_conventions_frame)
        ctd_naming_label = ttk.Label(
            master=ctd_naming_frame,
            text='CTD FILE NAMES',
            font=('Helvetica', '13', 'bold'),
        )
        ctd_naming_entry = ttk.Entry(
            master=ctd_naming_frame,
            width=14,
            textvariable=self.ctd_file_names,
        )

        dive_naming_frame = ttk.Frame(master=naming_conventions_frame)
        dive_naming_label = ttk.Label(
            master=dive_naming_frame,
            text='DIVE FILE NAMES',
            font=('Helvetica', '13', 'bold'),
        )
        dive_naming_entry = ttk.Entry(
            master=dive_naming_frame,
            width=14,
            textvariable=self.dive_file_names,
        )

        columns_frame = ttk.Frame(master=background)
        columns_label = ttk.Label(
            master=columns_frame,
            text='COLUMNS',
            font=('Helvetica', '13', 'bold'),
        )
        column_combobox = ttk.Combobox(
            master=columns_frame,
            values=['CTD', 'Tracking'],
            width=14,
            state='readonly',
        )
        column_combobox.current(0)
        column_combobox.bind('<<ComboboxSelected>>', lambda event: print(column_combobox.get()))

        # packin
        settings_label.pack(pady=(5, 0))
        settings_sub_label.pack(pady=(0, 5))

        ctd_directory_frame.pack(pady=10)
        ctd_directory_label.pack(anchor='w')
        ctd_directory_entry.pack(anchor='w')

        tracking_directory_frame.pack(pady=10)
        tracking_directory_label.pack(anchor='w')
        tracking_directory_entry.pack(anchor='w')

        naming_conventions_frame.pack(pady=10, fill=tk.X)
        ctd_naming_frame.pack(side=tk.LEFT)
        ctd_naming_label.pack(side=tk.TOP, anchor='w')
        ctd_naming_entry.pack(side=tk.TOP, anchor='w')
        dive_naming_frame.pack(side=tk.RIGHT)
        dive_naming_label.pack(side=tk.TOP, anchor='w')
        dive_naming_entry.pack(side=tk.TOP, anchor='w')

        columns_frame.pack(pady=10, fill=tk.X)
        columns_label.pack(side=tk.LEFT, anchor='w')
        column_combobox.pack(side=tk.RIGHT, anchor='w')


if __name__ == '__main__':
    gui = Gui()
    gui.mainloop()
