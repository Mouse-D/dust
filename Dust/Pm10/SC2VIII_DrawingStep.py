'''
directions:
    @param filename: nc文件所在的路径+完整文件名
    @param dataName: nc文件要画的数据的变量名称
    @param lonMin: 画布的经度左边界
    @param lonMax: 画布的经度右边界
    @param latMin: 画布的纬度下边界
    @param latMax: 画布的纬度上边界
    @param cbarMax: 颜色条的最大值
    @param savePath: 画出图来存放的路径+完整文件名
    @return:
2021.6.16
'''
from matplotlib.colors import ListedColormap
import os
from datetime import datetime
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeat
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import shapefile
from cartopy.crs import PlateCarree, LambertConformal
from cartopy._crs import Geodetic
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.axes_grid1.colorbar import colorbar
from netCDF4 import Dataset
from matplotlib import ticker, cm
import matplotlib as mpl
import cartopy.io.shapereader as shpreader


def DrawingPro(inputfiles,filename,lonsName,latsName,dataName,lonMin,lonMax,latMin,latMax,cbarticks,savePath,step,FigSize,glFlag,pow,shpFlag,dpi):
    plt.rcParams.update({'font.size':15})
    if shpFlag==0:
        FigSize=(13.3,16)
    fig = plt.figure(figsize=FigSize)
    # ax = fig.add_subplot(111)
    plt.xticks([])
    plt.yticks([])
    plt.axis('off')
    fh = Dataset(filename, mode='r')
    lons = fh.variables[lonsName][:]
    lats = fh.variables[latsName][:]
    data = fh.variables[dataName][:]
    data[data <= step] = np.nan
    # data=data*10**3
    # data=data*10**3
    data = data * (10 ** pow)
    # data[data==0]=np.nan
    fh.close()
    # fh = Dataset("‪G:/00 SC/geoJudge/ningxiaJudge.nc", mode='r')
    fh = Dataset("/himawari/spq/input/judge/ningxiaJudge.nc", mode='r')
    ningxia = fh.variables['pm2_5'][:]
    fh.close()
    data=data*ningxia
    nx=data.shape[1]
    ny=data.shape[0]
    proj = ccrs.PlateCarree()
    # proj = ccrs.LambertAzimuthalEqualArea()
    ax = fig.subplots(1, 1, subplot_kw={'projection': proj})
    if shpFlag==1:
        # chinaProvince = shpreader.Reader('./Data_ipynb/Ningxia.dbf').geometries()
        chinaProvince = shpreader.Reader('/himawari/spq/input/Data_ipynb/Ningxia.dbf').geometries()
        # chinaProvince = shpreader.Reader('./Data_ipynb/宁夏界线.dbf').geometries()
        ##绘制省界
        ax.add_geometries(chinaProvince, proj,facecolor='none', edgecolor='black',linewidth=5,zorder = 2,alpha=0.4)
        # china = shpreader.Reader('./Data_ipynb/Ningxia.dbf').geometries()
        # ##绘制国界
        # ax.add_geometries(china, proj, facecolor='none', edgecolor='grey', linewidth=2, zorder=2,alpha=0.8)

        #分支处理
        if inputfiles[6:8]=="xx":
            PK_time = inputfiles[0:6]
            PK_time = datetime.strptime(PK_time, '%Y%m')
            PK_time = PK_time.strftime("%Y{Y}%m{m}").format(Y='年', m='月')
        elif inputfiles[8:10]=="xx":
            PK_time = inputfiles[0:8]
            PK_time = datetime.strptime(PK_time, '%Y%m%d')
            PK_time = PK_time.strftime("%Y{Y}%m{m}%d{d}").format(Y='年', m='月', d='日')
        else:
            PK_time = inputfiles[0:10]
            PK_time = datetime.strptime(PK_time, '%Y%m%d%H')
            PK_time = PK_time.strftime("%Y{Y}%m{m}%d{d}%H:00").format(Y='年', m='月', d='日')
        if step==0:
            stringtitle="地面PM10浓度地图(微克/立方米)"+PK_time
        else:
            stringtitle = "地面PM10浓度热点地图(＞"+str(step)+"微克/立方米)"+ PK_time

        ax.set_title(stringtitle,
                     fontproperties="SimHei",
                     fontsize=37, weight='black',color='black',loc ='left',
                     y=0.96,
                     backgroundcolor='white',
                     horizontalalignment='left')#x=0.2,
    extent = [lonMin,lonMax,latMin,latMax]
    ax.set_extent(extent, proj)
    if glFlag==1:
        gl = ax.gridlines(crs=proj, draw_labels=True,
          linewidth=0.6, color='k', alpha=0.5, linestyle='--')

        gl.xlabels_top = False
        gl.ylabels_right = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER


    # cmap = ListedColormap(["#F6FBB0", "#FDBF6F", "#9E0142"])
    norm = mpl.colors.Normalize(vmin=cbarticks[0], vmax=cbarticks[-1])
    im = ax.pcolormesh(lons, lats, data,transform=proj,cmap=cm.Spectral_r,norm=norm,zorder=1)#cm.Spectral_r
    # position=fig.add_axes([0.7, 0.17, 0.15, 0.012])
    # position=fig.add_axes([0.2, 0.05, 0.5, 0.012])
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)

    if shpFlag == 1:
        cb=plt.colorbar(im,aspect=35,shrink=0.6)#aspect左右缩进，越小越宽
        # font = {'family': 'Arial',
        #         'color': 'black',
        #         'weight': 'normal',
        #         'size': 16,
        #         }
        # cb.set_label('×10${^{-1}}$', fontdict=font)

        # # font = {'size': 14,}
        cb.set_ticks(cbarticks)
        cb.ax.tick_params(labelsize=26)
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1.1, hspace=0, wspace=0)

    # plt.rcParams['font.sans-serif'] = ['Times New Roman']
    plt.rcParams['font.sans-serif'] = ['Arial']
    # plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
    ax.margins(0, 0)
    ax.outline_patch.set_visible(False)
    plt.savefig(savePath,dpi=dpi)#图外透明：transparent=True
    # plt.show()
    # plt.cla()
    plt.close()
    plt.close("all")
    import gc
    del lons, lats, data,im
    gc.collect()
