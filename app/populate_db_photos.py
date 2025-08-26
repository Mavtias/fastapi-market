import os
import requests

# Carpeta donde guardar las imágenes
SAVE_DIR = "app/assets/img/uploads"
os.makedirs(SAVE_DIR, exist_ok=True)

# Cantidad de imágenes a descargar
N_IMAGES = 100

# Tamaño de las imágenes
WIDTH, HEIGHT = 400, 300  # puedes ajustar

for i in range(1, N_IMAGES + 1):
    url = f"https://picsum.photos/{WIDTH}/{HEIGHT}?random={i}"
    response = requests.get(url)

    if response.status_code == 200:
        filename = os.path.join(SAVE_DIR, f"fake_{i}.jpg")
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Imagen {i} guardada en {filename}")
    else:
        print(f"⚠️ Error al descargar imagen {i}")

print("🎉 Descarga completa de imágenes Faker")
