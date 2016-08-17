from paraview import simple
from paraview.simple import Show,Render,Arrow
from paraview.simple import XMLStructuredGridReader,Hide,GetLayout
from paraview.simple import IsoVolume,SetActiveSource,FindSource,IntegrateVariables
from paraview.simple import GetActiveView,SaveScreenshot,GetActiveViewOrCreate,CreateView
import os
from paraview.servermanager import Fetch

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


# Function to create arrow:

def create_arrow(tip_radius,tip_length,shaft_radius):
    """ Function returns arrow as per the required arguments"""
    
    p=Arrow()
    p.TipRadius = tip_radius
    p.TipLength = tip_length
    p.ShaftRadius = shaft_radius
    arrow1Display = Show(p)
    arrow1Display.ColorArrayName = [None, '']
    arrow1Display.DiffuseColor = [0.6666666666666666, 0.0, 0.0] # change solid color
    return arrow1Display
 
#isoVolumes_list is used to collect the views after applying IsoVolume filter on all Shapes 

isoVolumes_list = []

#fullVolumes_list is used to collect the views after applying threshold values [-1,1] 

fullVolumes_list = []

#calculating IsoVolume 
'''
for i in grids_list:
    xMLStructuredGridReader = FindSource(i)
    Hide(xMLStructuredGridReader)
    SetActiveSource(xMLStructuredGridReader) 
    isoVolume = IsoVolume(Input=xMLStructuredGridReader)
    isoVolume.InputScalars = ['POINTS', 'ion_pdf_n_c0']
    isoVolume.ThresholdRange = [3e-05, 1.0]
    isoVolumes_list.append(isoVolume)
'''

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


'''
for i in isoVolumes_list:
    SetActiveSource(i)
    Show(i)
    SaveScreenshot('currentview'+str(i)+'.png')
    Hide(i)
'''


def get_integral(input_value):
    SetActiveSource(input_value)
    value_table = IntegrateVariables(Input=input_value)    
    renderView1 = GetActiveViewOrCreate('RenderView')        
    viewLayout1 = GetLayout()
    spreadSheetView1 = CreateView('SpreadSheetView')
    spreadSheetView1.BlockSize = 50L
    spreadSheetView1.ViewSize = [40,40]
    integrateVariables4Display = Show(value_table, spreadSheetView1)
    p = Fetch(value_table)
    
    # getting value of full volume

    vtkarray = p.GetPointData().GetArray("ion_pdf_n_c0")
    for index in range(0, vtkarray.GetNumberOfTuples()):
        m = vtkarray.GetValue(index)

    return m

def get_values(grid_reader):
    
    """Return range of variable for given grid_reader value from grids_list[]"""
    values_list = []
    p = FindSource(grid_reader)
    pd = p.PointData
    for index in range(pd.GetNumberOfArrays()):
        # appending all the range values of variabels in one list 
        values_list.append(pd.GetArray(index).GetRange())
    # returning range values only for pdf_n_c0
    return values_list[0]
    

from scipy.optimize import fsolve

def findIntersection(fun1,fun2,x0):
    return fsolve(lambda x : fun1(x) - fun2(x),x0)

def integrator_func(isovalue):
    """ Function takes input as minimiun iso_volume value and returns 
    new integral filte"""
    for i in fullVolumes_list:
        pq=FindSource(i) 
        isoVolume = IsoVolume(Input=pq)
        isoVolume.InputScalars = ['POINTS', 'ion_pdf_n_c0']
        isoVolume.ThresholdRange = [isovalue, 1.0]
        integrate_variable = IntegrateVariables(Input=isoVolume)
        p = Fetch(integrate_variable)
    
    # returning volume after updating lower iso limit    
        vtkarray = p.GetPointData().GetArray("ion_pdf_n_c0")
        for index in range(0, vtkarray.GetNumberOfTuples()):
            m = vtkarray.GetValue(index)

    return m

p = get_integral(i)
desiredI_1 = 0.25*p
desiredI_2=0.75*p


# following code can be used to call each function individually
#print get_integral(fullVolumes_list[0])
#print integrator_func(-1)
#min_v,max_v = get_values(-2.8954487633103226e-06)
#print min_v,max_v

''' this code print desired integral 1 and 2  for each shape
'''

m = get_values(grids_list[0])
minval,maxval=m[0],m[1]
isovalue1 = findIntersection( integrator_func, lambda x: desiredI_1, 0.5*(maxval-minval)+minval )

#print min_value,max_value

#isovalue1 = findIntersection( integrator_fun1111111c, lambda x: desiredI_1, 0.5*(maxval-minval)+minval )

'''
isovalue1 = findIntersection( integrator_func, lambda x: desiredI_1, 0.5*(maxval-minval)+minval )
print isovalue1
isovalue2 = findIntersection( integrator_func, lambda x: desiredI_2, 0.5*(maxval-minval)+minval )
print isovalue2
'''
#print min_value,max_value

#calling create_arrow() function:


#create_arrow(0.04,0.15,0.008)

#create_arrow(tip_radius='0.04',tip_length='0.15',shaft_radius='0.008')

#isovalue1 = findIntersection(2,3,0.5*(maxval-minval)+minval)
#isovalue2 =  findIntersection(integrator_func(-2.8954487633103226e-06),desiredI_1, 0.5*(max_v-min_v)+min_v) 
