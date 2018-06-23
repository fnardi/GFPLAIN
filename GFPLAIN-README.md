# GFPLAIN
Global FloodPLAIN mapping using a geomorphic algorithm

## Getting Started

This short README document will get you started in applying the geomorphic FloodPLAIN mapping algorithm GFPLAIN based on Nardi et al. (2006, 2018) 

### Prerequisites

The GFPLAIN v1.0 is built as a set of phyton scripts prepared to run within a GIS ESRI environment. 
A ESRI toolbox is also provided for providing an easy-to-use interface to run the GFPLAIN model.
Nevertheless, the phyton scripts can be easily adapated to run under GRASS, QGIS or other GIS environemnts.

## Description and Instructions

GFPLAIN is based on three phyton scripts:
1) 01-HYDROBASE.py that is the first preprocessing tool that takes as an input the Digital Elevation Model (DEM) and produce:
- the filled DEM (raster grid)
- the flow direction (raster grid)
- the flow accumulation (drainage area) (raster grid)
- the stream network (raster grid and vector shapefile)

2) 02-GFPLAIN_PREPROCESSING.py that produces further supporting files for running the core GFPLAIN tool

3) GFPLAIN.py that is the core geomorphic floodplain algorithm producing the floodplain raster layer

## References
2006) Nardi F., Vivoni E.R., Grimaldi S., Testing Floodplain Width Scaling Using A Hydrogeomorphic Delineation Method, Water Resources Research, 42, W09409.
2007) Grimaldi S., Nardi F., Di Benedetto F., Istanbulluoglu E., Bras R.L. A physically-based method for removing pits in digital elevation models, Advances in Water Resources, 30,  2151–2158. 
2008) Nardi F., Grimaldi S., Petroselli A., Santini M., Vivoni E.R. Hydrogeomorphic properties of simulated drainage patterns using DEMs: the flat area issue, Hydrological Sciences Journal 53(6). 
2013) Nardi F., Biscarini C., Di Francesco S., Manciola P. Ubertini L., Comparing a large scale DEM-based floodplain delineation algorithm with standard flood maps: the Tiber river basin case study, Journal of Irrigation and Drainage, Volume 62, Issue S2, Pages 11-19.
2018) Nardi F, Morrison RR, Annis A, Grantham TE. Hydrologic scaling for hydrogeomorphic floodplain mapping: Insights into human‐induced floodplain disconnectivity. River Res Applic.;1–11.


## Authors

The GFPLAIN is based on the original AML code developed by Fernando Nardi and conceived together with Salvatore Grimaldi (see Nardi et al., 2006).
The actual phyton version was developed by Antonio Annis adapating and completely reprogramming the original code as in Nardi et al. (2018)
* **Fernando Nardi** - *Original AML code & Theoretical study conception* - [fnardi](https://github.com/fnardi)
* **Salvatore Grimaldi** - *Theoretical study conception* - [Scholar profile](https://scholar.google.it/citations?user=WZ4OQcMAAAAJ&hl=en)
* **Antonio Annis** - *Phyton programming for GFPLAIN v1.0* - [aannis](https://github.com/aannis)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

The GFPLAIN v1.0 algorithms is released under the GNU GPL v3.

## Acknowledgments

* Salvatore Grimaldi contributed to the scientific idea of the hydrogeomorphic floodplain model.
* Enrique Vivoni and Giuliano Di Baldassarre  are also gratefully acknowledged for the scientific support in working on Nardi et al. (2018) work.
