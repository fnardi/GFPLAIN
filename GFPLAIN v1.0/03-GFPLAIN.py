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
#  GFPLAIN.py
#
#  Floodplain delineation tool applying Nardi et al., 2018 method
#  Power law parameters for the GFPLAIN dataset:
#  a= 0.01
#  b= 0.30
#-------------------------------------------

#Import system modules
from __future__ import division
import sys, string, os, arcpy, math, traceback, glob
from arcpy.sa import *
from datetime import datetime

# Allow output to overwrite...
arcpy.env.overwriteOutput = True

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

try:


    #INPUT ARGIMENTS
    path =   arcpy.GetParameterAsText(0)             # Basin path
    a     =  float(arcpy.GetParameterAsText(1))      # Leopold a parameter
    b     =  float(arcpy.GetParameterAsText(2))      # Leopold b parameter
    suff  =  arcpy.GetParameterAsText(3)             # suffix ogf the simulation

    #Get initial time
    Init_Time=datetime.now()    
    
    FPP_path= path + "\\FLOODPLAIN\\PRE"
    #GETTING FILES
    os.chdir(FPP_path)
    Code = glob.glob("*acc")[0][:-4]
    FACC = FPP_path + "\\"+ Code + "_acc"
    FD = FPP_path + "\\"+ Code + "_dir"
    DEM = FPP_path + "\\"+ Code + "_fill"
    ACC_BLC = FPP_path + "\\"+ Code + "_accblc"
    DEM_DIFF = FPP_path + "\\"+ Code + "_diff"
    WAT_SORD = FPP_path + "\\"+ Code + "_wsord.shp"


    #Getting DEM pixelsize
    pixelsize_ob = arcpy.GetRasterProperties_management (DEM, "CELLSIZEX")#get the cellsize of SINK grid
    pixelsize = float( pixelsize_ob.getOutput(0) )
    cellarea = pixelsize ** 2                            #calculate the cell area
    
    #OUTPUT FILES
        
    FP_path = path + "\\FLOODPLAIN"
    if not os.path.exists(FP_path):
        os.makedirs(FP_path)

    WAT_FL = FP_path + "\\"+ Code + "_watfl"
    WAT_HGD = FP_path + "\\"+ Code + "_wathgd"
    FPL_GRD = FP_path + "\\"+ Code + "_fpl"
    FPL_DEPTH = FP_path + "\\"+ Code + suff + "_dep" 
    FPL1 = FP_path + "\\"+ Code + "_fpl1" + suff + ".shp"
    FPL2 = FP_path + "\\"+ Code + "_fp2" + suff + ".shp"
    FPL = FP_path + "\\"+ Code + "_fpl" + suff + ".shp"
    FPL_ORD = FP_path + "\\"+ Code + "_fpl" + suff + "_ord.shp"
    RES =  FP_path + "\\"+ Code + "_"+ suff +'_FPL_Report.txt'   #RESULTS
  
    arcpy.AddMessage('')
    arcpy.AddMessage('-----------------------------------------')
    arcpy.AddMessage('FLOODPLAIN MODULE')
    arcpy.AddMessage(' ')

    arcpy.AddMessage('- Computing water energy levels for each stream network cell...')

    outF = a* (Raster(ACC_BLC)**b)*100
    outF.save(WAT_FL)

    #Assigning thr same stream water energy level for each hydrologically connected cell
    outW = Watershed(FD, WAT_FL,  "VALUE")
    outW.save(WAT_HGD)
    
    #outCon = SetNull (DEM_DIFF, 1,  "VALUE < %f" % bl_tresh )
    arcpy.AddMessage('- Delineating floodplain polygon...')
    #Subtracting the terrain elevation to the water energy levels
    outCon = Con(Raster(DEM_DIFF)<= Raster(WAT_HGD) ,1 )
    outCon.save(FPL_GRD)

    #Filterinf positive values
    outCon = Con(Raster(DEM_DIFF)<= Raster(WAT_HGD) ,(Raster(WAT_HGD)-Raster(DEM_DIFF))/100 )
    outCon.save(FPL_DEPTH)
    
    #Creating the polyogon from the raster
    arcpy.RasterToPolygon_conversion(FPL_GRD, FPL1,"SIMPLIFY")
    arcpy.EliminatePolygonPart_management(FPL1, FPL2, "AREA", cellarea*10000, "", "CONTAINED_ONLY")
    arcpy.Dissolve_management(FPL2, FPL)

    #Assigning the Leopold parameters
    arcpy.AddField_management(FPL, "AREA", "float")
    arcpy.CalculateField_management(FPL, "AREA", "!shape.area@squaremeters!", "PYTHON")
    arcpy.AddField_management(FPL, "a", "float")
    arcpy.CalculateField_management(FPL, "a", "%f" %a, "PYTHON")
    arcpy.AddField_management(FPL, "b", "float")
    arcpy.CalculateField_management(FPL, "b", "%f" %b, "PYTHON")

    #Splitting the floodplain poligon for each stream order
    arcpy.Clip_analysis(WAT_SORD, FPL, FPL_ORD)
    arcpy.AddField_management(FPL_ORD, "AREA", "float")
    arcpy.CalculateField_management(FPL_ORD, "AREA", "!shape.area@squaremeters!", "PYTHON")
    
    arcpy.Delete_management(WAT_FL)
    arcpy.Delete_management(WAT_HGD)
    arcpy.Delete_management(FPL_GRD)
    arcpy.Delete_management(FPL1)
    arcpy.Delete_management(FPL2)

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
    R.write("{: <25} {: <20}\n".format("a Leopold parameter", "%.6f" %a))
    R.write("{: <25} {: <20}\n".format("b Leopold parameter", "%.4f" %b))
    R.write("{: <25} {: <20}\n".format("Resolution [m]:", "%.2f" %pixelsize))
    R.write("{: <25} {: <20}\n".format("Extension [km^2]:", "%.2f" %area))
    R.write("{: <25} {: <20}\n".format("Initial simulation time:", IT))
    R.write("{: <25} {: <20}\n".format("Final simulation time:", FT))
    R.write("{: <25} {: <20}\n".format("Simulation time:", Sim_Time))
    R.close()
    
    arcpy.AddMessage(' ')
    arcpy.AddMessage('FLOODPLAIN  COMPLETED!')
    
except:
     
    arcpy.AddError(arcpy.GetMessages())
    arcpy.AddMessage(traceback.format_exc()) 

