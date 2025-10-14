
# This PYTHON script loads a bib*tex.yml file and unpacks the variables
# into arrays.

import os
import yaml

def readYAML(inFileName) :
  hashObj = {}
  with open(inFileName) as inFile :
    hashObj = yaml.safe_load(inFile.read())
  return hashObj

def collectFieldsFrom(entry, fieldType) :
  theFields = []
  if fieldType in entry :
    theFields = entry[fieldType]
  if isinstance(theFields, str) :
    theFields = theFields.strip().split(',')
  strippedFields = []
  for aField in theFields :
    strippedFields.append(aField.strip())
  entry[fieldType] = sorted(strippedFields)

def unpackFieldsFromTypes(typesObj) :
  for entryType in sorted(typesObj.keys()) :
    entry = typesObj[entryType]

    collectFieldsFrom(entry, 'requiredFields')
    collectFieldsFrom(entry, 'usefulFields')
    collectFieldsFrom(entry, 'optionalFields')

    reducedOptFields = []
    for aField in entry['optionalFields'] :
      if aField not in entry['usefulFields'] :
        reducedOptFields.append(aField)
    entry['optionalFields'] = reducedOptFields

def crossrefField(fieldsObj, aField, fieldType, entryType, fieldsTypesName) :
  if aField in fieldsObj :
    fieldsObj[aField][fieldType].append(entryType)
  else :
    print(f"NO [{aField}] field found in {fieldsTypesName} (crossrefField)")

def crossrefFieldsInTypes(typesObj, fieldsObj, fieldsTypesName) :
  for fieldType, field in fieldsObj.items() :
    if 'requiredBy'  not in field : field['requiredBy']  = []
    if 'usefulFor'   not in field : field['usefulFor']   = []
    if 'optionalFor' not in field : field['optionalFor'] = []
    typeStr = field['type']
    if '(' in typeStr :
      typeArray = typeStr.split('(')
      field['structure'] = typeArray[0].strip()
      field['type']      = typeArray[1].split(')')[0].strip()
    else :
      field['structure'] = 'field'
      field['type']      = typeStr
  for entryType in sorted(typesObj.keys()) :
    entry = typesObj[entryType]
    if 'requiredFields' not in entry : entry['requiredFields'] = []
    for aField in entry['requiredFields'] :
      crossrefField(fieldsObj, aField, 'requiredBy',
                    entryType, fieldsTypesName)

    if 'usefulFields' not in entry : entry['usefulFields'] = []
    for aField in entry['usefulFields'] :
      crossrefField(fieldsObj, aField, 'usefulFor',
                    entryType, fieldsTypesName)

    if 'optionalFields' not in entry : entry['optionalFields'] = []
    for aField in entry['optionalFields'] :
      crossrefField(fieldsObj, aField, 'optionalFor',
                    entryType, fieldsTypesName)

def addCrossRefs(hashObj) :
  for key, value in hashObj.items() :
    if 'bibtex' not in value   : value['bibtex']   = []
    if 'biblatex' not in value : value['biblatex'] = []
    if 'amsrefs' not in value  : value['amsrefs']  = []
    if 'aigaion' not in value  : value['aigaion']  = []

def crossrefFormats(biblatex, bibtex, amsrefs, aigaion) :
  addCrossRefs(biblatex)
  addCrossRefs(bibtex)
  addCrossRefs(amsrefs)
  addCrossRefs(aigaion)

  for bibtexKey in sorted(bibtex.keys()) :
    bibtexValue = bibtex[bibtexKey]
    bibtexValue['bibtex'].append(bibtexKey)
    for aBiblatexKey in bibtexValue['biblatex'] :
      if aBiblatexKey in biblatex :
        biblatex[aBiblatexKey]['bibtex'].append(bibtexKey)
      else :
        print(f"NO [{aBiblatexKey}] in bibtex({bibtexKey}) xref")

  for amsrefsKey in sorted(amsrefs.keys()) :
    amsrefsValue = amsrefs[amsrefsKey]
    amsrefsValue['amsrefs'].append(amsrefsKey)
    for aBiblatexKey in amsrefsValue['biblatex'] :
      if aBiblatexKey in biblatex :
        biblatex[aBiblatexKey]['amsrefs'].append(amsrefsKey)
      else :
        if aBiblatexKey not in [
          'inbook', 'book', 'inconference', 'conference'
        ] :
          print(f"NO [{aBiblatexKey}] in amsrefs({amsrefsKey}) xref")

  for aigaionKey in sorted(aigaion.keys()) :
    aigaionValue = aigaion[aigaionKey]
    aigaionValue['aigaion'].append(aigaionKey)
    for aBiblatexKey in aigaionValue['biblatex'] :
      if aBiblatexKey in biblatex :
        biblatex[aBiblatexKey]['aigaion'].append(aigaionKey)
      else :
        print(f"NO [{aBiblatexKey}] in aigaion({aigaionKey}) xref")

  for biblatexKey in sorted(biblatex.keys()) :
    biblatexValue = biblatex[biblatexKey]
    biblatexValue['biblatex'].append(biblatexKey)

