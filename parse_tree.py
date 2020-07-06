#!/usr/bin/python3
# requires svg.path, install it like this: pip3 install svg.path

# converts a list of path elements of a SVG file to simple line drawing commands
from svg.path import parse_path
from svg.path.path import Line, CubicBezier, Move, Close, Path
from xml.dom import minidom
import colorsys
import lazyopt
import functools

FILE_NAME="self.svg"
NUM_SHAPES = 100000


class Shape(object):
  def __init__(self, path, fill_color):
    self.path = path
    self.fill_color_html = fill_color
    r = int(fill_color[1:3],16)
    g = int(fill_color[3:5],16)
    b = int(fill_color[5:7],16)
    self.color_rgb = (r,g,b)

  @property
  @functools.lru_cache(None)
  def color_hls(self):
    r,g,b = self.color_rgb
    return colorsys.rgb_to_hls(r/256.0, g/256.0, b/256.0)

  @property
  @functools.lru_cache(None)
  def line_points(self):
    "Take the path and compute a series of points"
    line_points = []
    for e in self.path:
      if isinstance(e, Line):
          if not line_points:
            line_points.append(e.start)
          line_points.append(e.end)
      elif isinstance(e, CubicBezier):
          if not line_points:
            line_points.append(e.start)
          point_num = 1
          while True:
            point_name = 'control{}'.format(point_num)
            if hasattr(e, point_name):
              point_value = getattr(e, point_name)
              line_points.append(point_value)
              point_num += 1
            else: 
              break
          line_points.append(e.end)
      elif isinstance(e, Move):
        line_points.append(e.start)
      elif isinstance(e, Close):
        pass
      else:
        raise ValueError(e)
    return line_points


  @property
  @functools.lru_cache(None)
  def centroid(self):
    sum = 0+0j
    num_points = len(self.line_points)
    for point in self.line_points:
      sum += point
    return sum/num_points

  @property
  @functools.lru_cache(None)
  def radius(self):
    
    max_delta = 0
    for point in self.line_points:
      this_delta = abs(point-self.centroid) 
      max_delta = max(max_delta, this_delta)
    return max_delta

  def get_shifted_path(self, new_centroid):
    "Returns a version of the path with a new centroid location"
    delta = new_centroid - self.centroid
    out_path = Path()
    for e in self.path:
      if isinstance(e, Line):
          out_path.append(Line(e.start+delta, e.end+delta))
      elif isinstance(e, CubicBezier):
          point_num = 1
          args = {'start': e.start+delta, 'end':e.end+delta}
          while True:
            point_name = 'control{}'.format(point_num)
            if hasattr(e, point_name):
              point_value = getattr(e, point_name)
              args[point_name] = point_value + delta
              point_num += 1
            else: 
              break
          out_path.append(CubicBezier(**args))
      elif isinstance(e, Move):
        out_path.append(Move(e.start+delta))
      elif isinstance(e, Close):
        out_path.append(Close(e.start+delta, e.end+delta))
      else:
        raise ValueError(e)
    return out_path

DOC_WIDTH = 1280
DOC_HEIGHT = 4000
SVG_HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 {width} {height}" width="{width}.0pt" height="{height}.0pt">""".format(width=DOC_WIDTH,height=DOC_HEIGHT)
FUDGE_FACTOR = 1.1

def PrintSVGFileContents(shapes):
  print (SVG_HEADER)

  # group the shapes into rows
  this_row_shapes = []
  current_x = 0
  current_y = 0
  for shape in shapes:
      if (current_x == 0):
        current_x += shape.radius
      else:
        current_x += shape.radius*2*FUDGE_FACTOR

      if current_x < DOC_WIDTH:
        this_row_shapes.append(shape)
      else:
        # shift the centroid all the way to the left, and down accordingly
        # sort the shapes in this row by color
        to_draw = sorted(this_row_shapes, key=lambda shape: shape.color_hls[1])
        current_x = 0
        for draw_shape in to_draw:
          if (current_x == 0):
            current_x += draw_shape.radius
          else:
            current_x += draw_shape.radius*2*FUDGE_FACTOR
          new_centroid = current_x + current_y*1j
          print ('<path d="{}" fill="{}"/>'.format(draw_shape.get_shifted_path(new_centroid).d(),
                 draw_shape.fill_color_html))

        # prepare for a new row
        print ('<!--new line! radius {}, old imag {}-->'.format(shape.radius, new_centroid.imag))
        current_y +=  max([row_shape.radius for row_shape in this_row_shapes])*FUDGE_FACTOR*2
        current_x = 0
        # we ended the row by encountering this shape, which was too big to fit
        this_row_shapes = [shape]
  print ("</svg>")

def ReadFile(file_name):
  # read the SVG file
  doc = minidom.parse(file_name)
  path_strings_with_fill  = [(path.getAttribute('d'), path.getAttribute("fill"))for path
                  in doc.getElementsByTagName('path')]
  doc.unlink()
  
  shapes = []
  # print the line draw commands
  for path_string, fill_color in path_strings_with_fill:
      path = parse_path(path_string)
      shape = Shape(path, fill_color)
      shapes.append(shape)
      if len(shapes) == NUM_SHAPES:
        break
  PrintSVGFileContents(sorted(shapes, key=lambda shape: shape.radius))

if __name__ == '__main__':
  lazyopt.apply_all()
  ReadFile(FILE_NAME)
