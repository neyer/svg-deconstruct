#!/usr/bin/python3
# requires svg.path, install it like this: pip3 install svg.path

# converts a list of path elements of a SVG file to simple line drawing commands
from svg.path import parse_path
from svg.path.path import Line, CubicBezier, Move, Close, Path
from xml.dom import minidom
import lazyopt
import functools

FILE_NAME="cc_iStock-478639870_16x9.svg"
NUM_SHAPES = 100


class Shape(object):
  def __init__(self, path, fill_color):
    self.path = path
    self.fill_color = fill_color

  @property
  @functools.lru_cache(None)
  def line_points(self):
    "Take the path and compute a series of points"
    line_points = []
    for e in self.path:
      if isinstance(e, Line):
          if not line_points:
            line_points.append((e.start.real,e.start.imag))
          line_points.append((e.end.real,e.end.imag))
      elif isinstance(e, CubicBezier):
          if not line_points:
            line_points.append((e.start.real,e.start.imag))
          point_num = 1
          while True:
            point_name = 'control{}'.format(point_num)
            if hasattr(e, point_name):
              point_value = getattr(e, point_name)
              line_points.append((point_value.real, point_value.imag))
              point_num += 1
            else: 
              break
          line_points.append((e.end.real,e.end.imag))
      elif isinstance(e, Move):
        line_points.append((e.start.real,e.start.imag))
      elif isinstance(e, Close):
        pass
      else:
        raise ValueError(e)
    return line_points


  @property
  @functools.lru_cache(None)
  def centroid(self):
    sum_x = 0
    sum_y = 0
    num_points = len(self.line_points)
    for point in self.line_points:
      sum_x += point[0]
      sum_y += point[1]
    return sum_x/num_points + (sum_y/num_points)*1j

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

SVG_HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 1280 720" width="1280.0pt" height="720.0pt">"""
DOC_WIDTH = 1280
DOC_HEIGHT = 720

def GetCentroidForShapeNum(shape_num):
  y_value = shape_num / 20
  x_value = shape_num % 20
  return 128*x_value + y_value*72j

def PrintSVGFileContents(shapes):
  print (SVG_HEADER)
  for shapeno, shape in zip(range(len(shapes)), shapes):
      print ('<path d="{}" fill="{}"/>'.format(
          shape.get_shifted_path(GetCentroidForShapeNum(shapeno)).d(),
          shape.fill_color))
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

  PrintSVGFileContents(shapes)

if __name__ == '__main__':
  lazyopt.apply_all()
  ReadFile(FILE_NAME)
