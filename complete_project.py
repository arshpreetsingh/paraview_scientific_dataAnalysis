from paraview import simple
from paraview.simple import Show,Render,Arrow,GetActiveSource,GetActiveCamera
from paraview.simple import XMLStructuredGridReader,Hide,GetLayout, Delete,RenameSource
from paraview.simple import IsoVolume,SetActiveSource,FindSource,IntegrateVariables
from paraview.simple import GetActiveView,SaveScreenshot,GetActiveViewOrCreate,CreateView
import os
from paraview.servermanager import Fetch
import itertools
from scipy.optimize import fsolve


simple._DisableFirstRenderCameraReset()

# List of all files for analysis
os.chdir('/home/metal-machine/para/bin/')

files_list = ['phase_space_vars_0.vts','phase_space_vars_500.vts','phase_space_vars_1000.vts']

# Reading all files
vts_reader = (XMLStructuredGridReader(FileName=i) for i in files_list)

renderView1 = GetActiveViewOrCreate('RenderView')

# Showing all files in Pipeline Browser
grid_readers_list = (Show(i,renderView1) for i in vts_reader)

# initilization of grids_list
grids_list =[]

#generating iso_volumes list counter from pipeline browser
#example: iso_volumes_list=['IsoVolume1','IsoVolume2','IsoVolume3']
iso_volumes_list=[]
count = 1

# creation grid_reader_list to find all the available GridReaders in Paraview Pipeline Browser

for i in grid_readers_list:
    grids_list.append('XMLStructuredGridReader'+str(count))
    iso_volumes_list.append('IsoVolume'+str(count))
    count+=1
def create_arrow(tip_radius,tip_length,shaft_radius,tip_resolution,shaft_resolution,*position_list):
    """ Function returns arrow as per the required arguments"""
    
    '''arrow method can be called as follows:
    create_arrow(0.04,0.15,0.008,12,12)
    To Hide arrow as the requirement function can be assigned to vaiable
 
    p = create_arrow(0.04,0.15,0.008,12,12)
    Delete(p)
   To set position we can pass position list in function argument
   
   position_list = [2,2,2]
   create_arrow(0.04,0.15,0.008,12,12,*position_list)
    '''
    p=Arrow()
    p.TipRadius = tip_radius
    p.TipLength = tip_length
    p.ShaftRadius = shaft_radius
    p.TipResolution = tip_resolution
    p.ShaftResolution = shaft_resolution
    dr=simple.GetDisplayProperties()
   # dr.DiffuseColor = [1.0, 0.0, 0.0]
   # dr.Origin = [0.0, 0.0, 0.0]
    dr.Position = position_list  # tried with [0,0,0], same
   # dr.Scale = [0.02, 0.02, 0.02]

    arrow1Display = Show(p)

    arrow1Display.ColorArrayName = [None, '']
    arrow1Display.DiffuseColor = [0.6666666666666666, 0.0, 0.0] # change solid color
    return arrow1Display

#fullVolumes_list is used to collect the views after applying threshold values [-1,1] 

fullVolumes_list = []


#calculating fullVolume

for i in grids_list:
    xMLStructuredGridReader = FindSource(i)
    Hide(xMLStructuredGridReader)
    SetActiveSource(xMLStructuredGridReader) 
    isoVolume = IsoVolume(Input=xMLStructuredGridReader)
    isoVolume.InputScalars = ['POINTS', 'ion_pdf_n_c0']
    isoVolume.ThresholdRange = [-1.0, 1.0]
    fullVolumes_list.append(isoVolume)


def get_integral(input_value):
    SetActiveSource(input_value)
    value_table = IntegrateVariables(Input=input_value)    
    p = Fetch(value_table)
    
    # getting value of full volume

    vtkarray = p.GetPointData().GetArray("ion_pdf_n_c0")
    for index in range(0, vtkarray.GetNumberOfTuples()):
        m = vtkarray.GetValue(index)
    Delete(value_table)
    del value_table
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
    


def findIntersection(fun1,constant,x0,args=''):
    def new_func(x,*args):
        return fun1(x, *args) - constant
    return fsolve(new_func, x0, args=args)


def integrator_func(isovalue,volume):
    """ Function takes input as minimiun iso_volume value and returns 
    new integral filte"""

    isoVolume = FindSource(volume)
    SetActiveSource(isoVolume) 
    isoVolume.ThresholdRange = [isovalue, 1.0]
    integrate_variable = IntegrateVariables(Input=isoVolume)
    p = Fetch(integrate_variable)
    Delete(integrate_variable)
    del integrate_variable
    # returning volume after updating lower iso limit    
    vtkarray = p.GetPointData().GetArray("ion_pdf_n_c0")
    for index in range(0, vtkarray.GetNumberOfTuples()):
        m = vtkarray.GetValue(index)
    
    return m


