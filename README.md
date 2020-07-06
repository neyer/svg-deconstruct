# SVG Deconstructor

Takes an SVG image consisting of a number of filled paths, breaks it up into shapes, and then re-arranges the shapes to make a 'deconstructed' image.

Turns
![svg image of a tree](https://raw.githubusercontent.com/neyer/svg-deconstruct/e9c539165743a801977eef49f934d9e8780301ba/wide.svg)

Into
![svg image of a tree, deconstructed](https://raw.githubusercontent.com/neyer/svg-deconstruct/e9c539165743a801977eef49f934d9e8780301ba/output-wide-sorted.svg)


# Why
I took a few drawing classes online, and these classes caused me to notice more of the beauty already around me. I started to view trees more as visual objects, pure creations of simple concepts like, color, and shape. Trees are _incredible_ works of art, when viewed only in terms of how they use these basic forms.

For example, consider line.  The only things that characterize a line are its angle and width. When I looked at how a tree 'uses' lines, I noticed that there is a wide distribution of line widths. The trunk is a very wide line, branches get increasingly smaller, until we get to twigs, and even the veins in the leaf of a tree.  The bigger lines
tend to have very restricted angles - the trunk usually goes straigth up. As lines get smaller and smaller, they start to every which way.

I was really hoping to see what this woudl actually look like. As a first pass, I thought i'd try breaking up an SVG image of a tree. I naively thought that the svg image would be
a rough approximation of the tree's geometry, but this turns out to not be the case.

I still haven't gotten to see what I actually watned to see, but now I have found one approach that didn't work - although it did make some neat pictures.

# How to use it
This uses python 3, and you'll need to install the libraries requirements.txt using pip. Run the program

`python parse_tree.py --file_name any-svg-file.svg > output-here.svg"

The program may through an error if it encounters svg path elements different from the ones in the test images i used. 

Enjoy!
