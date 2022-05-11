import os

from lxml import etree


def transform(input_file, output_file):
    tree = etree.parse(input_file)
    root = tree.getroot()
    root.set("namespace", root.get("namespace").strip())

    # error parameter state nodes
    for element in root.iter("state"):
        # delta state
        sub_element = etree.Element("parameter")
        sub_element.set("id", "delta")
        sub_element.set("spec", "parameter.RealParameter")
        sub_element.set("lower", "0.0")
        sub_element.set("upper", "1.0")
        sub_element.set("name", "stateNode")
        sub_element.text = "0.5"
        element.append(sub_element)
        # epsilon state
        sub_element = etree.Element("parameter")
        sub_element.set("id", "epsilon")
        sub_element.set("spec", "parameter.RealParameter")
        sub_element.set("lower", "0.0")
        sub_element.set("upper", "1.0")
        sub_element.set("name", "stateNode")
        sub_element.text = "0.01"
        element.append(sub_element)

    # error parameter priors
    for element in root.iter("distribution"):
        eid = element.get("id")
        if eid == "prior":
            # add delta prior
            dist_element = etree.Element("distribution")
            dist_element.set("id", "delta.prior")
            dist_element.set("spec", "beast.math.distributions.Prior")
            dist_element.set("x", "@delta")
            #  beta prior
            beta_element = etree.Element("distr")
            beta_element.set("id", "Beta123")
            beta_element.set("spec", "beast.math.distributions.Beta")
            # beta param 1
            param = etree.Element("parameter")
            param.set("id", "RealParameter123")
            param.set("spec", "parameter.RealParameter")
            param.set("name", "alpha")
            param.text = "1.5"
            beta_element.append(param)
            # beta param 2
            param2 = etree.Element("parameter")
            param2.set("id", "RealParameter456")
            param2.set("spec", "parameter.RealParameter")
            param2.set("name", "beta")
            param2.text = "4.5"
            beta_element.append(param2)
            dist_element.append(beta_element)
            element.append(dist_element)

            # add epsilon prior
            dist_element = etree.Element("distribution")
            dist_element.set("id", "epsilon.prior")
            dist_element.set("spec", "beast.math.distributions.Prior")
            dist_element.set("x", "@epsilon")
            #  beta prior
            beta_element = etree.Element("distr")
            beta_element.set("id", "Beta234")
            beta_element.set("spec", "beast.math.distributions.Beta")
            # beta param 1
            param = etree.Element("parameter")
            param.set("id", "RealParameter234")
            param.set("spec", "parameter.RealParameter")
            param.set("name", "alpha")
            param.text = "2.0"
            beta_element.append(param)
            # beta param 2
            param2 = etree.Element("parameter")
            param2.set("id", "RealParameter567")
            param2.set("spec", "parameter.RealParameter")
            param2.set("name", "beta")
            param2.text = "18.0"
            beta_element.append(param2)
            dist_element.append(beta_element)
            element.append(dist_element)

    # operators
    # locate theta scale operator position
    contentnav = tree.find(".//operator[@id=\"theta.scale\"]")
    # add delta operator
    contentnav.addnext(etree.XML("<operator id=\"delta.scale\" spec=\"ScaleOperator\" "
                                 "parameter=\"@delta\" weight=\"1.0\"/>"))
    # add epsilon operator
    contentnav.addnext(etree.XML("<operator id=\"epsilon.scale\" spec=\"ScaleOperator\" "
                                 "parameter=\"@epsilon\" weight=\"1.0\"/>"))

    # replace error model
    for element in root.iter("errorModel"):
        element.clear()
        element.set("id", "GT16ErrorModel")
        element.set("spec", "phylonco.beast.evolution.errormodel.GT16ErrorModel")
        element.set("delta", "@delta")
        element.set("epsilon", "@epsilon")
        sub_element = etree.Element("datatype")
        sub_element.set("id", "NucleotideDiploid16")
        sub_element.set("spec", "beast.evolution.datatype.NucleotideDiploid16")
        element.append(sub_element)

    # loggers for error parameters
    for element in root.iter("logger"):
        filename = str(element.get("fileName"))
        if filename.endswith(".log"):
            # add delta and epsilon loggers
            sub_element = etree.Element("log")
            sub_element.set("idref", "delta")
            element.append(sub_element)
            sub_element = etree.Element("log")
            sub_element.set("idref", "epsilon")
            element.append(sub_element)

    etree.indent(root)
    output_handle = open(output_file, "wb")
    output_handle.write(etree.tostring(root))


# process files
delta_values = ["0", "10", "25", "50", "80"]
for i in delta_values:
    for j in range(20):
        infile = "gt16_delta/gt16_delta_%s_%d.xml" % (i, j)
        if not os.path.exists(infile + ".temp"):
            outfile = infile + ".new"
            transform(infile, outfile)
            os.rename(infile, infile + ".temp")
            os.rename(outfile, infile)

epsilon_values = ["0", "0.1", "1", "5", "10"]
for i in epsilon_values:
    for j in range(20):
        infile = "gt16_epsilon/gt16_epsilon_%s_%d.xml" % (i, j)
        if not os.path.exists(infile + ".temp"):
            outfile = infile + ".new"
            transform(infile, outfile)
            os.rename(infile, infile + ".temp")
            os.rename(outfile, infile)
