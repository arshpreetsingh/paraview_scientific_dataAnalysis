from paraview import simple
from paraview.simple import Show,Render
from paraview.simple import XMLStructuredGridReader,Hide,GetLayout
from paraview.simple import IsoVolume,SetActiveSource,FindSource,IntegrateVariables
from paraview.simple import GetActiveView,SaveScreenshot,GetActiveViewOrCreate,CreateView
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

#fullVolumes_list is used to collect the views after applying threshold values [-1,1] 

fullVolumes_list = []

#calculating IsoVolume

for i in grids_list:
    xMLStructuredGridReader = FindSource(i)
    Hide(xMLStructuredGridReader)
    SetActiveSource(xMLStructuredGridReader) 
    isoVolume = IsoVolume(Input=xMLStructuredGridReader)
    isoVolume.InputScalars = ['POINTS', 'ion_pdf_n_c0']
    isoVolume.ThresholdRange = [3e-05, 1.0]
    isoVolumes_list.append(isoVolume)


#calculating fullVolume
for i in grids_list:
    xMLStructuredGridReader = FindSource(i)
    Hide(xMLStructuredGridReader)
    SetActiveSource(xMLStructuredGridReader) 
    isoVolume = IsoVolume(Input=xMLStructuredGridReader)
    isoVolume.InputScalars = ['POINTS', 'ion_pdf_n_c0']
    isoVolume.ThresholdRange = [-1.0, 1.0]
    fullVolumes_list.append(isoVolume)



# generating PNGs for each view
for i in isoVolumes_list:
    SetActiveSource(i)
    Show(i)
    SaveScreenshot('currentview'+str(i)+'.png')
    Hide(i)

# Applying integrate filter on IsoVolume
for i in isoVolumes_list:
    SetActiveSource(i)
    integrateVariables1 = IntegrateVariables(Input=i)
    Show(integrateVariables1) 


# Follwing Code can be un-commented if need to show different Spread-Sheet Views for IsoVolume
#and fullVolume integrater filters

'''
    renderView1 = GetActiveViewOrCreate('RenderView')
    viewLayout1 = GetLayout()
    spreadSheetView1 = CreateView('SpreadSheetView')
    spreadSheetView1.BlockSize = 50L
    spreadSheetView1.ViewSize = [40,40]
    integrateVariables4Display = Show(integrateVariables1, spreadSheetView1)
'''

#Applying Integrate Fileter on fullVolume

for i in fullVolumes_list:
    SetActiveSource(i)
    integrateVariables1 = IntegrateVariables(Input=i)
    Show(integrateVariables1)

#Showing only one Spreadsheet table, Others Can be selected from Drop-Down List.

SetActiveSource(fullVolumes_list[0])
value_table = IntegrateVariables(Input=i)    
renderView1 = GetActiveViewOrCreate('RenderView')        
viewLayout1 = GetLayout()
spreadSheetView1 = CreateView('SpreadSheetView')
spreadSheetView1.BlockSize = 50L
spreadSheetView1.ViewSize = [40,40]
integrateVariables4Display = Show(value_table, spreadSheetView1)
