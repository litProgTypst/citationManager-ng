# Capture new references

## Goals

We want tools to collect new references and translate them into
TiddlyWiki Tiddlers.

## Problem

Zotero is the "market" leader in managing "BibTeX" references.

Zotero's "output" format is essentially "only" one or more BibTeX
"libraries", text files in the BibTeX format.

However, we *will* need to collect multiple versions of a given reference,
and collate the results. This means we will need to be able to parse
multiple versions of a given reference, and semi-automatically amalgamate
these versions into one.

We would rather control our references as a collection of text files which
when combined provide a coherent interface to our reference collection.
These text files will be version controlled using Git.

Our (current) preferred "interface" is TiddlyWiki. So our "text files"
will be TiddlyWiki tiddlers.

**SO** we need the ability to load and parse BibTeX files, correlate
Authors, and then explode the resulting references into individual
tiddlers.

## Solution(s)

### New reference collection

We will use Zotero to collect ALL references, either using the Zotero
Connector (directly) and/or using Firefox's "Bib it now". 

We can use the BBT Zotero plugin to adapt/pin the citation key so that all
alternates have the same root citation with a `-X` appended.

```
  You can fix the citation key (called pinning in BBT) for an item by
  adding the text `Citation Key: <your citekey>` anywhere in the extra
  field of the item on a line of its own. You can generate a pinned
  citation key by selecting one or more items, right-clicking, and
  selecting Generate BibTeX key, which will add the current citation key
  to the extra field, thereby pinning it.
```

We can then export our current collection of reference variants using
Zotero's library export to Better BibLaTeX.

### Collation with existing references

We will write a script which loads and parses the BibLaTeX "library" of
current references, collates reference variants and collates with existing
references.

The result will be "edited" using Micro as a simple YAML file.

The results of this editing will be further collated. 

If there are any further things to be fixed, the result will be (re)edited
using Micro.

If there are no further things to be fixed, the results will be written
out as tiddlers.

### Generation of tiddlers

The final stage of the collation will be the creation of the resulting
tiddlers.

