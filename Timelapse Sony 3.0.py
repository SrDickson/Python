import os
import cv2
import shutil
import ffmpeg
from skimage import io
from PIL import Image


# 1.- Eliminación archivos corruptos
# ---------------------------------------------------------------------------------------------------------------------#

# Función para elimnar un archivo
def remove_file(path):
    if not os.remove(path):
        print(f"{path} se ha eliminado correctamente.")
    else:
        print(f"No se ha podido eliminar. {path}")

# Función para retornar el tamaño
def get_file_size(path):
    size = os.path.getsize(path)
    return size


def del_corrupted(path):

    # Franja para delimitar cuando un fichero es corrupto
    size = 0.1

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


# 1.1 Copia de archivos
# ---------------------------------------------------------------------------------------------------------------------#
def copiar_archivos():

    dir_origen = str(input("Introduce la ruta de origen: "))
    dir_destino = str(input("Introduce la ruta de destino: "))

    # Creamos el directorio de destino si no existe
    if not os.path.exists(dir_destino):
        os.makedirs(dir_destino)
        print("El directorio de destino ha sido creado.")

    # Obtenemos la lista de archivos del directorio origen
    archivos = os.listdir(dir_origen)

    # Recorremos la lista de archivos y los copiamos al directorio destino
    for archivo in archivos:
        origen = os.path.join(dir_origen, archivo)
        destino = os.path.join(dir_destino, archivo)
        shutil.copy(origen, destino)

    print("Copia de archivos finalizada.")



# 2.- Timelapse
# ---------------------------------------------------------------------------------------------------------------------#
def verify_image(img_file):
    try:
        img = io.imread(img_file)
    except:
        return False
    return True


def timelapse_vid():
    def create_timelapse(images_folder, output_filename, fps):

        # Obtener la lista de imágenes en el directorio
        images = sorted(os.listdir(images_folder))

        img_path = os.path.join(images_folder, images[0])
        img_size = Image.open(img_path)

        ancho, alto = img_size.size

        # Crear el objeto VideoWriter para guardar el video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_filename, fourcc, fps, (ancho, alto))

        try:
                # Iterar sobre las imágenes y agregarlas al video
                for image in images:

                    image_path = os.path.join(images_folder, image)

                    if image_path.endswith('.jpg') or image_path.endswith('.png'):
                        if verify_image(image_path):
                            frame = cv2.imread(image_path)
                            video.write(frame)

                            print("Se ha añadido la img:", image_path, "al Timelapse.")
                        else:
                            remove_file(image_path)
        except:
            print("Hubo un error procesando el vídeo.")

        # Liberar el objeto VideoWriter
        video.release()


    # Directorio principal que contiene los subdirectorios con las imágenes

    main_dir = str(input("Introduce el directorio que contiene los subdirectorios con imágenes: "))

    del_corrupted(main_dir)

    ds_path = os.path.join(main_dir, '.DS_Store')

    if os.path.exists(ds_path):
        os.remove(ds_path)


    # Tasa de fotogramas para el timelapse
    fps = 25

    # Obtener la lista de subdirectorios
    subdirs = os.listdir(main_dir)

    # Iterar sobre los subdirectorios
    for subdir in subdirs:
        subdir_path = os.path.join(main_dir, subdir)

        # Crear el timelapse para este subdirectorio

        # Caracteríasticas video

        client = main_dir.split(os.path.sep)[1]
        project = main_dir.split(os.path.sep)[2]
        date = main_dir.split(os.path.sep)[3]
        timelapse = subdir

        filename = "{}-{}-{}-{}".format(client, project, date, timelapse)

        nombre_ini_timelapse = filename
        nombre_timelapse = nombre_ini_timelapse + ".mp4"

        output_filename = os.path.join(subdir_path, f"{nombre_timelapse}.mp4")
        create_timelapse(subdir_path, output_filename, fps)

        # Mover el timelapse a la carpeta anterior

        shutil.move(output_filename, main_dir)

    # ruta del directorio actual
    path = main_dir

    # obtenemos todos los subdirectorios del directorio actual
    subdirectories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    # iteramos sobre cada subdirectorio
    for subdir in subdirectories:
        # ruta completa del subdirectorio
        subdir_path = os.path.join(path, subdir)
        # obtenemos la lista de archivos del subdirectorio
        files = os.listdir(subdir_path)
        # iteramos sobre la lista de archivos buscando la primera imagen
        for file in files:
            if file.endswith(".jpg") or file.endswith(".png"):
                # encontramos la primera imagen, así que copiamos el archivo al directorio actual
                shutil.copy(os.path.join(subdir_path, file), path)
                # salimos del loop
                break

# ----------------------------------------------------------------------------------------------------------------------#

    for subdir in subdirs:
        subdir_path = os.path.join(main_dir, subdir)

       # Obtener la lista de imágenes en el subdirectorio
        images = os.listdir(subdir_path)

    # Eliminar todas las imágenes menos la primera y la última
        for i in range(len(images)):

            image_path = os.path.join(subdir_path, images[i])

            if image_path.endswith('.jpg') or image_path.endswith('.png'):
                os.remove(image_path)

# 3.- Exportar Video
# ---------------------------------------------------------------------------------------------------------------------#
def exportar_video():

    menu_video_exit = False

    while menu_video_exit != True:

        print("# ----------------------------------------------------------------------------------------------------#")
        print("Elegiste la opción de exportar video.")
        print("1. Exportar ProRes y H264 en Area Clientes")
        print("2. Exportar solo ProRes")
        print("3. Salir")

        menu_video = int(input("¿Que opción desea ahora? "))

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
            ruta_h264 = nombre_mov + "_H264.mp4"

            command_h264 = f"ffmpeg -i {ruta} -s 3840x2160 -r 25 -c:v libx264 -crf 18 -preset slower -c:a aac -b:a 128k {ruta_h264}"
            os.system(command_h264)

            dropbox = str(input("Introduce la ruta del dropbox: "))
            shutil.move(ruta_h264, dropbox)

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

        if menu_video == 3:
            menu_video_exit = True

# Menu Opciones
# ---------------------------------------------------------------------------------------------------------------------#

menu_exit = False
while menu_exit != True:
    print("# --------------------------------------------------------------------------------------------------------#")
    print("Bienvenido al programa de timelapses de las cámaras Sony.")
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
