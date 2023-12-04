import math
import tkinter as tk
import subprocess

from tkinter import filedialog


class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="Enter text here", placeholder_color="grey", width=20, textvariable=None, *args, **kwargs):
        self.textvar = textvariable if textvariable is not None else tk.StringVar()

        super().__init__(master, textvariable=self.textvar, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        self.default_fg_color = self['fg']
        self.configure(width=width)

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

        self._add_placeholder()

    def _add_placeholder(self, event=None):
        if not self.textvar.get():
            self['fg'] = self.placeholder_color
            self.textvar.set(self.placeholder)

    def _clear_placeholder(self, event=None):
        if self['fg'] == self.placeholder_color:
            self.textvar.set('')
            self['fg'] = self.default_fg_color


class Gui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('CTD Process')
        self.minsize(350, 400)

        self.cruise_number = tk.StringVar(value='')
        self.source_folder = tk.StringVar(value='/Volumes/maxarray2/varsadditional')
        self.output_folder = tk.StringVar(value='/Volumes/maxarray2/varsadditional')

        self.button_text = tk.StringVar(value='GO')
        self.processing_text = tk.StringVar(value='')
        self.background = tk.Frame(master=self)
        self.canvas = tk.Canvas(master=self.background, width=50, height=50)
        self.processing = False

        self.initialize_widgets()

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

    def initialize_widgets(self):
        background = self.background

        # cruise number input
        cruise_frame = tk.Frame(master=background)
        cruise_label = tk.Label(master=cruise_frame, text='CRUISE NUMBER', font=('Helvetica', '13', 'bold'))
        cruise_entry = PlaceholderEntry(
            placeholder='e.g. EX2306',
            master=cruise_frame,
            width=30,
            textvariable=self.cruise_number,
        )

        # base directory input
        base_directory_frame = tk.Frame(master=background)
        base_directory_entry = tk.Entry(
            master=base_directory_frame,
            textvariable=self.source_folder,
            width=30,
        )
        base_directory_browse_button = tk.Button(
            master=base_directory_frame,
            text='Browse',
            command=lambda: self.get_file_path(self.source_folder),
        )
        base_directory_label = tk.Label(
            master=base_directory_frame,
            text='BASE DIRECTORY',
            font=('Helvetica', '13', 'bold'),
        )

        # output directory input
        output_directory_frame = tk.Frame(master=background)
        output_directory_entry = tk.Entry(
            master=output_directory_frame,
            textvariable=self.output_folder,
            width=30,
        )
        output_directory_browse_button = tk.Button(
            master=output_directory_frame,
            text='Browse',
            command=lambda: self.get_file_path(self.output_folder),
        )
        output_directory_label = tk.Label(
            master=output_directory_frame,
            text='OUTPUT DIRECTORY',
            font=('Helvetica', '13', 'bold'),
        )

        # processing status
        processing_status_label = tk.Label(
            master=self.background,
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

        background.pack(padx=30, pady=20)


if __name__ == '__main__':
    gui = Gui()
    gui.mainloop()
