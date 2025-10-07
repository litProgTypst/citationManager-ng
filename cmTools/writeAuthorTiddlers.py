
import os
import yaml

from utils import titleToFilenameStub, assembleTiddler, convertToCamelCase

"""
Need to compile list of non-ascii characters in our references (cleannames?)

input_string = "Hello, 世界!"
non_ascii_chars = [char for char in input_string if ord(char) > 127]
print(non_ascii_chars)

"""

def writeAuthorTable(newRefsDir, title, biblatex, authorLetters2) :
  lines = []

  lines.append(f"<h2>{biblatex['cleanname']}</h2>")

  lines.append("<table>")
  if 'cleanname' in biblatex and biblatex['cleanname'] :
    lines.append(f"""
      <tr>
        <th>clean name:</th>
        <td>{ biblatex['cleanname'] }</td>
      </tr>
    """)

  if 'synonymOf' in biblatex and biblatex['synonymOf'] :
    lines.append(f"""
      <tr>
        <th>synonym of:</th>
        <td>{ biblatex['synonymOf'] }</td>
      </tr>
    """)

  if 'firstname' in biblatex and biblatex['firstname'] :
    lines.append(f"""
      <tr>
        <th>first name:</th>
        <td>{ biblatex['firstname'] }</td>
      </tr>
    """)
  if 'von' in biblatex and biblatex['von'] :
    lines.append(f"""
      <tr>
        <th>von:</th>
        <td>{ biblatex['von'] }</td>
      </tr>
    """)

  if 'surname' in biblatex and biblatex['surname'] :
    lines.append(f"""
      <tr>
        <th>last name:</th>
        <td>{ biblatex['surname'] }</td>
      </tr>
    """)

  if 'jr' in biblatex and biblatex['jr'] :
    lines.append(f"""
      <tr>
        <th>jr:</th>
        <td>${ biblatex['jr'] }</td>
      </tr>
    """)

  if 'institute' in biblatex and biblatex['institute'] :
    lines.append(f"""
      <tr>
        <th>institute:</th>
        <td>{ biblatex['institute'] }</td>
      </tr>
    """)

  if 'email' in biblatex and (biblatex['email']) :
    lines.append(f"""
      <tr>
        <th>email:</th>
        <td>
          <a href="mailto:${ biblatex['email'] }">${ biblatex['email'] }</a>
        </td>
      </tr>
    """)

  if 'url' in biblatex and biblatex['url'] :
    lines.append("""
      <tr>
        <th>url:</th>
        <td>
          <ul>
    """)
    for aUrl in biblatex['url'] :
      lines.append(f'            <li><a href="{ aUrl }">{ aUrl }</a></li>')

    lines.append("""
          </ul>
        </td>
      </tr>
    """)

  # if papers is not None :
  #   lines.append("""
  #    <tr>
  #      <th>citeKeys:</th>
  #       <td>
  #         <ul>
  #   """)
  #   for citeKey, citeTitle, auxTitle in papers :
  #     lines.append(f"""
  #           <li>
  #             <a href="/refs/{ citeKey }">${ citeTitle }</a>
  #             <br> { auxTitle }
  #           </li>
  #     """)
  #   lines.append("""
  #         </ul>
  #       </td>
  #     </tr>
  #   """)

  lines.append("</table>")

  lines.append("<<toc-selective-expandable>>")

  headerContent = "\n".join(lines)
  headerContent = headerContent.replace("`","'")

  fileName = convertToCamelCase(title)
  authorLetters2.add(fileName[0:2])
  tags = f"[[Author_{fileName[0:2]}]]"
  print(fileName)

  fileNameStub = titleToFilenameStub(fileName)

  with open(os.path.join(newRefsDir, fileNameStub) + '.tid', 'w') as tidFile :
    tiddler = assembleTiddler(
      fileName, headerContent, tags
    )
    tidFile.write(tiddler)
  with open(
    os.path.join(newRefsDir, fileName) + '_bibLatex.yaml', 'w'
  ) as yamlFile :
    yamlFile.write(yaml.dump(biblatex))

def writeAuthorNote(newRefsDir, title, notes) :
  noteContent = notes.strip()
  noteContent = noteContent.replace("`","'")

  if noteContent :
    fileName = convertToCamelCase(title)
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


def writeAuthorToC(newRefsDir, authorLetters2) :
  authorLetters1 = set()
  for anAuthorLetter in sorted(authorLetters2) :
    authorLetters1.add(anAuthorLetter[0:1])
    fileName = 'Author_' + anAuthorLetter
    fileNameStub = titleToFilenameStub(fileName)
    with open(
      os.path.join(newRefsDir, fileNameStub) + '.tid', "w"
    ) as tidFile :
      tags = f"[[{fileName[0:8]}]]"
      tiddler = assembleTiddler(
        fileName,
        "<<toc-selective-expandable>>",
        tags,
        caption=anAuthorLetter
      )
      tidFile.write(tiddler)

  for anAuthorLetter in sorted(authorLetters1) :
    fileName = 'Author_' + anAuthorLetter
    fileNameStub = titleToFilenameStub(fileName)
    with open(
      os.path.join(newRefsDir, fileNameStub) + '.tid', "w"
    ) as tidFile :
      tags = "[[Author]]"
      tiddler = assembleTiddler(
        fileName,
        "<<toc-selective-expandable>>",
        tags,
        caption=anAuthorLetter
      )
      tidFile.write(tiddler)

  fileName = 'Author'
  fileNameStub = titleToFilenameStub(fileName)
  with open(os.path.join(newRefsDir, fileNameStub) + '.tid', "w") as tidFile :
    tiddler = assembleTiddler(
      fileName,
      """
<div class="tc-table-of-contents">

<<toc-selective-expandable 'Author'>>

</div>
      """,
      "$:/tags/SideBar"
    )
    tidFile.write(tiddler)

