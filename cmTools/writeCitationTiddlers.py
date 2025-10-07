
import os
import yaml

from utils import titleToFilenameStub, assembleTiddler, \
  convertToCamelCase, author2url

#####################################
# Load YAML data files

yamlDir = os.path.dirname(__file__)

citationFieldOrderPath = os.path.join(yamlDir, 'citationFieldOrder.yaml')
citationFieldOrder = {
  'order' : [],
  'outputMap' : {}
}
with open(citationFieldOrderPath) as yamlFile :
  citationFieldOrder = yaml.safe_load(yamlFile.read())

#####################################
# Helper functions

monthNum2Names = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December'
]

def citeMonth(lines, fieldValue) :
  if isinstance(fieldValue, str) :
    lines.append(fieldValue)
  elif isinstance(fieldValue, int) :
    lines.append(monthNum2Names[fieldValue])

def citeIsbn(lines, isbn) :
  lines.append(
    f'<a href="https://openlibrary.org/search?isbn={ isbn }">{ isbn }</a>'
  )

def citeCiteKey(lines, citeKeys, pdfBaseUrl) :
  if isinstance(citeKeys, str) :
    lines.append(citeKeys)
    if pdfBaseUrl :
      lines.append("<br/>")
      lines.append(f'<a href="{pdfBaseUrl}.pdf" target="_blank">pdf</a>')  # noqa
      lines.append(f'(<a href="{pdfBaseUrl}-parts.pdf" target="_blank">parts</a>)')  # noqa
  else :
    for citeKey in citeKeys :
      lines.append(citeKey)

def citeCiteKeys(lines, citeKeys) :
  if isinstance(citeKeys, str) :
    lines.append(citeKeys)
  else :
    for citeKey in citeKeys :
      lines.append(citeKey)

def citeDoi(lines, doi) :
  lines.append(
    f'<a href="http://doi.org/{ doi }">{ doi }</a>'
  )

def citeNames(lines, names, tags) :
  lines.append("<ul>")
  if isinstance(names, str) :
    lines.append(
      f' <li><a href="#{ author2url(names) }">{names}</a></li>'
    )
    tags.append(f"[[{ author2url(names)}]]")
  else :
    for name in names :
      lines.append(
        f' <li><a href="#{ author2url(name) }">{name}</a></li>'
      )
      tags.append(f"[[{ author2url(name)}]]")
  lines.append("</ul>")

def citeUrls(lines, urls):
  lines.append("<ul>")
  if isinstance(urls, str) :
    lines.append(f'<li><a href="{ urls }">{ urls }</a></li>')
  else :
    for aURL in urls :
      lines.append(f'<li><a href="{ aURL }">{ aURL }</a></li>')
  lines.append("</ul>")

citeRefs = {
  'citeMonth'    : citeMonth,
  'citeIsbn'     : citeIsbn,
  'citeCiteKey'  : citeCiteKey,
  'citeCiteKeys' : citeCiteKeys,
  'citeDoi'      : citeDoi,
  'citeNames'    : citeNames,
  'citeUrls'     : citeUrls
}

