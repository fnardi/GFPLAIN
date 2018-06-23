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
# HYDROBASE.py
# Description:
# From a given DEM, it:
# -Fills the DEM for hydrologic processing
# -Calculates sinks              - dem_sink
# -Calculates flow direction     - dem_dir
# -Calculates flow accumulation - dem_acc
# -Extracts stream network and stream orders both in grid and shapefile formats dem_ord
#-------------------------------------------

#Import system modules
import sys, string, os, arcpy, math, traceback
from arcpy.sa import *
from datetime import datetime

# Allow output to overwrite...
arcpy.env.overwriteOutput = True

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")


try:

    #INPUTS----------------------------------------------------------------------------------

    DEM = arcpy.GetParameterAsText(0)       # DEM [meters] input grid --> required
    bl_tresh = arcpy.GetParameterAsText(1)  # threshold area [Square kilometers] for stream network

    #Get initial time
    Init_Time=datetime.now()

    #Suffix for stream order layer
    sfx =  bl_tresh
    if "." in bl_tresh:
        sfx = sfx.replace(".","")
        
        
    # CREATING THE FOLDER FOR THE OUTPUTS---------------------------------------------------- 
    DEM_name = os.path.basename(DEM).split('.')[0] #Name of DEM
    DEM_path = os.path.dirname(DEM)                #Path of DEM
    OutPath =DEM_path+"\\HYDROBASE"
    if not os.path.exists(OutPath):
        os.makedirs(OutPath)
       
    #OUTPUT FILES NAME---------------------------------------------------------------------
    #Permanent files   
    FILL = OutPath + "\\"+ DEM_name + '_fill'             #DEM FILLED GRID
    FDIR = OutPath + "\\"+ DEM_name + '_dir'              #FLOW DIRECTION GRID
    FACC = OutPath + "\\"+ DEM_name + '_acc'              #FLOW ACCUMULATION
    CONA = OutPath + "\\"+ DEM_name + '_ca'               #CONTRIBUTING AREA GRID
    SORD = OutPath + "\\"+ DEM_name + '_ord' +sfx         #STREAM ORDER GRID
    SLIN = OutPath + "\\"+ DEM_name + '_bl' +sfx + '.shp' #STREAM LINE SHP
    RES =  OutPath + "\\"+ DEM_name + "_Thresh"+sfx+'_HB_Results.txt'   #RESULTS
    #temporary file names
    STREAM = OutPath+ "\\" + DEM_name + '_stream'         #stream network without order


    #-------------------------START --------------------------------------------------------------

    arcpy.AddMessage('-----------------------------------------')
    arcpy.AddMessage('HYDROBASE CALCULATION')
    
    arcpy.env.extent = DEM
    arcpy.env.mask = DEM
    
    #get the cellsize of DEM grid
    pixelsize = float( arcpy.GetRasterProperties_management (DEM, "CELLSIZEX").getOutput(0) )
    cellarea = pixelsize ** 2
    # define cell size and extension for raster calculator
    arcpy.env.cellSize = pixelsize
            
    #fill the raw DEM
    if not arcpy.Exists(FILL):
        arcpy.AddMessage(' - Computing DEM Filling...')
        outFill = Fill (DEM)
        outFill.save(FILL)
        arcpy.AddMessage(' - Computing Flow Direction...')
        #calculate the new FLOW DIRECTION
        outFD = FlowDirection(FILL) 
        outFD.save(FDIR)
        arcpy.AddMessage(' - Computing Flow Accumulation...')
        outFac = FlowAccumulation(FDIR)
        outFac.save(FACC)               

    #calculate the CONTRIBUTING AREA
    if not arcpy.Exists(CONA):
        outTimes = Raster(FACC) * cellarea 
        outTimes.save(CONA)
    # treshold area in m^2
    bl_tresh = float(bl_tresh) * 1000000

    # Extracting stream network
    arcpy.AddMessage(' - Computing Stream Network...')
    if not arcpy.Exists(SORD):
        outSN = SetNull (CONA, 1,  "VALUE < %f" % bl_tresh )
        outSN.save(STREAM)
        # Calculating stream order grid
        arcpy.AddMessage(' - Computing Stream Order...')
        outSO = StreamOrder(STREAM, FDIR)
        outSO.save(SORD)
        # calculation of stream network shape file
        arcpy.AddMessage(' - Converting Stream to Feature...')
        StreamToFeature(SORD, FDIR, SLIN)
       
    arcpy.Delete_management(STREAM)
    #arcpy.Delete_management(CONA)

    Fin_Time=datetime.now()
    

    ext = arcpy.Describe(DEM).extent
    area = (ext.width * ext.height)/1000000
    IT= Init_Time.strftime('%Y-%m-%d %H:%M:%S')
    FT= Fin_Time.strftime('%Y-%m-%d %H:%M:%S')
    Sim_Time = (Fin_Time - Init_Time)
    import datetime
    Sim_Time = Sim_Time-datetime.timedelta(microseconds=Sim_Time.microseconds)

    R = open(RES, 'w')    
    R.write("{: <25} {: <20}\n".format("DEM name:", DEM_name))
    R.write("{: <25} {: <20}\n".format("Threshold area [km^2]:", "%.2f" %(bl_tresh/1000000)))
    R.write("{: <25} {: <20}\n".format("Resolution [m]:", "%.2f" %pixelsize))
    R.write("{: <25} {: <20}\n".format("Extension [km^2]:", "%.2f" %area))
    R.write("{: <25} {: <20}\n".format("Initial simulation time:", IT))
    R.write("{: <25} {: <20}\n".format("Final simulation time:", FT))
    R.write("{: <25} {: <20}\n".format("Simulation time:", Sim_Time))
    R.close()
            
    arcpy.AddMessage(' ')
    arcpy.AddMessage('HYDROBASE COMPLETED!')

    #---------------------------------------------------------------------------------------------------
   

except: 
    arcpy.AddError(arcpy.GetMessages())
    arcpy.AddMessage(traceback.format_exc()) 
    #print arcpy.GetMessages()
