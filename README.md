<!-- Project Header -->

<br />
<p align="center">
  <a href="https://github.com/charles-havener/chaos_game">
    <img src="Icon\icon.ico" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Chaos Game Visualizer</h3>

  <p align="center">
    A visualization tool for chaos game parameter adjustments
    <br />
    <a href="https://imgur.com/gallery/jqMogwz"><strong>4000x4000 Example Output Images »</strong></a>
    <br />
  </p>
</p>

<!-- Table of Contents-->

## Table of Contents

- [About the Project](#about-the-project)
- [How it works](#how-it-works)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Requirements](#requirements)
  - [Running](#running)
- [Further Restrictions and Explanations](#further-restrictions-and-explanations)
  - [Reduction](#reduction)
  - [Rule Sets](#rule-sets)
  - [Compression](#compression)
  - [Rotation](#rotation)
  - [Probability](#probability)
  - [Output Options](#output)
- [License](#license)

<!-- About the Project -->

## About The Project

<br>
<p align="center">Inspired by <a href="https://www.youtube.com/watch?v=kbKtFN71Lfs&list=PLt5AfwLFPxWLDKmnxLg8477hrxY33LL6q&index=7&t=0s&app=desktop">this video</a> uploaded by Numberphile</p>
<p align="center">Adjust parameters to create unexpected output from chaos, with the option to save a high resolution of your creations and discoveries.
</p>
<p align="center">
  <img src="Images\preview.png" alt="Preview" width="900">
</p>
<p align="center"></p>
<br>
<p align="center">Examples of line reduction method</p>
<p align="center">
  <img src="Images\line_reduction.png" alt="Line Examples" width="900">
</p>
<p align="center"></p>
<br>
<p align="center">Examples of points reduction method</p>
<p align="center">
  <img src="Images\points_reduction.png" alt="Points Examples" width="900">
</p>
<p align="center"></p>
<br>

<p align="center">Built with 
<a href="https://www.python.org/downloads/release/python-378/">Python 3.7.8</a>, 
<a href="https://kivy.org/#home">Kivy</a>, 
<a href="https://datashader.org/">Datashader</a>, 
<a href="https://numba.pydata.org/">Numba (Jit)</a>, 
and more</p>

<br>

## How it Works

### 1. Constructing the data set

1. We begin by constructing the vertices of a regular polygon.
2. Start at any arbitrary initial point in the xy plane. (the output is the same no matter which point is chosen. Here, vertex 0 of the constructed polygon will always be chosen for consistent output sizing).
3. At each step a vertex is randomly chosen (further constrictions can be applied with [rule sets](#rule-sets) and [probabilites](#probability))
4. A new point is added by moving halfway from the chosen vertex to the current point (further adjusted with [compression](#compression)).
5. The newly plotted point becomes the current point and steps [3, 5] are repeated until N points are created

### 2. Aggregation (Reduction)

With such a large number of points, we'll run into some serious plotting issues just mapping each point to its (x,y) location, namely overplotting and oversaturation.

To better visualize our output, we are overlaying our (x,y) points on a canvas (our image) and binning the data points into groups based on which pixel of the canvas they would fall onto. The data is further categorized in these bins by the outer vertex that was chosen when they were initially created. The value of these bins determines the 'brightness' of each pixel in our final image.

### 3. Color Mapping

From here the bins are flushed through a histogram equalization function which makes sure each 'brightness' level is equally represented throughout the image.

Finally based on the colormap chosen, each outer vertex is assigned a color. The subcategories of each bin relate to the outer vertex chosen for the initial data points within the bin and are mutually exclusive. The color assigned to the pixel for each bin is a composition of the colors relative to the size of the bins subcategories.

<br>

<!-- Getting Started -->

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

- Create a Python 3.7.8 virtual environment _(will **not** work on most recent python version)_

```sh
$ virtualenv -p <path to Python 3.7.8> venv_chaos_game
```

### Requirements

- Install the required packages in the created virtual environment after cloning the repo

```sh
$ pip install -r requirements.txt
```

### Running

- Run the visualization tool with the following:

```sh
$ python main.py
```

<br>

<!-- Explanation of Restrictions that can be Applied -->

## Further Restrictions and Explanations

<br>

### Reduction

Which data shader reduction method should be used.

- Line: Computes a reduction by pixel, mapping data to pixels as one or more lines.
- Points: Computes a reduction by pixel, mapping data to pixels as points.

  <br>

### Rule Sets

Sets restrictions on the outer vertex that will be selected next.

- Standard:
  - The standard rule set. Any outer vertex can be chosen to draw the next point from.
- Not Prev (Not previous):
  - Any out vertex can be chosen other than the one that was chosen in the last step. (i.e cannot choose any outer vertex consectutively)
- Not CCW (Not counter-clockwise):
  - Can be any of the outer vertices other than the one directly CCW to the previously chosen one.
- Not CW (Not clockwise):
  - Can be any of the outer vertices other than the one directly CW to the previously chosen one.
- Not Opposite:
  - Can not be the point directly opposite of the previously chosen vertex. Has no effect when **V** is odd.
- Not Adj (Not adjacent):
  - The chosen vertex cannot be a vertex adjacent to the previously chosen vertex.
- Not Adj Prev2 (Not adjacent to either of the previous 2 vertices chosen):
  - The chosen vertex cannot be a vertex adjacent to either of the previously chosen vertices.
- Not Adj Prev2 Same (Not adjacent to the previous vertex if the previous 2 chosen vertices were the same):
  - The chosen vertex cannot be a vertex adjacent to the previous vertex, if the previous two vertices were the same.

### Compression

Can be uniquely applied to each outer vertex. Defaults to 2 if left empty or input is invalid

The ratio of the distance traveled to create the new point from the randomly chosen vertex. A value of **3** would result in the point being drawn 1/**3** of the distance to the lastly created point from the chosen vertex.

<!-- ADD IMAGE TO SHOW-->

### Rotation

Can be uniquely applied to each outer vertex. Defaults to 0 if left empty or input is invalid

Expressed in degrees. Rotation is applied counter clockwise about the chosen outer vertex.

<!-- ADD IMAGE TO SHOW-->

### Probability

Can be uniquely applied to each outer vertex. Defaults to 1/**V** if left empty or input is invalid.

Values will be scaled and adjusted to sum to 1 with proportion kept the same. For example, if **V**=4 and **Probability** = [1, 2, 1, 1], **Probability** will be adjusted to [0.2, 0.4, 0.2, 0.2].

### Output

Two options for output. Both will create an image in the directory of that **main** is ran from that will be overwritten on subsequent button presses. You will need to navigate to this directory and rename or move the .png file to save a copy of the image.

- Update Image with Current Parameters:
  - will create a new 1000x1000 image named "image1000.png" with **N** points using the parameters chosen and update the image on the right of the display.
- Output a High Quality Version of This Image:
  - will create a new 4000x4000 named "image4000.png" with 250,000,000 (points reduction) or 15,000,000 (line reduction) points in the data set.
  - This can take quite a long time, and may cause the application to crash if attempted on a poorly specced pc.

_For more examples, please refer to the [Examples shown on Imgur](https://imgur.com/gallery/jqMogwz)_

<br>

<!-- LICENSE -->

## License

Distributed under the MIT License. See [MIT License](https://opensource.org/licenses/MIT) for more information.
