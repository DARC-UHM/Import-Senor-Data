import tkinter as tk

from tkinter import filedialog, ttk


class Gui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.source_folder = tk.StringVar(value='/Volumes/maxarray2/varsadditional')
        self.output_folder = tk.StringVar(value='/Volumes/maxarray2/varsadditional')
        self.title('CTD Process')
        self.minsize(400, 400)
        self.initialize_widgets()

    def initialize_widgets(self):
        background = tk.Frame(master=self, background='yellow')
        background.pack(fill=tk.BOTH, expand=True)

        # cruise and preset frame
        cruise_preset_frame = tk.Frame(master=background, background='blue')

        # cruise number input
        cruise_frame = tk.Frame(master=cruise_preset_frame)
        cruise_label = tk.Label(master=cruise_frame, text='CRUISE NUMBER', font=('Helvetica', '13', 'bold'))
        cruise_entry = tk.Entry(master=cruise_frame, width=15)

        # preset input
        preset_frame = tk.Frame(master=cruise_preset_frame)
        preset_label = tk.Label(master=preset_frame, text='PRESET', font=('Helvetica', '13', 'bold'))
        preset_combobox = ttk.Combobox(master=preset_frame, values=['EX', 'NA'], state='readonly', width=10)
        preset_combobox.current(0)
        preset_combobox.bind('<<ComboboxSelected>>', lambda event: print(preset_combobox.get()))

        # base directory input
        base_directory_frame = tk.Frame(master=background)
        base_directory_input_frame = tk.Frame(master=base_directory_frame)
        base_directory_entry = tk.Entry(
            master=base_directory_input_frame,
            textvariable=self.source_folder,
            width=30,
        )
        base_directory_browse_button = tk.Button(
            master=base_directory_input_frame,
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
        output_directory_input_frame = tk.Frame(master=output_directory_frame)
        output_directory_entry = tk.Entry(
            master=output_directory_input_frame,
            textvariable=self.output_folder,
            width=30,
        )
        output_directory_browse_button = tk.Button(
            master=output_directory_input_frame,
            text='Browse',
            command=lambda: self.get_file_path(self.output_folder),
        )
        output_directory_label = tk.Label(
            master=output_directory_frame,
            text='OUTPUT DIRECTORY',
            font=('Helvetica', '13', 'bold'),
        )

        # go button
        go_button = tk.Button(master=background, text='Go', width=20, height=2)

        # packin
        cruise_preset_frame.pack(pady=10, expand=True, fill=tk.X)

        cruise_frame.pack(side=tk.TOP, anchor='w')
        cruise_label.pack(side=tk.TOP, anchor='w')
        cruise_entry.pack(side=tk.TOP, anchor='w')

        preset_frame.pack(side=tk.TOP, padx=10)
        preset_label.pack(side=tk.TOP, anchor='w')
        preset_combobox.pack(side=tk.TOP, anchor='w')

        base_directory_frame.pack(pady=10)
        base_directory_label.pack(side=tk.TOP, anchor='w')
        base_directory_input_frame.pack()
        base_directory_entry.pack(side=tk.LEFT)
        base_directory_browse_button.pack(side=tk.RIGHT)

        output_directory_frame.pack(pady=10)
        output_directory_label.pack(side=tk.TOP, anchor='w')
        output_directory_input_frame.pack()
        output_directory_entry.pack(side=tk.LEFT)
        output_directory_browse_button.pack(side=tk.RIGHT)

        go_button.pack(pady=(10, 30))

        background.pack(padx=20, pady=20)

    def get_file_path(self, path):
        file_path = filedialog.askdirectory(initialdir='/Volumes/maxarray2/varsadditional', title='Select a folder')
        path.set(file_path)


if __name__ == '__main__':
    gui = Gui()
    gui.mainloop()
