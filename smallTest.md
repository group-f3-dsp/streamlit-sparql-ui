Hi, yes it is possible to feed the data into WebVOWL, but you have to adjust your data a bit.

Here is a simple example (I write some comments to the lines)

// Since this is JSON we need an object.

```json
{
  // We first start with some meta information. (You can simply take it as it is, it does not interfere with the
  // visualization, but this information is shown in the sidebar, so it would be better if you try to maintain also
  // these to be correct and reflecting your data

  "_comment": "Just a test",
  "header": {
    "languages": ["en", "undefined"],
    "baseIris": ["http://www.w3.org/2000/01/rdf-schema", "http://visualdataweb.de/test_cases_vowl/ontology/72"],
    "iri": "http://visualdataweb.de/example_ontology/"
  },
  "namespace": [],
  "metrics": {
    "classCount": 3,
    "datatypeCount": 2,
    "objectPropertyCount": 4,
    "datatypePropertyCount": 2,
    "propertyCount": 6,
    "nodeCount": 3,
    "individualCount": 0
  },
  // Now we define the classes
  // id can be a string or a number, I use c1 for class1 and d1 for datatype1
  // WebVOWL supports different types of classes, you can look them up in one of the already provided ontologies (Export->Save as JSON)
  "class": [
    { "id": "c1", "type": "owl:Class" },
    { "id": "c2", "type": "owl:Class" },
    { "id": "c3", "type": "owl:Class" },
    { "id": "d1", "type": "rdfs:Datatype" }, // <<-- This is a named datatype, we can change its name
    { "id": "d2", "type": "rdfs:Literal" } // <<-- This is a Literal, so the name is set to Literal automatically
  ],

  // Now we need to define some attributes, there are more but these should be sufficient for now
  // We set here the label of a node with an Id
  "classAttribute": [
    { "label": "A", "id": "c1" },
    { "label": "B", "id": "c2" },
    { "label": "C", "id": "c3" },
    { "label": "aDatatype", "id": "d1" }, // <-- here we named the rdfs:datatype = aDatatype
    { "id": "d2" } // <-- here we don't need to set the label because this one is a literal
  ],

  // Now we define the properties (I give them here the id p1)
  "property": [
    { "id": "p1", "type": "owl:objectProperty" },
    { "id": "p2", "type": "owl:objectProperty" },
    { "id": "p3", "type": "owl:objectProperty" },
    { "id": "p4", "type": "owl:objectProperty" },
    { "id": "p5", "type": "owl:datatypeProperty" }, // <<-- datatype properties
    { "id": "p6", "type": "owl:datatypeProperty" } // <<-- datatype properties
  ],
  // Here we give these properties a label and also define the domain and the range
  "propertyAttribute": [
    { "id": "p1", "domain": "c1", "range": "c2", "label": "p1" },
    { "id": "p2", "domain": "c1", "range": "c3", "label": "p2" },
    { "id": "p3", "domain": "c2", "range": "c3", "label": "p3" },
    { "id": "p4", "domain": "c3", "range": "c1", "label": "p4" },
    { "id": "p5", "domain": "c3", "range": "d1", "label": "datatypeProperty" },
    { "id": "p6", "domain": "c3", "range": "d2", "label": "literalProperty" }
  ]
}
// That's it
```

For more details, you can refer to the [GitHub discussion](https://github.com/VisualDataWeb/WebVOWL/issues/117).