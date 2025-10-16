
import importlib.resources
import os
from pathlib import Path
import sys
import yaml

def die(msg) :
  print(msg)
  sys.exit(1)

def addConfigurationArgs(parser) :
  parser.add_argument(
    '-c', '--config',
    help="The path to the user configuration file",
    default=os.path.expanduser('~/.config/citationManager/config.yaml')
  )
  parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    default=False,
    action='store_true'
  )

class Config(object) :
  def __new__(cls) :
    if not hasattr(cls, 'instance') :
      cls.instance = super(Config, cls).__new__(cls)
    return cls.instance

  def __getitem__(self, key) :
    return self.config[key]

  def print(self) :
    print("-------------------------------------------------")
    print(yaml.dump(self.config))
    print("-------------------------------------------------")

  def resourceException(self, resourceName, err) :
    print(f"Could not load {resourceName}")
    print(f"  from {self.config[resourceName]}")
    print(repr(err))

  def loadResource(self, resourceName) :
    resourcePath = resourceName + 'Path'
    print(f"Loading {resourceName} from {resourcePath}")
    if resourcePath in self.config :
      print(f"ResourcePath in config {resourcePath}")
      try :
        resourcePath = Path(
          self.config[resourcePath]
        ).expanduser()
        setattr(
          self, resourceName, yaml.safe_load(
            resourcePath.read_text()
          )
        )
      except Exception as err :
        self.resourceException(resourceName, err)

    if not hasattr(self, resourceName) :
      try :
        setattr(
          self, resourceName, yaml.safe_load(
            importlib.resources.read_text(
              'cmTools.resources', resourceName + '.yaml'
            )
          )
        )
      except Exception as err :
        self.resourceException(resourceName, err)

    if not hasattr(self, resourceName) :
      setattr(self, resourceName, {})

    print(f" Finished loading {resourceName}")

  def loadConfig(self, args, verbose=False) :
    if 'config' not in args :
      die("No configuration file specified... can not continue")

    self.config = {}
    with open(args['config']) as confFile :
      self.config = yaml.safe_load(confFile.read())

    for aKey, aValue in args.items() :
      if aValue : self.config[aKey] = aValue

    if 'verbose' not in self.config :
      self.config['verbose'] = verbose

    if 'refsDir' not in self.config :
      die("ERROR: no references directory has been configured!")

    self.refsDir = Path(self.config['refsDir']).expanduser()
    if not any(self.refsDir.glob("**/*_*Biblatex.yaml")) :
      print("No files found....")
      print(f"  at {self.config['refsDir']}")
      print(f"  at {self.refsDir}")
      print("  have you mounted the remote references?")
      sys.exit(1)

    if 'newRefsDir' not in self.config :
      die("ERROR: no NEW references directory has been configured!")

    self.newRefsDir = Path(self.config['newRefsDir']).expanduser()
    self.newRefsDir.mkdir(parents=True, exist_ok=True)

    if 'pdfDir' not in self.config :
      self.config['pdfDir'] = "~/Downloads/PDF"

    Path(self.config['pdfDir']).expanduser().mkdir(exist_ok=True)

    if 'entryTypeMapping' not in self.config :
      self.config['entryTypeMapping'] = {}

    if 'biblatexFieldMapping' not in self.config :
      self.config['biblatexFieldMapping'] = {}

    if 'width'  not in self.config : self.config['width'] = 600
    if 'height' not in self.config : self.config['height'] = 600

    self.loadResource('biblatexFieldOrder')
    self.loadResource('biblatexFields')
    self.loadResource('biblatexTypes')
    self.loadResource('citationFieldOrder')

    if self.config['verbose'] : self.print()

