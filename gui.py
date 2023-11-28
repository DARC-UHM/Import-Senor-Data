import tkinter as tk

from tkinter import filedialog, ttk


class Gui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cruise_number = tk.StringVar(value='')
        self.preset = tk.StringVar(value='EX')
        self.source_folder = tk.StringVar(value='/Volumes/maxarray2/varsadditional')
        self.output_folder = tk.StringVar(value='/Volumes/maxarray2/varsadditional')
        self.title('CTD Process')
        self.minsize(350, 400)
        self.initialize_widgets()

    def go_button_callback(self):
        print('cruise number: {}'.format(self.cruise_number.get()))
        print('preset: {}'.format(self.preset.get()))
        print('source folder: {}'.format(self.source_folder.get()))
        print('output folder: {}'.format(self.output_folder.get()))

    def update_preset(self, preset):
        self.preset.set(preset)

    def get_file_path(self, path):
        file_path = filedialog.askdirectory(initialdir='/Volumes/maxarray2/varsadditional', title='Select a folder')
        path.set(file_path)

    def initialize_widgets(self):
        background = tk.Frame(master=self)

        # cruise and preset frame
        cruise_preset_frame = tk.Frame(master=background)

        # cruise number input
        cruise_frame = tk.Frame(master=cruise_preset_frame)
        cruise_label = tk.Label(master=cruise_frame, text='CRUISE NUMBER', font=('Helvetica', '13', 'bold'))
        cruise_entry = tk.Entry(
            master=cruise_frame,
            width=15,
            textvariable=self.cruise_number,
        )

        # preset input
        preset_frame = tk.Frame(master=cruise_preset_frame)
        preset_label = tk.Label(master=preset_frame, text='PRESET', font=('Helvetica', '13', 'bold'))
        preset_combobox = ttk.Combobox(master=preset_frame, values=['EX', 'NA'], state='readonly', width=10)
        preset_combobox.current(0)
        preset_combobox.bind('<<ComboboxSelected>>', lambda event: self.update_preset(preset_combobox.get()))

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

        # go button
        go_button = tk.Button(
            master=background,
            text='GO',
            width=20,
            height=2,
            font=('Helvetica', '13', 'bold'),
            command=self.go_button_callback,
        )

        # packin
        cruise_preset_frame.pack(pady=(5, 10), fill=tk.X)

        cruise_frame.pack(side=tk.LEFT)
        cruise_label.pack(side=tk.TOP, anchor='w')
        cruise_entry.pack(side=tk.TOP, anchor='w')

        preset_frame.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=20)
        preset_label.pack(side=tk.TOP, anchor='w', pady=(0, 2))
        preset_combobox.pack(side=tk.TOP, anchor='w')

        base_directory_frame.pack(pady=10, fill=tk.X)
        base_directory_label.pack(anchor='w')
        base_directory_entry.pack(anchor='w')
        base_directory_browse_button.pack(anchor='w')

        output_directory_frame.pack(pady=10, fill=tk.X)
        output_directory_label.pack(anchor='w')
        output_directory_entry.pack(anchor='w')
        output_directory_browse_button.pack(anchor='w')

        go_button.pack(pady=(20, 30))

        background.pack(padx=30, pady=20)


if __name__ == '__main__':
    gui = Gui()
    gui.mainloop()
