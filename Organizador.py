import os
from io import BytesIO
import cv2
import shutil
import ffmpeg
from skimage import io
from PIL import Image
from datetime import datetime
import exifread


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

#----------------------------------------------------------------------------------------------------------------------#

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

    input("Presiona Enter para continuar...")

# ----------------------------------------------------------------------------------------------------------------------#
# 3. Organizar imágenes

# 3. Organizar imágenes

def ordenar_obras():
    directory = input("Ingresa el directorio con las imágenes: ")

    # Crea una lista para almacenar las fechas de creación de las imágenes
    image_times = []

    # Recorre todos los archivos en el directorio
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        with open(file_path, 'rb') as image_file:
            image = BytesIO(image_file.read())
            try:
                tags = exifread.process_file(image)
                date_time = tags.get('EXIF DateTimeOriginal')
                if date_time:
                    date_time = date_time.values
                    date_time = datetime.strptime(date_time, '%Y:%m:%d %H:%M:%S')
                    image_times.append((date_time, file_path))
                else:
                    print(f"La imagen {filename} no tiene fecha de creación en los metadatos")
            except Exception as e:
                print(f"{filename} no es una imagen válida")

    # Ordena la lista de acuerdo a la fecha de creación de las imágenes
    image_times.sort(key=lambda x: x[0])

    # Contador para contar el numero de carpetas creadas
    counter = 1
    # Crea una variable para almacenar el tiempo de la imagen anterior
    prev_time = None
    # Crea una variable para almacenar el nombre de la carpeta actual
    new_folder = None
    # Recorre la lista de imágenes ordenadas
    for time, file_path in image_times:
        # Si la imagen anterior no es None y la diferencia de tiempo entre la imagen anterior y la actual es mayor a 3 minutos
        if prev_time and (time - prev_time).total_seconds() > 1800:
            # Crea una nueva carpeta
            new_folder = f"Obra{counter}"
            os.makedirs(os.path.join(directory, new_folder))
            counter += 1
        # Si la variable new_folder aun no se ha definido
        elif not new_folder:
            new_folder = f"Obra{counter}"
            os.makedirs(os.path.join(directory, new_folder))
            counter += 1

        # Mueve la imagen a la carpeta actual
        shutil.move(file_path, os.path.join(directory, new_folder))
        prev_time = time
        print("Se ha movido la imagen: ", file_path, "a", os.path.join(directory, new_folder))

    #----------------------------------------------------------------------------------------------------------------------#

    root_dir = directory

    # Recorre todos los subdirectorios en el directorio raíz
    for subdir in os.listdir(root_dir):
        directory = os.path.join(root_dir, subdir)
        # Verifica si el subdirectorio es un directorio
        if os.path.isdir(directory):
            # Crea una lista para almacenar las fechas de creación de las imágenes
            image_times = []

            # Recorre todos los archivos en el subdirectorio
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                with open(file_path, 'rb') as image_file:
                    image = BytesIO(image_file.read())
                    try:
                        tags = exifread.process_file(image)
                        date_time = tags.get('EXIF DateTimeOriginal')
                        if date_time:
                            date_time = date_time.values
                            date_time = datetime.strptime(date_time, '%Y:%m:%d %H:%M:%S')
                            image_times.append((date_time, file_path))
                        else:
                            print(f"La imagen {filename} no tiene fecha de creación en los metadatos")
                    except Exception as e:
                        print(f"{filename} no es una imagen válida")

            # Ordena la lista de acuerdo a la fecha de creación de las imágenes
            image_times.sort(key=lambda x: x[0])

            # Contador para contar el numero de carpetas creadas
            counter = 1
            # Crea una variable para almacenar el tiempo de la imagen anterior
            prev_time = None
            # Crea una variable para almacenar el nombre de la carpeta actual
            new_folder = None
            # Recorre la lista de imágenes ordenadas
            for time, file_path in image_times:
                # Si la imagen anterior no es None y la diferencia de tiempo entre la imagen anterior y la actual es mayor a 3 minutos
                if prev_time and (time - prev_time).total_seconds() > 30:
                    # Crea una nueva carpeta
                    new_folder = f"Timelapse{counter}"
                    os.makedirs(os.path.join(directory, new_folder))
                    counter += 1
                # Si la variable new_folder aun no se ha definido
                elif not new_folder:
                    new_folder = f"Timelapse{counter}"
                    os.makedirs(os.path.join(directory, new_folder))
                    counter += 1

                # Mueve la imagen a la carpeta actual
                shutil.move(file_path, os.path.join(directory, new_folder))
                prev_time = time
                print("Se ha movido la imagen: ", file_path, "a", os.path.join(directory, new_folder))

    input("Presiona Enter para continuar...")


# 4. Exportar videos
# ----------------------------------------------------------------------------------------------------------------------#

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

            input("Presiona Enter para continuar...")

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

            input("Presiona Enter para continuar...")

        if menu_video == 3:
            menu()

# Camara Sony A7II
# ----------------------------------------------------------------------------------------------------------------------#
def camara_timelapse():

    os.system("clear")
    print("Menú Cámara Timelapse: ")
    print("#----------------------------------------------------------------------------------------------------#")
    print("1.- Organizar imágenes.")
    print("2.- Crear Timelapses.")
    print("3.- Exportar.")
    print("4.- Volver.")

    menu_A7II = str(input("Introduce la opción: "))

    if menu_A7II == "1":
        ordenar_obras()
        camara_timelapse()
    if menu_A7II == "2":
        timelapse_vid()
        camara_timelapse()
    if menu_A7II == "3":
        exportar_video()
        camara_timelapse()
    if menu_A7II == "4":
        menu()

# Camara Sony
# ----------------------------------------------------------------------------------------------------------------------#
def camara_video():

    os.system("clear")
    print("Menú Cámara Video: ")
    print("#----------------------------------------------------------------------------------------------------#")
    print("1.- Organizar imágenes.")
    print("2.- Volver.")

    menu_camara2 = str(input("Introduce la opción: "))

    if menu_camara2 == "1":
        ordenar_obras()
        camara_video()
    if menu_camara2 == "2":
        menu()

# Dron
# ----------------------------------------------------------------------------------------------------------------------#
def dron():

    os.system("clear")
    print("Menú Dron: ")
    print("#----------------------------------------------------------------------------------------------------#")
    print("1.- Organizar imágenes.")
    print("2.- Volver.")

    menu_dron = str(input("Introduce la opción: "))

    if menu_dron == "1":
        ordenar_obras()
        dron()
    if menu_dron == "2":
        menu()


# Menu
# ----------------------------------------------------------------------------------------------------------------------#
def menu():
    os.system("clear")
    print("Bienvenido al menu de organización de tarjetas SD")
    print("1.- Crear Copia de Seguridad")
    print("2.- Cámara Timelapse.")
    print("3.- Cámara Video.")
    print("4.- Dron.")
    print("5.- Salir.")

    menu_opcion = str(input("Introduce la opcion: "))

    if menu_opcion == "1":
        copiar_archivos()
        menu()
    if menu_opcion == "2":
        camara_timelapse()
        menu()
    if menu_opcion == "3":
        camara_video()
        menu()
    if menu_opcion == "4":
        dron()
        menu()
    if menu_opcion == "5":
        exit()

menu()
