from PIL import Image
import numpy as np
import math
import os

MODES = ['linear_encoding_large', 'linear_decoding__group-22', 'linear_decoding__group-22_reruns-2']
SUBJECTS = ['subj01', 'subj02', 'subj03', 'subj04', 'subj05', 'subj06', 'subj07', 'subj08']
LAYERS = ['white', 'pial', 'layerB1', 'layerB2', 'layerB3']
SPACES = ['fssubject', 'fsavg']

HEIGHT = 1024
WIDTH = 2249

    
def create_canvas(scale = 64, partition = 8):
    canvas = Image.new('RGB', (int(WIDTH*scale), int(HEIGHT*scale/partition)))
    return canvas

def open_image(img_id, resized_images=True):
    if resized_images:
        return Image.open('./resized_images/{}.jpg'.format(img_id))
    else:
        return Image.open('./static_data/new_examples/{}.jpg'.format(img_id))

def generate_atlas(mode='linear_encoding_large', subj_id = 'subj01', space = 'fssubject', layer = 'white', scale = 64, partition = 8, resized_images=True):
    top_images_data = np.load('./static_data/top_images_voxel/{0}/{0}__top_images__{1}.npy'.format(mode, subj_id))
    voxel_ids = np.load('./static_data/top_images_voxel/voxel_ids__{}__{}__{}.npy'.format(space, subj_id, layer))
    # mappings = np.load('./static_data/{}/mapping_map.npy'.format(subj_id))
    if space == 'fssubject':
        pts = np.load('./static_data/{}/pt_flat.npy'.format(subj_id))
    elif space == 'fsavg':
        pts = np.load('./static_data/pt_flat.npy')
    

    maxx = 0
    minx = 0
    
    maxy = 0
    miny = 0
    dx = 0
    dy = 0
    
    for i in range(len(pts)):
        if pts[i][0] > maxx:
            maxx = pts[i][0]
        if pts[i][0] < minx:
            minx = pts[i][0]
        if pts[i][1] > maxy:
            maxy = pts[i][1]
        if pts[i][1] < miny:
            miny = pts[i][1]
    scaleX = -0.5 / maxx
    scaleY = 0.5 / maxy
    offsetX = 0.5
    offsetY = 0.5
    
    for i in range(len(pts)):
        pts[i][0] = pts[i][0] * scaleX + offsetX
        pts[i][1] = pts[i][1] * scaleY + offsetY
    
    def paint_canvas_centers_only():
        for p in range(partition):
            canvas = create_canvas(scale, partition)
            if partition == 1:
                add_brain_areas(canvas)
            else:
                print("Only one partition is supported for brain areas")
                raise Exception("Only one partition is supported for brain areas")
            for voxel in centers.keys():    
                center_x = centers[voxel][0]
                center_y = centers[voxel][1]
                if not in_partition(center_x, center_y, p, partition):
                    continue
                # print("Progress: {}/{}".format(vertex, len(pts)))
                center_y -= p/partition
                try:
                    top_img = open_image(top_images_data[voxel][0], resized_images)
                except Exception as e:
                    print("E:{}\t{}:{}".format(e, voxel, top_images_data[voxel][0]))
                # print(vertex_x*WIDTH*scale, vertex_y*HEIGHT*scale)
                try:
                    canvas.paste(top_img, (int(center_x*WIDTH*scale), int((1-center_y)*HEIGHT*scale)))
                except Exception as e:
                    print(voxel, center_x, center_y)
            save_atlas(canvas,mode, subj_id, layer, space, p)
    
    
    def paint_canvas_all_vertices():
        for p in range(partition):
            canvas = create_canvas(scale, partition)
            for vertex in range(len(pts)):    
                vertex_x = pts[vertex][0]
                vertex_y = pts[vertex][1]
                if not in_partition(vertex_x, vertex_y, p, partition) or voxel_ids[vertex]==-1:
                    continue
                # print("Progress: {}/{}".format(vertex, len(pts)))
                vertex_y -= p/partition
                top_img = open_image(top_images_data[voxel_ids[vertex]][0], resized_images) 
                # print(vertex_x*WIDTH*scale, vertex_y*HEIGHT*scale)
                try:
                    canvas.paste(top_img, (int(vertex_x*WIDTH*scale), int(vertex_y*HEIGHT*scale)))
                except Exception as e:
                    print(vertex_x, vertex_y)
            save_atlas(canvas,mode, subj_id, layer, space, p)
    
    def add_brain_areas(canvas:Image):
        foreground = Image.open("./static_data/foreground.png").resize((int(WIDTH*scale), int(HEIGHT*scale)))
        canvas.paste(foreground, (0, 0))
        
    
    centers = find_centers(pts, voxel_ids)
    paint_canvas_centers_only()
    config = open('./atlas/{0}/{1}/{2}/config.txt'.format(mode, subj_id, space), 'w')
    config.write('mode: {0}\nsubject: {1}\nspace: {3}\n\
scale: {4}\nresized_images: {5}\npartitions: {6}\n'.format(space, subj_id, layer, space, scale, resized_images, partition))

def resize_all_images(dim = (64, 64)):
    if not os.path.exists('./resized_images'):
        os.makedirs('./resized_images')
    
    for file in os.listdir('./static_data/new_examples'):
        if file.endswith('.jpg'):
            img_id = file.split('.')[0]
            Image.open('./static_data/new_examples/{}'.format(file)).resize(dim).save('resized_images/{}'.format(file))
            
def in_partition(x, y, p, partition = 8):
    return y >= p/partition and y < (p+1)/partition

def save_atlas(canvas, mode, subj_id, layer, space, p):
    os.makedirs('./atlas/{0}/{1}/{2}'.format(mode, subj_id, space), exist_ok=True)
    canvas.save('./atlas/{0}/{1}/{2}/{1}_{3}_{4}.png'.format(mode, subj_id, space, layer, p))

def find_centers(pts, voxel_ids):
    centers = {}
    unique_voxel_ids = np.unique(voxel_ids)
    for voxel_id in unique_voxel_ids:
        if voxel_id == -1:
            continue
        voxel_pts = pts[voxel_ids == voxel_id]
        center = np.mean(voxel_pts, axis=0)
        centers[voxel_id] = center
    return centers

if __name__ == '__main__':
    
    # resize_all_images()
    # for mode in MODES:
        for subj_id in SUBJECTS:
            for space in SPACES:
                # for layer in LAYERS:
                    generate_atlas(subj_id=subj_id, space=space, layer='pial', mode='linear_decoding__group-22_reruns-2', scale=32, resized_images=False, partition=1)
    
    # generate_atlas(subj_id='subj05', space='fssubject', layer='pial', mode='linear_decoding__group-22_reruns-2', scale=32, resized_images=False, partition=1)
