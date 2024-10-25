import numpy as np
import os
import easyocr 
from capture_image import ScreenshotSelector
import tkinter as tk
from tkinter import scrolledtext
from spellchecker import SpellChecker 
import torch  
import re  
import sys  
import keyboard

class OCRApplication:
    def __init__(self, master):
        self.master = master
        self.master.title("Aplicación OCR")
        self.texto_final = ""
        self.master.minsize(400, 400) 
        self.spell_checker = SpellChecker(language='es')

        self.gpu_disponible = torch.cuda.is_available()
        print(f"GPU disponible: {self.gpu_disponible}")

        self.ocr_reader = easyocr.Reader(['es'], gpu=self.gpu_disponible)

  
        self.resultado_texto = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=20)
        self.resultado_texto.pack(padx=10, pady=10)

        self.boton_frame = tk.Frame(master)
        self.boton_frame.pack(side=tk.BOTTOM, pady=10)
        self.btn_capturar = tk.Button(self.boton_frame, text="Capturar", command=self.capture_and_process, height=2, width=20)
        self.btn_capturar.pack(side=tk.LEFT, padx=5)
        
        keyboard.add_hotkey('ctrl + q', self.capture_and_process)

        self.btn_limpiar = tk.Button(self.boton_frame, text="Limpiar", command=self.clean_text, height=2, width=20)
        self.btn_limpiar.pack(side=tk.LEFT, padx=5)

        self.btn_copiar = tk.Button(self.boton_frame, text="Copiar", command=self.copy_text, height=2, width=20)
        self.btn_copiar.pack(side=tk.LEFT, padx=5)

        self.resultado_texto.bind("<KeyRelease>", self.check_spelling)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def capture_and_process(self):
        try:
            self.master.withdraw()
            screenshot_selector = ScreenshotSelector()

            if screenshot_selector.image_np is not None:
                self.process_image(screenshot_selector.image_np)

            self.master.deiconify()
            self.copy_text()

        except Exception as e:
            print(f"Error al capturar o procesar la imagen: {e}")
            self.master.destroy()  

    def process_image(self, imagen_np):
        result_easy = self.ocr_reader.readtext(imagen_np, detail=0)

        self.texto_final = " ".join(palabra.strip() for palabra in result_easy)

        self.resultado_texto.delete(1.0, tk.END)
        self.resultado_texto.insert(tk.END, self.texto_final)

        self.check_spelling()

    def check_spelling(self, event=None):
        cursor_pos = self.resultado_texto.index(tk.INSERT)

   
        texto = self.resultado_texto.get(1.0, tk.END).upper().strip()

        self.resultado_texto.delete(1.0, tk.END)
        self.resultado_texto.insert(tk.END, texto)


        self.resultado_texto.tag_remove("error", 1.0, tk.END)

        palabras = re.findall(r'\b\w+\b', texto)  

     
        for palabra in palabras:
            if palabra not in self.spell_checker:
                palabra = palabra.replace("  ", " ").replace(";", ",")
 
                start_index = texto.index(palabra)
                end_index = start_index + len(palabra)

     
                self.resultado_texto.tag_add("error", f"1.{start_index}", f"1.{end_index}")

        self.resultado_texto.tag_config("error", foreground="red")


        self.resultado_texto.mark_set(tk.INSERT, cursor_pos)

    def copy_text(self):

        texto = self.resultado_texto.get(1.0, tk.END).rstrip('\n') 
        self.master.clipboard_clear()
        self.master.clipboard_append(texto)

    def clean_text(self):
      
        self.resultado_texto.delete(1.0, tk.END)
        self.master.clipboard_clear()

    def on_closing(self):
        self.master.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApplication(root)
    root.mainloop()

