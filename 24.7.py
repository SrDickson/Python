import os
import sys
import cv2
import shutil
import ffmpeg
from skimage import io


# 1.- Eliminación archivos corruptos
# ---------------------------------------------------------------------------------------------------------------------#

# Función para retornar el tamaño
def get_file_size(path):
    size = os.path.getsize(path)
    return size


# Función para elimnar un archivo
def remove_file(path):
    if not os.remove(path):
        print(f"{path} se ha eliminado correctamente.")
    else:
        print(f"No se ha podido eliminar. {path}")


def del_corrupted():
    # Ruta de los ficheros (Ej. C:/Home/Desktop)
    path = str(input("Introduzca la ruta: "))

    # Franja para delimitar cuando un fichero es corrupto
    size = 1.5

    # Comprobación de que exista la ruta
    if os.path.exists(path):

        size = size * 1024 * 1024
        for root_folder, folders, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root_folder, file)
                if get_file_size(file_path) <= size:
                    remove_file(file_path)
        else:
            if os.path.isfile(path):

                if get_file_size(path) <= size:
                    remove_file(path)
    else:
        print(f"{path} doesn't exist")


# 2.- Timelapse
# ---------------------------------------------------------------------------------------------------------------------#
def verify_image(img_file):
    try:
        img = io.imread(img_file)
    except:
        return False
    return True


def timelapse_vid():
    # Ubicación del directorio
    path = str(input("Introduce la ruta donde estén las imágenes almacenadas: "))
    archivos = sorted(os.listdir(path))
    img_array = []

    # Crear directorio para guardar el timelapse
    ruta = str(input("Introduce la ruta a la que quieres que se exporte el Timelapse: "))
    nombre_directorio = os.path.basename(ruta)

    nomArchivo = archivos[0]
    dirArchivo = path + "/" + str(nomArchivo) # Cambiar la barra a la ruta de windows \\ (tiene que ser doble)
    img = cv2.imread(dirArchivo)
    img_array.append(img)

    # Dimensiones de los frames alto y ancho
    height, width = img.shape[:2]

    # Caracteríasticas video
    nombre_ini_timelapse = nombre_directorio
    nombre_timelapse = nombre_ini_timelapse + ".mp4"
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(nombre_timelapse, codec, 25, (width, height))

    # Leer imagenes
    contador_corruptas = 0
    try:
        for x in range(1, len(archivos)):
            nomArchivo = archivos[x]
            dirArchivo = path + "/" + str(nomArchivo) # Cambiar la barra a la ruta de windows \\ (tiene que ser doble)
            if verify_image(dirArchivo):
                img = cv2.imread(dirArchivo)
                video.write(img)
                print("Se ha añadido la img:", nomArchivo, "al Timelapse.")
            else:
                remove_file(dirArchivo)
                contador_corruptas += 1

        print("He detectado", contador_corruptas, "imagenes corruptas y se han eliminado.")
    except:
        print("Hubo un error al cargar la imagen.")

    # liberar
    video.release()

    # Exportar a la carpeta deseada
    shutil.move(nombre_timelapse, ruta)

    print("Se ha creado el Timelapse correctamente.")


