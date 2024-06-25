import csv
import requests
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys

def check_link(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return False

def process_links(csv_file_path, link_column_name, progress_var, progress_bar, root):
    broken_links = []

    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Verificar se a coluna existe
        if link_column_name not in reader.fieldnames:
            messagebox.showerror("Testador de Links", f"ERRO: O arquivo CSV não contém a coluna '{link_column_name}'.")
            root.quit()
            return
        
        total_links = sum(1 for _ in reader)
        csvfile.seek(0)  # Reset the reader to the beginning of the file
        next(reader)  # Skip the header row

        if total_links == 0:
            messagebox.showerror("Testador de Links", "ERRO: O arquivo CSV não contém registros.")
            root.quit()
            return

        for i, row in enumerate(reader, start=1):
            link = row[link_column_name]
            if not check_link('https://' + link):
                broken_links.append(link)
            progress_var.set((i / total_links) * 100)
            progress_bar.update()

    if broken_links:
        messagebox.showinfo("Testador de Links", f"Foram encontrados {len(broken_links)} links quebrados.")
        save_broken_links(broken_links)
    else:
        messagebox.showinfo("Testador de Links", "Nenhum link quebrado encontrado.")

    root.quit()

def save_broken_links(broken_links):
    if getattr(sys, 'frozen', False):
        # Estamos executando como um aplicativo congelado pelo PyInstaller
        exe_path = os.path.dirname(sys.executable)
    else:
        # Estamos executando o script diretamente
        exe_path = os.path.dirname(os.path.abspath(__file__))

    output_file = os.path.join(exe_path, "broken_links.txt")

    try:
        with open(output_file, 'w') as f:
            for link in broken_links:
                f.write(link + '\n')
        messagebox.showinfo("Testador de Links", f"Links quebrados salvos em: {output_file}")
    except Exception as e:
        print(f"Erro ao salvar links quebrados: {e}")

def main():
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal
    csv_file_path = filedialog.askopenfilename(
        title="Selecione o arquivo CSV",
        filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
    )

    if not csv_file_path:
        messagebox.showerror("Erro", "Nenhum arquivo selecionado.")
        return

    root.deiconify()  # Mostra a janela principal
    root.title("Testador de Links")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100)
    progress_bar.pack(fill=tk.X, expand=1)

    link_column_name = 'linkfot'
    threading.Thread(target=process_links, args=(csv_file_path, link_column_name, progress_var, progress_bar, root)).start()

    root.mainloop()

if __name__ == "__main__":
    main()
