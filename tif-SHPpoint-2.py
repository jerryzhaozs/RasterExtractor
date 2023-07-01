import os
import csv
from osgeo import gdal
from osgeo import ogr
from osgeo.gdalconst import *

inputSHP = r'E:\ArcgisFiles\gadm36_2_coundries\Bolivia\Bolivia_gadm36_1_fishnet_point.shp'  # 点数据文件
InputRasterFolder = r'E:\ArcgisFiles\SPAM_2010\spam2010v2r0_global_harv_area.geotiff'  # 放栅格数据的文件夹
OutputPath = r'E:\ArcgisFiles\SPAM_2010\spam2010v2r0_global_harv_area.geotiff-xls'  # 存放路径
# inputSHP = r'E:\tiff-shp-xls-test\Argentinal_point_Output.shp'  #点数据文件
# InputRasterFolder = r'E:\tiff-shp-xls-test\spamtest'  #放栅格数据的文件夹

count = 0  # 计数器

# 创建CSV文件并写入标题行
csv_file = r'E:\ArcgisFiles\SPAM_2010\spam2010v2r0_global_harv_area.geotiff-xls\Bolivia.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Lon', 'Lat'] + os.listdir(InputRasterFolder))

    # 获取矢量点位的经纬度
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(inputSHP, 0)
    layer = ds.GetLayer()
    xValues = []
    yValues = []
    feature = layer.GetNextFeature()
    while feature:
        geometry = feature.GetGeometryRef()
        x = geometry.GetX()
        y = geometry.GetY()
        xValues.append(x)
        yValues.append(y)
        feature = layer.GetNextFeature()

    # 获取点位所在像元的栅格值
    input_folder_list = os.listdir(InputRasterFolder)
    tif_files = [filename for filename in input_folder_list if os.path.splitext(filename)[1] == '.tif']
    for i in range(len(xValues)):
        row_data = []
        for j in range(len(tif_files)):
            csvfile = InputRasterFolder + '\\' + tif_files[j]
            ds = gdal.Open(csvfile, GA_ReadOnly)
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

print("CSV file created successfully!")
