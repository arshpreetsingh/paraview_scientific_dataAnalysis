from paraview import simple
from paraview.simple import Show,Render
from paraview.simple import XMLStructuredGridReader,Hide
from paraview.simple import IsoVolume,SetActiveSource,FindSource
from paraview.simple import GetActiveView,SaveScreenshot,GetActiveViewOrCreate
import os

simple._DisableFirstRenderCameraReset()

# List of all files for analysis
os.chdir('/home/metal-machine/para/bin/')

files_list = ['phase_space_vars_0.vts',
              'phase_space_vars_500.vts', 
              'phase_space_vars_1000.vts']

# Reading all files
vts_reader = (XMLStructuredGridReader(FileName=i) for i in files_list)

renderView1 = GetActiveViewOrCreate('RenderView')

# Showing all files in Pipeline Browser
grid_readers_list = (Show(i,renderView1) for i in vts_reader)

# initilization of grids_list
grids_list =[]
count = 1

# creation grid_reader_list to find all the available GridReaders in Paraview Pipeline Browser

for i in grid_readers_list:
    grids_list.append('XMLStructuredGridReader'+str(count))
    count+=1
    
#isoVolumes_list is used to collect the views after applying IsoVolume filter on all Shapes 

isoVolumes_list = []

for i in grids_list:
    xMLStructuredGridReader = FindSource(i)
    Hide(xMLStructuredGridReader)
    SetActiveSource(xMLStructuredGridReader) 
    isoVolume = IsoVolume(Input=xMLStructuredGridReader)
    isoVolume.InputScalars = ['POINTS', 'ion_pdf_n_c0']
    isoVolume.ThresholdRange = [3e-05, 1.0]
    isoVolumes_list.append(isoVolume)

# generating PNGs for each view
for i in isoVolumes_list:
    SetActiveSource(i)
    Show(i)
    SaveScreenshot('currentview'+str(i)+'.png')
Hide(i)
