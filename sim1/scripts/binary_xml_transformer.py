import os
from lxml import etree


def old_yule_to_new_template(input_file, output_file):
    tree = etree.parse(input_file)
    root = tree.getroot()

    # replace namespace block
    for element in root.iter("beast"):
        element.set("version", "2.6")
        namespace = "beast.core:beast.core.util:"\
                    "beast.evolution.datatype:" \
                    "beast.evolution.alignment:" \
                    "beast.evolution.operators:" \
                    "beast.evolution.sitemodel:" \
                    "beast.evolution.substitutionmodel:" \
                    "beast.evolution.likelihood:" \
                    "phylonco.beast.evolution.substitutionmodel:" \
                    "phylonco.beast.evolution.errormodel:" \
                    "phylonco.beast.evolution.likelihood"
        element.set("namespace", namespace)

    # change datatype
    for element in root.iter("data"):
        if element.get("id") == "alignment":
            element.set("dataType", "binary")

    # update error model
    for element in root.iter("input"):
        if element.get("spec") == "BinaryWithErrorSampled":
            element.set("spec", "BinaryErrorModel")
            subelement = etree.Element("datatype")
            subelement.set("id", "datatype")
            subelement.set("spec", "beast.evolution.datatype.Binary")
            element.append(subelement)
        if element.get("spec") == "TreeLikelihoodWithErrorSlow":
            element.set("spec", "TreeLikelihoodWithErrorFast")

    # update output log filenames
    for element in root.iter("logger"):
        filename = str(element.get("fileName"))
        if filename.endswith(".log"):
            element.set("fileName", output_file.replace(".xml", ".log"))
        if filename.endswith(".trees"):
            element.set("fileName", output_file.replace(".xml", ".trees"))

    # strip extra spaces from namespace
    root.set("namespace", root.get("namespace").strip())
    # write xml
    etree.indent(root)
    output_handle = open(output_file, "wb")
    output_handle.write(etree.tostring(root))


def yule_no_error(input_file, output_file):
    tree = etree.parse(input_file)
    root = tree.getroot()

    for element in root.iter("input"):
        spec = element.get("spec")
        # remove
        # <input spec='BinaryErrorModel' id='errorModel'>
        if spec == "BinaryErrorModel":
            element.getparent().remove(element)
        # replace
        # <input spec='TreeLikelihoodWithErrorFast' id='treeLikelihood' useAmbiguities='true' useTipLikelihoods='true'>
        # with
        # <input spec='ThreadedTreeLikelihood'  id='treeLikelihood' useAmbiguities='true'>
        if spec == "TreeLikelihoodWithErrorFast":
            element.set("spec", "ThreadedTreeLikelihood")
            del element.attrib["useTipLikelihoods"]

    # remove
    # <errorModel idref="errorModel"/>
    for element in root.iter("errorModel"):
        if element.get("idref") == "errorModel":
            element.getparent().remove(element)

    # remove
    # <parameter id='error.alpha' ... />
    # <parameter id='error.beta' ... />
    for element in root.iter("parameter"):
        eid = element.get("id")
        if eid == "error.alpha" or eid == "error.beta":
            element.getparent().remove(element)

    # remove
    # <distribution spec='beast.math.distributions.Prior' x='@error.alpha'>
    #     ...
    # </distribution>
    # <distribution spec='beast.math.distributions.Prior' x='@error.beta'>
    #     ...
    # </distribution>
    for element in root.iter("distribution"):
        spec = element.get("spec")
        x = element.get("x")
        prior = "beast.math.distributions.Prior"
        if spec == prior and (x == "@error.alpha" or x == "@error.beta"):
            element.getparent().remove(element)

    # remove error.alpha error.beta operators
    # <operator id="alphaScaler" ... />
    # <operator id="betaScaler" ... />
    for element in root.iter("operator"):
        eid = element.get("id")
        if eid == "alphaScaler" or eid == "betaScaler":
            element.getparent().remove(element)

    # remove error loggers
    # <logger logEvery="2000" ...>
    #       <log idref="error.alpha"/>
    #       <log idref="error.beta"/>
    # ...
    # <logger logEvery="2000">
    #       <log idref="error.alpha"/>
    #       <ESS spec="ESS" name="log" arg="@error.alpha"/>
    #       <log idref="error.beta"/>
    #       <ESS spec="ESS" name="log" arg="@error.beta"/>
    #       ...
    for element in root.iter("log"):
        eid = element.get("idref")
        if eid == "error.alpha" or eid == "error.beta":
            element.getparent().remove(element)

    for element in root.iter("ESS"):
        arg = element.get("arg")
        if arg == "@error.alpha" or arg == "@error.beta":
            element.getparent().remove(element)

    # replace filename
    for element in root.iter("logger"):
        filename = str(element.get("fileName"))
        if filename.endswith(".log"):
            element.set("fileName", output_file.replace(".xml", ".log"))
        if filename.endswith(".trees"):
            element.set("fileName", output_file.replace(".xml", ".trees"))

    # remove comment
    # <!-- The error model -->
    for x in root:
        if x.tag is etree.Comment:
            if "error" in str(x):
                root.remove(x)

    # strip extra spaces from namespace
    root.set("namespace", root.get("namespace").strip())
    # write xml
    etree.indent(root)
    output_handle = open(output_file, "wb")
    output_handle.write(etree.tostring(root))


# transform xmls to new format
for i in range(1, 101):
    infile = "../../sim1/data/binary_yule_N200_L400_%d.xml" % i
    basename = os.path.basename(infile)
    outfile = basename.replace("N200", "n30")
    old_yule_to_new_template(infile, outfile)