def get_iso_value1():
    for i,j,k in itertools.izip(fullVolumes_list,grids_list,iso_volumes_list):
        p = get_integral(i)
        desiredI_1 = 0.25*p
        m = get_values(j)
        minval,maxval=m[0],m[1]
        isovalue1=findIntersection(integrator_func,desiredI_1,0.5*(maxval-minval)+minval,args=k)
        yield isovalue1

# Again updating the iso_volumes to full volume:

for i in iso_volumes_list:
    isoVolume = FindSource(i)
    SetActiveSource(isoVolume) 
    isoVolume.ThresholdRange = [-1.0, 1.0]

def get_iso_value2():
  
    for i,j,k in itertools.izip(fullVolumes_list,grids_list,iso_volumes_list):
        p = get_integral(i)
        desiredI_2 = 0.75*p
        m = get_values(j)
        minval,maxval=m[0],m[1]
        isovalue2=findIntersection(integrator_func,desiredI_2,0.5*(maxval-minval)+minval,args=k)
        yield isovalue2

# creating inner volumes for iso_value1
inner_volumes = []
for i,j in itertools.izip(grids_list,get_iso_value1()):
    GridReader = FindSource(i)
    Hide(GridReader)
    SetActiveSource(GridReader) 
    isoVolume = IsoVolume(Input=GridReader)
    isoVolume.InputScalars = ['POINTS', 'ion_pdf_n_c0']
    isoVolume.ThresholdRange = [j, 1.0]
    inner_volumes.append(isoVolume)


# need to update threashold value to get isovalue2 correctly
for i in iso_volumes_list:
    isoVolume = FindSource(i)
    SetActiveSource(isoVolume) 
    isoVolume.ThresholdRange = [-1.0, 1.0]


# creating outer volumes for iso_value2
outer_volumes = []
for i,j in itertools.izip(grids_list,get_iso_value2()):
    GridReader = FindSource(i)
    Hide(GridReader)
    SetActiveSource(GridReader) 
    isoVolume = IsoVolume(Input=GridReader)
    isoVolume.InputScalars = ['POINTS', 'ion_pdf_n_c0']
    isoVolume.ThresholdRange = [j, 1.0]
    outer_volumes.append(isoVolume)


# deleting the list of not required volumes
for i in iso_volumes_list:
    isoVolume = FindSource(i)
    Delete(isoVolume)    
    del isoVolume

# calling function to create arrow with specified values
position_list = [2,2,2]
create_arrow(0.04,0.15,0.008,12,12,*position_list)
# Showing, Rendering and Saving PNGs for inner and outer volumes

for i,j in itertools.izip(inner_volumes,outer_volumes):
    
    # Applying color ans opacity properties to inner volumes
    SetActiveSource(i)
    isoVolume = GetActiveSource()
    RenameSource('inner volume', isoVolume)
    display = Show(i,renderView1)
    display.ColorArrayName = [None, '']
    display.ScalarOpacityUnitDistance = 0.048839259427929105
    display.Opacity = 0.55
    display.DiffuseColor = [0.6666666666666666, 0.6666666666666666, 0.4980392156862745]
    
    # Applying color ans opacity properties to outer volumes
    SetActiveSource(j)
    isoVolume2 = GetActiveSource()
    RenameSource('outer volume', isoVolume2)
    display2 = Show(j,renderView1)
    display2.ColorArrayName = [None, '']
    display2.ScalarOpacityUnitDistance = 0.06374128525398871
    display2.Opacity = 0.3
    display2.DiffuseColor = [1.0, 0.6666666666666666, 0.4980392156862745]

    # Settings camera properties and saving into PNGs
    camera = GetActiveCamera()
    camera.SetPosition(-1.95,-2,-1.55)    
    camera.SetFocalPoint(0.5,0,0.45)
    camera.SetViewUp(0,0,-1)
    camera.SetViewAngle(30)
    renderView1.Background = [1.0, 1.0, 1.0]
    
    # saving current view into PNG file, Resolution can be increased using 
    # higher magnification value, for "magnification=4" it will produce PNG image
    # of 1800x1800 pixels(Which results much better default resolution)
     
    SaveScreenshot('currentview'+str(i)+'.png', magnification=4, quality=100)
    Hide(i)
Hide(j) 
