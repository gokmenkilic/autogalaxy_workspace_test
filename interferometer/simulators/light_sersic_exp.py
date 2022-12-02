"""
Simulator: Sersic
=================

This script simulates `Interferometer` data of a galaxy where:

 - The galaxy's bulge is an `Sersic`.
"""
# %matplotlib inline
# from pyprojroot import here
# workspace_path = str(here())
# %cd $workspace_path
# print(f"Working Directory has been set to `{workspace_path}`")

from os import path
import autogalaxy as ag
import autogalaxy.plot as aplt

""" 
The `dataset_type` describes the type of data being simulated (in this case, `Interferometer` data) and `dataset_name` 
gives it a descriptive name. They define the folder the dataset is output to on your hard-disk:

 - The image will be output to `/autogalaxy_workspace/dataset/dataset_type/dataset_name/image.fits`.
 - The noise-map will be output to `/autogalaxy_workspace/dataset/dataset_type/dataset_name/noise_map.fits`.
 - The psf will be output to `/autogalaxy_workspace/dataset/dataset_type/dataset_name/psf.fits`.
"""
dataset_type = "interferometer"
dataset_name = "light_sersic_exp"

"""
The path where the dataset will be output, which in this case is
`/autogalaxy_workspace/dataset/interferometer/light_sersic_exp`
"""
dataset_path = path.join("dataset", dataset_type, dataset_name)

"""
__Simulate__

For simulating interferometer data of a galaxy, we recommend using a Grid2D object with a `sub_size` of 1. This
simplifies the generation of the galaxy image in real space before it is transformed to Fourier space.
"""
grid_2d = ag.Grid2D.uniform(shape_native=(400, 400), pixel_scales=0.2, sub_size=1)

"""
To perform the Fourier transform we need the wavelengths of the baselines, which we'll load from the fits file below.

By default we use baselines from the Square Mile Array (SMA), which produces low resolution interferometer data that
can be fitted extremely efficiently. The `autogalaxy_workspace` includes ALMA uv_wavelengths files for simulating
much high resolution datasets (which can be performed by replacing "sma.fits" below with "alma.fits").
"""
uv_wavelengths_path = path.join("dataset", dataset_type, "uv_wavelengths")
uv_wavelengths = ag.util.array_1d.numpy_array_1d_via_fits_from(
    file_path=path.join(uv_wavelengths_path, "sma.fits"), hdu=0
)

"""
To simulate the interferometer dataset we first create a simulator, which defines the exposure time, noise levels 
and Fourier transform method used in the simulation.
"""
simulator = ag.SimulatorInterferometer(
    uv_wavelengths=uv_wavelengths,
    exposure_time=300.0,
    noise_sigma=1000.0,
    transformer_class=ag.TransformerDFT,
)

"""
__Plane__

Setup the galaxy with a bulge (elliptical Sersic) for this simulation.

For modeling, defining ellipticity in terms of the `ell_comps` improves the model-fitting procedure.

However, for simulating a galaxy you may find it more intuitive to define the elliptical geometry using the 
axis-ratio of the profile (axis_ratio = semi-major axis / semi-minor axis = b/a) and position angle, where angle is
in degrees and defined counter clockwise from the positive x-axis.

We can use the **PyAutoGalaxy** `convert` module to determine the elliptical components from the axis-ratio and angle.
"""
galaxy = ag.Galaxy(
    redshift=0.5,
    bulge=ag.lp.Sersic(
        centre=(0.0, 0.0),
        ell_comps=ag.convert.ell_comps_from(axis_ratio=0.9, angle=45.0),
        intensity=1.0,
        effective_radius=0.6,
        sersic_index=3.0,
    ),
    disk=ag.lp.Exponential(
        centre=(0.0, 0.0),
        ell_comps=ag.convert.ell_comps_from(axis_ratio=0.7, angle=30.0),
        intensity=0.5,
        effective_radius=1.6,
    ),
)

"""
Use these galaxies to setup a plane, which will generate the image for the simulated interferometer dataset.
"""
plane = ag.Plane(galaxies=[galaxy])

"""
Lets look at the plane`s image, this is the image we'll be simulating.
"""
plane_plotter = aplt.PlanePlotter(plane=plane, grid=grid_2d)
plane_plotter.figures_2d(image=True)

"""
We can now pass this simulator a plane, which creates the image plotted above and simulates it as an
interferometer dataset.
"""
interferometer = simulator.via_plane_from(plane=plane, grid=grid_2d)

"""
Lets plot the simulated interferometer dataset before we output it to fits.
"""
interferometer_plotter = aplt.InterferometerPlotter(interferometer=interferometer)
interferometer_plotter.figures_2d(dirty_image=True)
interferometer_plotter.subplot_interferometer()
interferometer_plotter.subplot_dirty_images()

"""
__Output__

Output the simulated dataset to the dataset path as .fits files.
"""
interferometer.output_to_fits(
    visibilities_path=path.join(dataset_path, "visibilities.fits"),
    noise_map_path=path.join(dataset_path, "noise_map.fits"),
    uv_wavelengths_path=path.join(dataset_path, "uv_wavelengths.fits"),
    overwrite=True,
)

"""
__Visualize__

Output a subplot of the simulated dataset, the image and the plane's quantities to the dataset path as .png files.
"""
mat_plot_2d = aplt.MatPlot2D(output=aplt.Output(path=dataset_path, format="png"))

interferometer_plotter = aplt.InterferometerPlotter(
    interferometer=interferometer, mat_plot_2d=mat_plot_2d
)
interferometer_plotter.subplot_interferometer()
interferometer_plotter.subplot_dirty_images()
interferometer_plotter.figures_2d(visibilities=True)

plane_plotter = aplt.PlanePlotter(plane=plane, grid=grid_2d, mat_plot_2d=mat_plot_2d)
plane_plotter.subplot()

"""
__Plane Output__

Save the `Plane` in the dataset folder as a .json file, ensuring the true light profiles and galaxies
are safely stored and available to check how the dataset was simulated in the future. 

This can be loaded via the method `Plane.from_json`.
"""
plane.output_to_json(file_path=path.join(dataset_path, "plane.json"))

"""
The dataset can be viewed in the folder `autogalaxy_workspace/imaging/light_sersic_exp`.
"""
