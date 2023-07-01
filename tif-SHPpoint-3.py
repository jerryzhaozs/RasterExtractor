import os
import csv
from osgeo import gdal
from osgeo import ogr
from osgeo.gdalconst import *
import multiprocessing

def process_point(x, y, tif_files, InputRasterFolder):
    row_data = []
    for j in range(len(tif_files)):
        csvfile = os.path.join(InputRasterFolder, tif_files[j])
        ds = gdal.Open(csvfile, GA_ReadOnly)
        transform = ds.GetGeoTransform()
        xOrigin = transform[0]
        yOrigin = transform[3]
        pixelWidth = transform[1]
        pixelHeight = transform[5]

        xOffset = int((x - xOrigin) / pixelWidth)
        yOffset = int((y - yOrigin) / pixelHeight)
        band = ds.GetRasterBand(1)
        data = band.ReadAsArray(xOffset, yOffset, 1, 1)
        value = data[0, 0] * 1.00
        row_data.append(value)
    return row_data

def process_shp_file(inputSHP, InputRasterFolder, OutputPath):
    count = 0
    # 创建CSV文件并写入标题行
    with open(OutputPath, 'w', newline='', encoding='utf-8') as file:
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

        with multiprocessing.Pool() as pool:
            results = [pool.apply_async(process_point, (xValues[i], yValues[i], tif_files, InputRasterFolder)) for i in range(len(xValues))]
            for i, result in enumerate(results):
                row_data = result.get()
                writer.writerow([xValues[i], yValues[i]] + row_data)
                count += 1
                if count % 1000 == 0:
                    print(count)

    print("CSV文件创建完成！")

if __name__ == '__main__':
    inputSHP = r'E:\ArcgisFiles\gadm36_2_coundries\China\china2023_fishnet_point_Output.shp'  # 点数据文件
    InputRasterFolder = r'E:\ArcgisFiles\SPAM_2010\spam2010v2r0_global_phys_area.geotiff'  # 放栅格数据的文件夹
    OutputPath = r'E:\ArcgisFiles\SPAM_2010\spam2010v2r0_global_phys_area.geotiff-csv\china.csv'  # 存放路径
    process_shp_file(inputSHP, InputRasterFolder, OutputPath)
