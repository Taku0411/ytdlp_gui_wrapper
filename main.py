# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
from tkinter.ttk import Progressbar
from tkinter import messagebox
from tkinter import scrolledtext
import pyperclip
from yt_dlp import YoutubeDL
import subprocess
import sys
import os
import getpass
import threading
import ffmpeg
import time
class Input(tk.Frame):
    def __init__(self, master=None):
        #variables
        self.setting_directory = os.path.expanduser('~/Desktop')
        self.output_directory = self.setting_directory
        self.vid_title = "none"
        tk.Frame.__init__(self, master)
        master.geometry('400x850')
        self.frame_input = tk.LabelFrame(master, text='①　URL入力')
        self.frame_download = tk.LabelFrame(master, text='②　画質選択')
        frame_direc_dl = tk.Frame(master)
        self.frame_seve_directory = tk.LabelFrame(frame_direc_dl, text='③　保存先選択', height=frame_direc_dl.winfo_height())
        self.frame_start = tk.LabelFrame(frame_direc_dl, text='④　ダウンロード')
        self.init()
        self.frame_input.pack()
        self.frame_download.pack()
        self.frame_seve_directory.pack(side=tk.LEFT,expand=True)
        self.frame_start.pack(expand=True, fill=tk.BOTH)
        frame_direc_dl.pack()
        self.pack()
        # video lists
        self.mp4_fmts = []
        self.webm_fmts = []
        self.audio_fmts = []
    def init(self):
        self.input()
        self.set_directory()
        self.set_name()
        self.download_button()
    def input(self):
        self.input_entry = tk.Entry(self.frame_input)
        paste_button = tk.Button(self.frame_input)
        paste_button.configure(text='paste', command=self.paste)
        self.input_button = tk.Button(self.frame_input)
        self.input_button.configure(text='OK', command=self.set_url_callback)
        self.input_entry.bind('<Return>', self.set_url_callback)
        self.input_entry.focus_set()
        self.input_entry.pack()
        paste_button.pack()
        self.input_button.pack()
    def set_url_callback(self, *event):
        self.analyse_gui()
        self.set_url()
        self.tktop.destroy()
    def analyse_gui(self):
        self.tktop = tk.Toplevel()
        self.tktop.wm_geometry('300x100')
        self.tktop.configure()
        self.tktop.update()
        lb = tk.Label(self.tktop, text='動画解析中...').pack()
        self.tktop.update()
    def set_url(self, *event):
        input_link = self.input_entry.get()
        if(input_link == ""):
            showerror(title='エラー', message='urlが正しくありません。')
        else:
            self.yt_url = input_link
            widgets = self.frame_download.winfo_children()
            if widgets:
                for child in widgets:
                    # print(child)
                    child.destroy()
            # try:
            self.extract_info_wapper(url=input_link)
            self.setMovieList()
            # except :
            #     showerror(title='エラー', message='urlが正しくありません。')
            #     self.input_entry.delete(0, tk.END)
    def extract_info_wapper(self, url):
        self.mp4_fmts = []
        self.webm_fmts = []
        self.audio_fmts = []
        ydl_opts = {}
        ydl = YoutubeDL(ydl_opts)
        info = ydl.extract_info(url=url, download=False)
        formats = info["formats"]
        self.vid_title = info["title"]

        duration = self.get_duration(info)
        for fmt in formats:
            # audio only
            if(fmt["resolution"] == "audio only" and fmt["format_note"] != "storyboard") and "m3u8" not in fmt["protocol"]:
                self.audio_fmts.append(fmt)
            # webm
            elif "vp9" in fmt["vcodec"]:
                self.webm_fmts.append(fmt)
            # mp4
            elif "avc1" in fmt["vcodec"]:
                self.mp4_fmts.append(fmt)
        max_size = 0
        max_size2 = 0
        for a_fmt in self.audio_fmts:
            if(a_fmt["filesize"] > max_size and a_fmt["ext"] == "m4a"):
                self.for_audio_m4a = a_fmt
                max_size = a_fmt["filesize"]
        for a_fmt in self.audio_fmts:
            if(a_fmt["filesize"] > max_size and a_fmt["ext"] == "webm"):
                self.for_audio_webm = a_fmt
                max_size = a_fmt["filesize"]

    # get seconds
    def get_duration(self, info):
        for fmt in info["formats"]:
            if fmt["format_note"] == "storyboard":
                if fmt["fragments"][0]["duration"]:
                    return int(fmt["fragments"][0]["duration"])
        print("error")

    def setMovieList(self):
        self.all_list = self.mp4_fmts + self.webm_fmts + self.audio_fmts
        webm_index = len(self.mp4_fmts)
        audio_index = webm_index + len(self.webm_fmts)
        title = tk.Message(self.frame_download, text='タイトル:' + self.vid_title, width=350)
        title.pack(fill=tk.BOTH,expand=1)
        self.choosen_format_index = tk.IntVar()
        self.choosen_format_index.set(-1)
        tk.Label(self.frame_download, text="mp4（推奨）").pack(side=tk.TOP, anchor=tk.N)
        counter = 0
        for fmt in self.all_list:
            if(counter == webm_index):
                tk.Label(self.frame_download, text="webm（非推奨）").pack()
            if(counter == audio_index):
                tk.Label(self.frame_download, text="音声").pack()
            resolution = fmt["resolution"]
            # print(fmt)
            # print(fmt["filesize"], fmt["filesize_approx"])
            filesize = round(int(fmt["filesize"]) / 1024 / 1024)
            vcodec = fmt["video_ext"]
            #print(format, amount, vcodec)
            #print(self.module.return_link(data))
            box = tk.Radiobutton(self.frame_download)
            # print(self.module)
            box.configure(text='画質：{}　サイズ:{}Mb'.format(resolution, filesize), variable=self.choosen_format_index,
                            value=self.all_list.index(fmt))
            box.pack()
            counter += 1
    def paste(self):
        self.input_entry.delete('0', 'end')
        self.input_entry.insert(tk.END, pyperclip.paste())
    def set_directory(self):
        self.output_link = tk.StringVar()
        self.output_entry = tk.Entry(self.frame_seve_directory)
        self.output_entry.bind('<Return>', self.set_folder)
        self.output_entry.pack()
        self.output_entry.insert(tk.END, self.setting_directory)
        choose_folder_button = tk.Button(self.frame_seve_directory)
        choose_folder_button.configure(text='フォルダを選択', command=self.choose_folder_gui)
        choose_folder_button.pack()
    def set_name(self):
        set_title = tk.Label(self.frame_seve_directory, text='保存名を入力（省略可）')
        set_title.pack()
        self.title_entry = tk.Entry(self.frame_seve_directory)
        self.title_entry.pack()
    def choose_folder_gui(self):
        output_link = askdirectory()
        if self.output_entry != '':
            self.output_entry.delete(0, tk.END)
        self.output_entry.insert(tk.END, output_link)
        self.set_folder()
    def set_folder(self, *args):
        self.output_directory = self.output_entry.get()
        if os.path.exists(self.output_directory):
            return self.output_directory
        else:
            return False
    def check_download_is_ok(self):
        self.buttton_no = self.choosen_format_index.get()
        folder = self.set_folder()
        self.title_output = self.title_entry.get()
        if self.title_output == '':
            self.title_output = self.movie_title
        # print(self.title_output)
        if folder:
            if self.buttton_no != -1:
                return True
            else:
                tk.messagebox.showerror(title='エラー', message='画質を選択してください')
                return False
        elif folder == '':
            tk.messagebox.showerror(title='エラー', text='保存先を入力してください')
            return False
        else:
            tk.messagebox.showerror(title='エラー', message='ファイル保存先が存在しません')
            return False
    def download_button(self):
        dl_button = tk.Button(self.frame_start, text='ダウンロード', command=self.download_file)
        dl_button.pack(anchor=tk.CENTER)
    def download_file(self):
        tktop = tk.Toplevel()
        tktop.wm_geometry('300x100')
        tktop.configure()
        tk.Label(tktop, text='ダウンロード中...').pack()
        tktop.update()
        fmt_index = self.choosen_format_index.get()
        # print(self.all_list[fmt_index])
        fmt = self.all_list[fmt_index]
        #check download file is audio or video
        fmt_string = ""
        if(fmt["audio_ext"] == "none"):
            vid_ext = fmt["format_id"]
            if(fmt["video_ext"] == "webm"):
                audio_ext = self.for_audio_webm["format_id"]
            if (fmt["video_ext"] == "mp4"):
                audio_ext = self.for_audio_m4a["format_id"]
            fmt_string = "{}+{}".format(vid_ext, audio_ext)
        else:
            fmt_string = "{}".format(fmt["format_id"])
        
        # print(self.output_directory)
        # ydl_ops = {"format" : "{}".format(fmt_string), "--merge-output-format": "mp4", "--paths": str(self.output_directory)}
        commands = "yt-dlp -f {} --paths {} {}".format(fmt_string, self.output_directory, self.yt_url)
        # print(commands)
        subprocess.run(commands, shell=True)
        # ydl = YoutubeDL(ydl_ops)
        # thread1 = threading.Thread(target=ydl.download, args = (self.yt_url, ))
        # thread1.start()
        # ydl.download(url_list=self.yt_url)
        tktop.destroy()
    
win = tk.Tk()
app = Input(master=win)
app.mainloop()