def writeYAML(hashObj, outFileName) :
  with open(outFileName, 'w') as outFile :
    for aKey in sorted(hashObj.keys()) :
      aValue = hashObj[aKey]
      if '[' in aKey :
        outFile.write(f"'{aKey}':\n")
      else :
        outFile.write(f"{aKey}:\n")

      comment = aValue.pop('comment')
      if '\n' in comment :
        outFile.write("  comment: |\n")
        for aLine in comment.splitlines() :
          outFile.write(f"    {aLine}\n")
      else :
        outFile.write(f"  comment: {comment}\n")

      for aSubKey in sorted(aValue.keys()) :
        aSubValue = aValue[aSubKey]
        if isinstance(aSubValue, list) :
          if not aSubValue :
            outFile.write(f"  {aSubKey}: []\n")
          else :
            outFile.write(f"  {aSubKey}:\n")
            for aSubSubValue in aSubValue :
              outFile.write(f"  - {aSubSubValue}\n")
        else :
          if not aSubValue :
            aSubValue = ""
          outFile.write(f"  {aSubKey}: {aSubValue}\n")
      outFile.write('\n')

biblatexTypes  = readYAML('biblatexTypes.yaml.orig')
biblatexFields = readYAML('biblatexFields.yaml.orig')
bibtexTypes    = readYAML('bibtexTypes.yaml.orig')
bibtexFields   = readYAML('bibtexFields.yaml.orig')
amsrefsTypes   = readYAML('amsrefsTypes.yaml.orig')
amsrefsFields  = readYAML('amsrefsFields.yaml.orig')
aigaionTypes   = readYAML('aigaionTypes.yaml.orig')
aigaionFields  = readYAML('aigaionFields.yaml.orig')

unpackFieldsFromTypes(biblatexTypes)
unpackFieldsFromTypes(bibtexTypes)
unpackFieldsFromTypes(amsrefsTypes)
unpackFieldsFromTypes(aigaionTypes)

crossrefFieldsInTypes(biblatexTypes, biblatexFields, 'biblatex')
crossrefFieldsInTypes(bibtexTypes,   bibtexFields,   'bibtex')
crossrefFieldsInTypes(amsrefsTypes,  amsrefsFields,  'amsrefs')
crossrefFieldsInTypes(aigaionTypes,  aigaionFields,  'aigaion')

crossrefFormats(biblatexTypes,  bibtexTypes,  amsrefsTypes,  aigaionTypes)
crossrefFormats(biblatexFields, bibtexFields, amsrefsFields, aigaionFields)

writeYAML(biblatexTypes,  'biblatexTypes.yaml')
writeYAML(biblatexFields, 'biblatexFields.yaml')
writeYAML(bibtexTypes,    'bibtexTypes.yaml')
writeYAML(bibtexFields,   'bibtexFields.yaml')
writeYAML(amsrefsTypes,   'amsrefsTypes.yaml')
writeYAML(amsrefsFields,  'amsrefsFields.yaml')
writeYAML(aigaionTypes,   'aigaionTypes.yaml')
writeYAML(aigaionFields,  'aigaionFields.yaml')

#
# Copy a couple of other yaml files from *.yml.orig to *.yml
# This allows us to rm *.yml at will ;-)
#
os.system("cp monthNum2Names.yaml.orig monthNum2Names.yaml")
os.system("cp citationFieldOrder.yaml.orig citationFieldOrder.yaml")
os.system("cp biblatexFieldOrder.yaml.orig biblatexFieldOrder.yaml")
os.system(
  "cp biblatexFieldsXapianTerms.yaml.orig biblatexFieldsXapianTerms.yaml"
)


