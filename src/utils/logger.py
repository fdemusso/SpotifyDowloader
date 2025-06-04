import os
import time

def log_error(message, output_folder):
    """Scrive un messaggio di errore nel file log.txt nella cartella di output."""
    log_file = os.path.join(output_folder, "log.txt")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def has_content(file):
    """Restituisce 1 se il file contiene dati, altrimenti 0."""
    if not os.path.exists(file):
        return 0

    with open(file, "r") as file:
        for line in file:
            if line.strip():
                return 1
    return 3 