# 3.- Exportar Video
# ---------------------------------------------------------------------------------------------------------------------#
def exportar_video():

    menu_video_exit = False

    while menu_video_exit != True:

        print("# --------------------------------------------------------------------------------------------------------#")
        print("Elegiste la opción de exportar video.")
        print("1. Exportar RAW + ProRes + H264")
        print("2. Exportar RAW + ProRes ")
        print("3. Exportar RAW + H264")
        print("4. Eliminar RAW y exportar ProRes + H264")
        print("5. Eliminar las imágenes de la carpeta")
        print("6. Salir")

        menu_video = int(input("¿Que opción desea ahora? "))

        # 1. Exportar RAW + ProRes + H264
        if menu_video == 1:
            # Transformamos el video
            # Ruta video a transformar
            ruta = str(input("Introduce la ruta del video a transformar: "))

            ruta_exportar = str(input("Introduce la ruta donde quieres exportar los videos: "))

            # Obtener el nombre del directorio
            nombre_directorio = os.path.basename(ruta)
            nombre_mov = os.path.splitext(nombre_directorio)[0]
            command = f"ffmpeg -i {ruta} -c:v prores_ks -profile:v 3 -vendor apl0 -bits_per_mb 8000 -pix_fmt yuv422p10le {nombre_mov}_ProRes.mov"
            os.system(command)

            video = nombre_mov + "_ProRes.mov"

            shutil.move(video, ruta_exportar)

            # Creación del H264

            # Obtener el nombre del archivo sin su extensión
            ruta_h264 = os.path.splitext(ruta)[0] + "_H264.mp4"

            input_vid = ffmpeg.input(ruta)
            vid = (
                input_vid
                .filter('scale', w=1920, h=1080)
                .output(ruta_h264)
                .overwrite_output()
                .run()
            )

        # 2. Exportar RAW + ProRes
        if menu_video == 2:
            # Transformamos el video
            # Ruta video a transformar
            ruta = str(input("Introduce la ruta del video a transformar: "))

            ruta_exportar = str(input("Introduce la ruta donde quieres exportar los videos: "))

            # Obtener el nombre del directorio
            nombre_directorio = os.path.basename(ruta)
            nombre_mov = os.path.splitext(nombre_directorio)[0]
            command = f"ffmpeg -i {ruta} -c:v prores_ks -profile:v 3 -vendor apl0 -bits_per_mb 8000 -pix_fmt yuv422p10le {nombre_mov}_ProRes.mov"
            os.system(command)

            video = nombre_mov + "_ProRes.mov"

            shutil.move(video, ruta_exportar)

        # 3. Exportar RAW + H264
        if menu_video == 3:
            # Creación del H264

            # Obtener el nombre del archivo sin su extensión
            ruta_h264 = os.path.splitext(ruta)[0] + "_H264.mp4"

            input_vid = ffmpeg.input(ruta)
            vid = (
                input_vid
                .filter('scale', w=1920, h=1080)
                .output(ruta_h264)
                .overwrite_output()
                .run()
            )

        # 4. Eliminar RAW y exportar ProRes + H264
        if menu_video == 4:
            # Transformamos el video
            # Ruta video a transformar
            ruta = str(input("Introduce la ruta del video a transformar: "))

            ruta_exportar = str(input("Introduce la ruta donde quieres exportar los videos: "))

            # Obtener el nombre del directorio
            nombre_directorio = os.path.basename(ruta)
            nombre_mov = os.path.splitext(nombre_directorio)[0]
            command = f"ffmpeg -i {ruta} -c:v prores_ks -profile:v 3 -vendor apl0 -bits_per_mb 8000 -pix_fmt yuv422p10le {nombre_mov}_ProRes.mov"
            os.system(command)

            video = nombre_mov + "_ProRes.mov"

            shutil.move(video, ruta_exportar)

            # Creación del H264

            # Obtener el nombre del archivo sin su extensión
            ruta_h264 = os.path.splitext(ruta)[0] + "_H264.mp4"

            input_vid = ffmpeg.input(ruta)
            vid = (
                input_vid
                .filter('scale', w=1920, h=1080)
                .output(ruta_h264)
                .overwrite_output()
                .run()
            )

            remove_file(ruta)

        # 5. Eliminar las imágenes de la carpeta
        if menu_video == 5:
            # Define la ruta de la carpeta que quieres analizar
            folder_path = str(input("Introduce la ruta para eliminar las imagenes: "))

            # Obtén todos los archivos de la carpeta
            files = os.listdir(folder_path)

            # Itera sobre los archivos
            for file in files:
                # Obtén la ruta completa del archivo
                file_path = os.path.join(folder_path, file)

                # Si el archivo es una imagen (tiene una extensión de imagen), entonces bórralo
                if file_path.endswith(".png") or file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
                    os.remove(file_path)

        # 6. Salir
        if menu_video == 6:
            menu_video_exit = True


# Menu Opciones
# ---------------------------------------------------------------------------------------------------------------------#

menu_exit = False
while menu_exit != True:
    print("# --------------------------------------------------------------------------------------------------------#")
    print("Bienvenido al programa de automatización de imágenes.")
    print("1.- Eliminacion de imagenes corruptas y Creación del timelapse.")
    print("2.- Exportar video.")
    print("0.- Salir")

    opcion_menu = int(input("Introduce la opción: "))
    if opcion_menu == 1:  # Eliminación de imágenes corruptas y creación de Timelapse de TODA la carpeta
        timelapse_vid()
    if opcion_menu == 2:  # Exportar Video
        exportar_video()
    if opcion_menu == 0:  # Salida del programa
        print("Gracias por usar este programa. ¡Hasta luego!")
        menu_exit = True
