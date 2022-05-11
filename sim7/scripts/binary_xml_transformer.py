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


# transform xmls to new format
reps = 20
for beta in ["0", "10", "25", "50", "60"]:
    for i in range(1, reps + 1):
        infile = "../data/binary_beta/binary_beta_%s_%d.xml.temp" % (beta, i)
        basename = os.path.basename(infile)
        outfile = basename.replace(".temp", "")
        old_yule_to_new_template(infile, outfile)
        if os.path.exists(outfile):
            print("Output BEAST2 xml: %s" % outfile)
            output_dir = os.path.dirname(infile)
            os.rename(outfile, os.path.join(output_dir, outfile))
            os.remove(infile)  # remove temp xml

for alpha in ["0", "0.1", "1", "5", "10"]:
    for i in range(1, reps + 1):
        infile = "../data/binary_alpha/binary_alpha_%s_%d.xml.temp" % (alpha, i)
        basename = os.path.basename(infile)
        outfile = basename.replace(".temp", "")
        old_yule_to_new_template(infile, outfile)
        if os.path.exists(outfile):
            print("Output BEAST2 xml: %s" % outfile)
            output_dir = os.path.dirname(infile)
            os.rename(outfile, os.path.join(output_dir, outfile))
            os.remove(infile)  # remove temp xml

