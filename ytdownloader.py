import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        
        # URL Entry and Fetch Button
        self.url_frame = ttk.Frame(self.root)
        self.url_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.url_label = ttk.Label(self.url_frame, text="YouTube URL:")
        self.url_label.pack(side=tk.LEFT)
        
        self.url_entry = ttk.Entry(self.url_frame)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
        
        self.fetch_button = ttk.Button(self.url_frame, text="Fetch Info", command=self.fetch_info)
        self.fetch_button.pack(side=tk.LEFT, padx=(5,0))
        
        # Video Info Display
        self.info_label = ttk.Label(self.root, text="")
        self.info_label.pack(padx=10, pady=5, anchor=tk.W)
        
        # Include Video and Audio Checkboxes
        self.include_frame = ttk.Frame(self.root)
        self.include_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.include_video_var = tk.BooleanVar(value=False)
        self.include_video_check = ttk.Checkbutton(
            self.include_frame, text="Include Video", variable=self.include_video_var, command=self.toggle_video_dropdown
        )
        self.include_video_check.pack(side=tk.LEFT, padx=(0,10))
        
        self.include_audio_var = tk.BooleanVar(value=False)
        self.include_audio_check = ttk.Checkbutton(
            self.include_frame, text="Include Audio", variable=self.include_audio_var, command=self.toggle_audio_dropdown
        )
        self.include_audio_check.pack(side=tk.LEFT)
        
        # Video Format Selection
        self.video_frame = ttk.Frame(self.root)
        self.video_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.video_label = ttk.Label(self.video_frame, text="Video Format:")
        self.video_label.pack(side=tk.LEFT)
        
        self.video_var = tk.StringVar()
        self.video_dropdown = ttk.Combobox(self.video_frame, textvariable=self.video_var, state='readonly')
        self.video_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
        self.video_dropdown.config(state=tk.DISABLED)  # Disabled initially
        
        self.video_format_ids = []
        
        # Audio Format Selection
        self.audio_frame = ttk.Frame(self.root)
        self.audio_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.audio_label = ttk.Label(self.audio_frame, text="Audio Format:")
        self.audio_label.pack(side=tk.LEFT)
        
        self.audio_var = tk.StringVar()
        self.audio_dropdown = ttk.Combobox(self.audio_frame, textvariable=self.audio_var, state='readonly')
        self.audio_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
        self.audio_dropdown.config(state=tk.DISABLED)  # Disabled initially
        
        self.audio_format_ids = []
        
        # Save Location
        self.save_frame = ttk.Frame(self.root)
        self.save_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.save_label = ttk.Label(self.save_frame, text="Save Location:")
        self.save_label.pack(side=tk.LEFT)
        
        self.save_entry = ttk.Entry(self.save_frame)
        self.save_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
        self.save_entry.config(state=tk.DISABLED)  # Disabled initially
        
        self.save_button = ttk.Button(self.save_frame, text="Browse", command=self.select_save_location)
        self.save_button.pack(side=tk.LEFT, padx=(5,0))
        self.save_button.config(state=tk.DISABLED)  # Disabled initially
        
        # Download Button
        self.download_button = ttk.Button(self.root, text="Download", command=self.start_download)
        self.download_button.pack(padx=10, pady=5)
        self.download_button.config(state=tk.DISABLED)  # Disabled initially
        
        # Mini Console
        self.console_frame = ttk.Frame(self.root)
        self.console_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.console = tk.Text(self.console_frame, height=10, state=tk.DISABLED)
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Variables
        self.save_path = ""
    
    def fetch_info(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info.get('extractor_key', '').lower() != 'youtube':
                    messagebox.showerror("Error", "Only YouTube videos are supported")
                    return
                
                self.video_format_ids = []
                self.audio_format_ids = []
                video_format_list = []
                audio_format_list = []
                
                for f in info['formats']:
                    if f.get('video_ext') != 'none' or f.get('audio_ext') != 'none':
                        # Determine stream type
                        has_video = f.get('vcodec') != 'none'
                        has_audio = f.get('acodec') != 'none'
                        
                        # Get resolution, framerate, filesize, and codecs
                        resolution = f.get('resolution', 'N/A')
                        framerate = f.get('fps', 'N/A')
                        filesize = f.get('filesize', 0)
                        filesize_mb = f"{filesize / (1024 * 1024):.2f} MB" if filesize else "N/A"
                        video_codec = f.get('vcodec', 'N/A').split('.')[0]  # Simplify codec name
                        audio_codec = f.get('acodec', 'N/A').split('.')[0]  # Simplify codec name
                        
                        # Add to video or audio format list
                        if has_video:
                            video_format_list.append(
                                f"{resolution} | {framerate}fps | {filesize_mb} | {f['ext']} | Video: {video_codec}"
                            )
                            self.video_format_ids.append(f['format_id'])
                        if has_audio:
                            audio_format_list.append(
                                f"{filesize_mb} | {f['ext']} | Audio: {audio_codec}"
                            )
                            self.audio_format_ids.append(f['format_id'])
                
                self.video_dropdown['values'] = video_format_list
                self.audio_dropdown['values'] = audio_format_list
                
                if video_format_list or audio_format_list:
                    self.enable_controls()  # Enable controls after successful fetch
                else:
                    messagebox.showerror("Error", "No valid formats available")
                
                self.info_label.config(text=f"Title: {info.get('title', 'Unknown')}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch video info: {str(e)}")
    
    def toggle_video_dropdown(self):
        """Enable or disable the video dropdown based on the checkbox."""
        if self.include_video_var.get():
            self.video_dropdown.config(state=tk.NORMAL)
        else:
            self.video_dropdown.config(state=tk.DISABLED)
    
    def toggle_audio_dropdown(self):
        """Enable or disable the audio dropdown based on the checkbox."""
        if self.include_audio_var.get():
            self.audio_dropdown.config(state=tk.NORMAL)
        else:
            self.audio_dropdown.config(state=tk.DISABLED)
    
    def enable_controls(self):
        """Enable format selection, save location, and download controls."""
        self.video_dropdown.config(state=tk.NORMAL if self.include_video_var.get() else tk.DISABLED)
        self.audio_dropdown.config(state=tk.NORMAL if self.include_audio_var.get() else tk.DISABLED)
        self.save_entry.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        self.download_button.config(state=tk.NORMAL)
    
    def select_save_location(self):
        self.save_path = filedialog.askdirectory()
        if self.save_path:
            self.save_entry.delete(0, tk.END)
            self.save_entry.insert(0, self.save_path)
    
    def start_download(self):
        if not self.include_video_var.get() and not self.include_audio_var.get():
            messagebox.showerror("Error", "Please select at least one of Video or Audio")
            return
        
        if not self.save_path:
            messagebox.showerror("Error", "Please select a save location")
            return
        
        video_format_id = None
        audio_format_id = None
        
        if self.include_video_var.get():
            selected_video_index = self.video_dropdown.current()
            if selected_video_index == -1 or selected_video_index >= len(self.video_format_ids):
                messagebox.showerror("Error", "Please select a valid video format")
                return
            video_format_id = self.video_format_ids[selected_video_index]
        
        if self.include_audio_var.get():
            selected_audio_index = self.audio_dropdown.current()
            if selected_audio_index == -1 or selected_audio_index >= len(self.audio_format_ids):
                messagebox.showerror("Error", "Please select a valid audio format")
                return
            audio_format_id = self.audio_format_ids[selected_audio_index]
        
        url = self.url_entry.get().strip()
        
        self.fetch_button.config(state=tk.DISABLED)
        self.download_button.config(state=tk.DISABLED)
        
        threading.Thread(target=self.download_video, args=(url, video_format_id, audio_format_id), daemon=True).start()
    
    def download_video(self, url, video_format_id, audio_format_id):
        ydl_opts = {
            'outtmpl': f"{self.save_path}/%(title)s.%(ext)s",
            'progress_hooks': [self.progress_hook],
        }
        
        if video_format_id and audio_format_id:
            # Merge video and audio
            ydl_opts['format'] = f"{video_format_id}+{audio_format_id}"
        elif video_format_id:
            # Download video only
            ydl_opts['format'] = video_format_id
        elif audio_format_id:
            # Download audio only
            ydl_opts['format'] = audio_format_id
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.log_to_console("Starting download...")
                ydl.download([url])
                self.log_to_console("Download completed successfully!")
                messagebox.showinfo("Success", "Download completed successfully")
        except Exception as e:
            self.log_to_console(f"Download failed: {str(e)}")
            messagebox.showerror("Error", f"Download failed: {str(e)}")
        finally:
            self.root.after(0, self.enable_buttons)
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            progress = f"Downloading: {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']}"
            self.log_to_console(progress)
    
    def log_to_console(self, message):
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, message + "\n")
        self.console.config(state=tk.DISABLED)
        self.console.see(tk.END)
    
    def enable_buttons(self):
        self.fetch_button.config(state=tk.NORMAL)
        self.download_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()