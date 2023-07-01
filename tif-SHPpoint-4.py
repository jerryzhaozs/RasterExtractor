import os
import csv
from osgeo import gdal
from osgeo import ogr
from osgeo.gdalconst import *

# 设置输入和输出路径
inputSHP = r'E:\ArcgisFiles\gadm36_2_coundries\Argentinal\Argentinal_gadm36_2_point_Output.shp'  # 点数据文件
InputRasterFolder = r'E:\ArcgisFiles\SPAM_2010\spam2010v2r0_global_phys_area.geotiff'  # 放栅格数据的文件夹
OutputPath = r'E:\ArcgisFiles\SPAM_2010\spam2010v2r0_global_phys_area.geotiff-csv\Argentinal.csv'  # 存放路径

count = 0  # 计数器

# 创建CSV文件并写入标题行
csv_file = OutputPath
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Lon', 'Lat'] + os.listdir(InputRasterFolder))

    # 获取矢量点位的经纬度
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(inputSHP, 0)
    layer = ds.GetLayer()

    xValues = []
    yValues = []

    # 缓存矢量点位数据
    for feature in layer:
        geometry = feature.GetGeometryRef()
        x = geometry.GetX()
        y = geometry.GetY()
        xValues.append(x)
        yValues.append(y)

    # 获取栅格文件列表
    input_folder_list = os.listdir(InputRasterFolder)
    tif_files = [filename for filename in input_folder_list if os.path.splitext(filename)[1] == '.tif']

    # 缓存栅格数据
    ds_cache = {}
    for tif_file in tif_files:
        tif_path = os.path.join(InputRasterFolder, tif_file)
        ds = gdal.Open(tif_path, GA_ReadOnly)
        ds_cache[tif_file] = ds

    # 处理每个点位
    for i in range(len(xValues)):
        row_data = []
        for j in range(len(tif_files)):
            tif_file = tif_files[j]
            ds = ds_cache[tif_file]
            transform = ds.GetGeoTransform()
            xOrigin = transform[0]
            yOrigin = transform[3]
            pixelWidth = transform[1]
            pixelHeight = transform[5]

            x = xValues[i]
            y = yValues[i]
            xOffset = int((x - xOrigin) / pixelWidth)
            yOffset = int((y - yOrigin) / pixelHeight)
            band = ds.GetRasterBand(1)
            data = band.ReadAsArray(xOffset, yOffset, 1, 1)
            value = data[0, 0] * 1.00
            row_data.append(value)

        writer.writerow([xValues[i], yValues[i]] + row_data)

        # 计数器
        count += 1
        if count % 1000 == 0:
            print(count)

# 关闭所有栅格数据集
for ds in ds_cache.values():
    ds = None

print("CSV file created successfully!")
