# AssetInterdependenceViz
## Description:
In current literature, there is a lack of analysis in analyzing the relationships between different assets of varying asset classes. Consequently, an interactive visualization tool recommending a diverse set of assets is not existent.

Our project focuses on visualizing the interdependencies of various individual assets from varying asset classes such as publicly traded companies, foreign exchange currencies, and commonly traded commodities (oil, gold, silver, grain,banana etc) as a graph. Our project visualizes these interdependencies via a graph in a user-defined graphical user interface with various components.

The goal of our project is to provide users a complex tool to guide investment recommendations. These recommendations are given to users through two main visualizations - a graph network and a time series chart. Each of our two major visualizations are built from different algorithms in the back-end.

## Installation/Execution:
1. The data for our project is too large to upload on GitHub. Download the data from the following link and place the downloaded folder within the src folder.

https://drive.google.com/file/d/12lqB-mwb_YugnkNy4ZxihjLBj8A8_RGN/view?usp=sharing

2. Change directory to the src folder via the command
```
cd src
```
3. Activate virtual environment via the command
```
source env/bin/activate
```
4. Start the application via the command
```
python app.py
```
Note: Pip install any missing modules on your device

5. Open the web application on your browser at the following link:

http://127.0.0.1:8050/