def writeCitationTable(newRefsDir, title, biblatex, citationLetters2) :

  # compute the base fileName
  citeKey = biblatex['citekey']
  fileName = citeKey
  if ' ' in fileName :
    fileName = convertToCamelCase(fileName)
  with open(
    os.path.join(newRefsDir, fileName) + '_bibLatex.yaml', 'w'
  ) as yamlFile :
    yamlFile.write(yaml.dump(biblatex))
  citationLetters2.add(fileName[0:2])
  tags = [ f"[[Citation_{fileName[0:2]}]]" ]

  # now prepend the year if we know it
  if 'year' in biblatex :
    fileName = str(biblatex['year']) + '-' + fileName
  print(fileName)
  fileNameStub = titleToFilenameStub(fileName)

  biblatexUrl   = fileName + '_bibLatex'
  bibcontextUrl = fileName + '_bibContext'
  bibTypstUrl   = fileName + '_bibTypst'

  lines = []

  lines.append(f"<h2>{biblatex['title']}</h2>")

  lines.append("<<toc>>")

  # lines.append(
  #   " ".join([
  #     f'[[BibLaTeX|{ biblatexUrl }]]',
  #     f'[[BibConTeXt(lua)|{ bibcontextUrl }]]',
  #     f'[[BibTypst(hayagriva YAML)|{ bibTypstUrl }]]'
  #  ])
  # )

  lines.append( "  <table>")
  for aField in citationFieldOrder['order'] :
    if (aField in biblatex) and (biblatex[aField] is not None) :
      lines.append(f"""
      <tr><!-- { aField } -->
      """)
      outputMap = citationFieldOrder['outputMap']
      if (aField in outputMap) and (outputMap[aField] is not None) :
        aFieldOutputMap = outputMap[aField]
        if 'text' in aFieldOutputMap :
          lines.append(f"""
        <th>{ aFieldOutputMap['text'] }:</th>
          """)
        else :
          lines.append(f"""
        <th>{ aField }:</th>
          """)

        if 'include' in aFieldOutputMap :
          lines.append("""
        <td>
          """)
          fieldValue = biblatex[aField]
          if fieldValue is not None :
              templateName = aFieldOutputMap['include']
              if templateName == 'citeNames' :
                citeNames(lines, fieldValue, tags)
              elif templateName == 'citeCiteKey' :
                pdfBaseUrl = None
                if 'docType' in biblatex :
                  pdfBaseUrl = f"/static/references/{biblatex['docType']}/{citeKey[0:2]}/{citeKey}"  # noqa
                citeCiteKey(lines, fieldValue, pdfBaseUrl)
              else :
                citeRefs[templateName](lines, fieldValue)
          lines.append("""
        </td>
          """)
        else :
          lines.append(f"""
        <td>{ biblatex[aField] }</td>
          """)

      else :
        lines.append(f"""
        <th>{ aField }:</th>
        <td>{ biblatex[aField] }</td>
        """)

      lines.append("""</tr>""")
      # endif
    # endif
  # endfor
  lines.append("""
    </table>
  """)

  headerContent = "\n".join(lines)
  headerContent = headerContent.replace("`","'")

  captionTitle = biblatex['title'].strip(
  ).replace(":"," "
  ).replace("`","'"
  ).replace("\n", " "
  )
  caption = f"{fileName} | {captionTitle}"
  # caption = f"{fileName}"

  with open(os.path.join(newRefsDir, fileNameStub) + '.tid', 'w') as tidFile :
    tiddler = assembleTiddler(
      fileName,
      headerContent,
      " ".join(tags),
      caption=caption
    )
    tidFile.write(tiddler)

  tags = f"[[{fileName}]]"

  with open(os.path.join(newRefsDir, biblatexUrl) + '.tid', 'w') as tidFile :
    tiddler = assembleTiddler(biblatexUrl, "", tags)
    tidFile.write(tiddler)
  with open(os.path.join(newRefsDir, bibcontextUrl) + '.tid', 'w') as tidFile :
    tiddler = assembleTiddler(bibcontextUrl, "", tags)
    tidFile.write(tiddler)
  with open(os.path.join(newRefsDir, bibTypstUrl) + '.tid', 'w') as tidFile :
    tiddler = assembleTiddler(bibTypstUrl, "", tags)
    tidFile.write(tiddler)

def writeCitationNote(newRefsDir, citeKey, notes, biblatex) :
  noteContent = notes.strip()
  noteContent = noteContent.replace("`","'")

  if noteContent :
    fileName = citeKey
    if ' ' in fileName :
      fileName = convertToCamelCase(fileName)
    if 'year' in biblatex :
      fileName = str(biblatex['year']) + '-' + fileName
    tags = f"[[{fileName}]]"
    fileName = fileName + '_Notes'
    fileNameStub = titleToFilenameStub(fileName)
    with open(
      os.path.join(newRefsDir, fileNameStub) + '.tid', 'w'
    ) as tidFile :
      tiddler = assembleTiddler(
        fileName, noteContent, tags, type="text/markdown"
      )
      tidFile.write(tiddler)

def writeCitationToC(newRefsDir, citationLetters2) :
  citationLetters1 = set()
  for aCitationLetter in sorted(citationLetters2) :
    citationLetters1.add(aCitationLetter[0:1])
    fileName = 'Citation_' + aCitationLetter
    fileNameStub = titleToFilenameStub(fileName)
    with open(
      os.path.join(newRefsDir, fileNameStub) + '.tid', "w"
    ) as tidFile :
      tags = f"[[{fileName[0:10]}]]"
      tiddler = assembleTiddler(
        fileName,
        "<<toc-selective-expandable>>",
        tags,
        caption=aCitationLetter
      )
      tidFile.write(tiddler)

  for aCitationLetter in sorted(citationLetters1) :
    fileName = 'Citation_' + aCitationLetter
    fileNameStub = titleToFilenameStub(fileName)
    with open(
      os.path.join(newRefsDir, fileNameStub) + '.tid', "w"
    ) as tidFile :
      tags = "[[Citation]]"
      tiddler = assembleTiddler(
        fileName,
        "<<toc-selective-expandable>>",
        tags,
        caption=aCitationLetter
      )
      tidFile.write(tiddler)

  fileName = 'Citation'
  fileNameStub = titleToFilenameStub(fileName)
  with open(os.path.join(newRefsDir, fileNameStub) + '.tid', "w") as tidFile :
    tiddler = assembleTiddler(
      fileName,
      '<div class="tc-table-of-contents"><<toc-selective-expandable "Citation">></div>',  # noqa
      "$:/tags/SideBar"
    )
    tidFile.write(tiddler)

