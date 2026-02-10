import os
from pdf2image import convert_from_path
from PIL import Image, ImageDraw

# --- CONFIGURATION AUTO ---
PDF_PATH = r'C:\Code\random\pdf-cut\Notes_260205_112327.pdf'

# On va chercher le dossier 'bin' dynamiquement pour éviter les erreurs de frappe
base_poppler = r'C:\Code\random\pdf-cut'
found_bin = ""

for root, dirs, files in os.walk(base_poppler):
    if 'pdfinfo.exe' in files:
        found_bin = root
        break

if found_bin:
    print(f" Poppler trouvé ici : {found_bin}")
    POPPLER_PATH = found_bin
else:
    print(" IMPOSSIBLE de trouver pdfinfo.exe dans le dossier !")
    print("Vérifie que tu as bien dézippé le fichier poppler.zip")
    exit()

# --- LA SUITE DU CODE ---
print("Conversion du PDF en image (Patience, ça peut prendre 10s)...")
pages = convert_from_path(PDF_PATH, dpi=300, poppler_path=POPPLER_PATH)

PAGE_NUM = 0 

img = pages[PAGE_NUM]
W, H = img.size

# Paramètres de ta grille
ROWS = 10
COLS = 15          # nombre de coeurs par ligne (à découper)
TOTAL_COLS = 15.8    # largeur réelle de la page en colonnes (1 col de marge à droite)

# La taille d'une cellule est basée sur la largeur totale (15.5 cols)
w_cell = W / TOTAL_COLS
h_cell = H / ROWS

# Dessin de la grille pour vérification
img_debug = img.copy()
draw = ImageDraw.Draw(img_debug)
for c in range(COLS + 1):
    x = c * w_cell
    draw.line([(x, 0), (x, H)], fill="red", width=5)
for r in range(ROWS + 1):
    y = r * h_cell
    draw.line([(0, y), (W, y)], fill="red", width=5)

img_debug.save("debug_grid.png")
print("Fichier 'debug_grid.png' créé. Ouvre-le pour vérifier l'alignement !")

# ==========================================
# 3. DÉCOUPAGE ET SAUVEGARDE
# ==========================================
output_dir = "emojis_extraits"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("Découpage en cours...")
count = 0
# On boucle sur les lignes et les colonnes (on ignore la 15ème si elle est vide/tronquée)
for p in range(8):
    img = pages[PAGE_NUM+p]
    for r in range(ROWS):
        for c in range(COLS): 
            left = c * w_cell
            top = r * h_cell
            right = (c + 1) * w_cell
            bottom = (r + 1) * h_cell
            
            # Crop (gauche, haut, droite, bas)
            emoji = img.crop((left, top, right, bottom))
            emoji = emoji.resize((32, 32), Image.LANCZOS)
            emoji = emoji.point(lambda x: 0 if x < 240 else 255)  # Seuil pour rendre l'image binaire (noir et blanc)
            # Sauvegarde
            emoji.save(f"{output_dir}/emoji_{p+1}{r+1}_{c+1}.png")
            count += 1

print(f"Terminé ! {count} emojis sauvegardés dans le dossier '{output_dir}'.")