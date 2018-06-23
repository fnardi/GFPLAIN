/***************************************************************************
GFPLAIN Global FloodPLAIN mapping using a geomorphic algorithm 
A ESRI-based GIS plugin
-------------------
version                : 1.0
authors                : Fernando Nardi, Antonio Annis
contact                : fernando.nardi@unistrapg.it; antonio.annis@unistrapg.it 
Research group website : http://www.gistar.org
***************************************************************************/
    
/***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************/

#-------------------------------------------
# GFPLAIN - PREPROCESSING
#
# IT GENERATES AUXILIAR LAYERS FOR THE GFPLAIN TOOL
#-------------------------------------------

#Import system modules
import sys, string, os, arcpy, math, traceback, glob, numpy
from arcpy.sa import *
from datetime import datetime

# Allow output to overwrite...
arcpy.env.overwriteOutput = True

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

try:


    #INPUT ARGIMENTS
    DEM =        arcpy.GetParameterAsText(0)     # DEM Name
    Folder =     arcpy.GetParameterAsText(1)     # Folder Name for the results
    Code = arcpy.GetParameterAsText(2)     # Short Name of the Basin
    bl_tresh =  arcpy.GetParameterAsText(3)     # treshold area in km2 for stream network

    #Get initial time
    Init_Time=datetime.now()
    
    suff_ord =  bl_tresh
    if "." in bl_tresh:
        suff_ord = suff_ord.replace(".","")
        
    #GETTING THE NAME OF THE DEM
    DEM_name = os.path.basename(DEM)
    ldn=len(DEM_name)
    #Current working directory
    DEM_path=DEM[:-(ldn+1)]
    pixelsize_ob = arcpy.GetRasterProperties_management (DEM, "CELLSIZEX")#get the cellsize of SINK grid
    pixelsize = float( pixelsize_ob.getOutput(0) )
    cellarea = pixelsize ** 2                            #calculate the cell area
    
    
    #GETTING FILES
    hydrobase_path = DEM_path +"\\HYDROBASE"                             #HYDROBASE PATH
    FILL= hydrobase_path + "\\"+ DEM_name + "_fill"                         #FLOW DIRECTION
    FACC= hydrobase_path + "\\"+ DEM_name + "_acc"                         #FLOW ACCUMULATION
    FD= hydrobase_path + "\\"+ DEM_name + "_dir"                         #FLOW DIRECTION
    SORD  = hydrobase_path + "\\" + DEM_name + "_ord" + suff_ord        #STREAM ORDER
    SL_SB = hydrobase_path + "\\" + DEM_name + "_bl" + suff_ord +".shp" #STREAM LINE

    
    #OUTPUTFOLDER
    FPP_path= DEM_path + "\\" + Folder + "\\FLOODPLAIN\\PRE"
    #Creating the new folder
    if not os.path.exists(FPP_path):
        os.makedirs(FPP_path)
        
    #OUTPUT FILES
    FD1 = FPP_path + "\\"+ Code + "_dir"
    FACC1 = FPP_path + "\\"+ Code + "_acc"
    FILL1 = FPP_path + "\\"+ Code + "_fill"
    DEM_BL = FPP_path + "\\"+ Code + "_bldem"
    DEM_BLcm = FPP_path + "\\"+ Code + "_bldemc"
    DEM_BLWAT = FPP_path + "\\"+ Code + "_blwat"
    DEM_DIFF = FPP_path + "\\"+ Code + "_diff"
    ACC_BL = FPP_path + "\\"+ Code + "_accbl"
    ACC_BLC = FPP_path + "\\"+ Code + "_accblc"
    WAT_ORD = FPP_path + "\\"+ Code + "_word"
    WAT_SORD = FPP_path + "\\"+ Code + "_wsord.shp"
    RES =  FPP_path + "\\"+ Code + "_Thresh"+suff_ord +'_FPL_PRE_Results.txt'   #RESULTS


    #Calculating the area of the cell
    arcpy.env.cellSize = pixelsize
    
    #Extension enviroment
    arcpy.env.extent = DEM
    
    arcpy.AddMessage('')
    arcpy.AddMessage('-----------------------------------------')
    arcpy.AddMessage('GFPLAIN PREPROCESSING')
    arcpy.AddMessage(' ')
 



    #Mask for the calculation
    arcpy.env.mask = DEM     
        
    arcpy.CopyRaster_management(FACC,FACC1)
    arcpy.CopyRaster_management(FILL,FILL1)
    arcpy.CopyRaster_management(FD,FD1)
    
    bl_tresh = float(bl_tresh) * 1000000

    #Flow accumulation on the stream network
    outA = SetNull (FACC, FACC,  "VALUE < %f" % (bl_tresh/cellarea) )
    outA.save(ACC_BL)

    #Contributing area of the stream network
    outAC = Raster(ACC_BL)*cellarea
    outAC.save(ACC_BLC)

    #Elevation of the stream networks in m.a.s.l.
    outBD = SetNull (FACC, FILL,  "VALUE < %f" % (bl_tresh/cellarea) )
    outBD.save(DEM_BL)

    #Elevation of the stream networks in cm.a.s.l.
    outBDc = Raster(DEM_BL) * 100
    outBDc.save(DEM_BLcm)

    #Watershed of the elevation of the stream networks in cm.a.s.l.
    outW = Watershed(FD, DEM_BLcm,  "VALUE")
    outW.save(DEM_BLWAT)

    #Difference between hillsope elevation and the hydrologically connected stream elevation
    outD = Raster(FILL)*100 - Raster(DEM_BLWAT)
    outD.save(DEM_DIFF)

    #Watershed divided per stream orders
    outW = Watershed(FD, SORD,  "VALUE")
    outW.save(WAT_ORD)

    arcpy.RasterToPolygon_conversion(WAT_ORD, WAT_SORD)

    arcpy.Delete_management(ACC_BL)
    arcpy.Delete_management(DEM_BL)
    arcpy.Delete_management(DEM_BLcm)
    arcpy.Delete_management(DEM_BLWAT)

    Fin_Time=datetime.now()
    ext = arcpy.Describe(DEM).extent
    area = (ext.width * ext.height)/1000000
    IT= Init_Time.strftime('%Y-%m-%d %H:%M:%S')
    FT= Fin_Time.strftime('%Y-%m-%d %H:%M:%S')
    Sim_Time = (Fin_Time - Init_Time)
    import datetime
    Sim_Time = Sim_Time-datetime.timedelta(microseconds=Sim_Time.microseconds)

    R = open(RES, 'w')    
    R.write("{: <25} {: <20}\n".format("DEM name:", Code))
    R.write("{: <25} {: <20}\n".format("Threshold area [km^2]:", "%.2f" %(bl_tresh/1000000)))
    R.write("{: <25} {: <20}\n".format("Resolution [m]:", "%.2f" %pixelsize))
    R.write("{: <25} {: <20}\n".format("Extension [km^2]:", "%.2f" %area))
    R.write("{: <25} {: <20}\n".format("Initial simulation time:", IT))
    R.write("{: <25} {: <20}\n".format("Final simulation time:", FT))
    R.write("{: <25} {: <20}\n".format("Simulation time:", Sim_Time))
    R.close()

    
    arcpy.AddMessage(' ')
    arcpy.AddMessage('GFPLAIN PREPROCESSING  COMPLETED!')
except:
     
    arcpy.AddError(arcpy.GetMessages())
    arcpy.AddMessage(traceback.format_exc()) 

