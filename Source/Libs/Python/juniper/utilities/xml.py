"""
Module of various XML utility functions
"""
import xml
import xml.etree.ElementTree
import xml.dom.minidom as minidom


def prettify(elem):
    """
    Prettify an XML Element
    :param <XMLElement:element> The element to prettify
    :return <XMLElement:output> Reparsed element
    """
    elem.text = ""
    elem.tail = ""
    for node in elem:
        for sub_node in node:
            sub_node.tail = ""
            if((sub_node.text is None) or (sub_node.text.isspace())):
                sub_node.text = ""
        if((node.text is None) or (node.text.isspace())):
            node.text = ""
        node.tail = ""

        rough_string = xml.etree.ElementTree.tostring(elem)
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


def get_or_create_sub_element(parent_element, element_name):
    """
    Returns eitherthe first found instance of a SubElement  - or creates a new one with the given name
    :param <XmlElement:parent_element> The parent element to search/add to
    :param <str:element_name> The name of the element key to find
    :return <XmlElement:sub_element> The existing SubElement if found - else the newly created SubElement
    """
    output = parent_element.find(element_name)
    if(output is None):
        output = xml.etree.ElementTree.SubElement(parent_element, element_name)
    return output


def add_element(target_element, element_name, *keyvals):
    """
    Adds an element to the input xml element
    :param <xmlElement:target_element> The parent element to add this child to
    :param <str:element_name> The name of the new child element
    :param <[string]:*keyvals> Array of keys/values for this element (Ie, [key1, value1, key2, value2])
    :return <xmlElement:output> The new element as added to the parent xml element
    """
    output = xml.etree.ElementTree.SubElement(target_element, element_name)
    for i in range(0, len(keyvals), 2):
        output.set(str(keyvals[i]), str(keyvals[i + 1]))
    return output


def save(path, xml_doc):
    """
    Saves out an input xml document to a given filepath
    :param <str:path> Path to export this file to
    :param <ElementTree:xml_doc> Xml document to export
    """
    final_xml_string = xml.etree.ElementTree.tostring(xml_doc.getroot(), method="xml", encoding="utf-8")
    final_xml_string = minidom.parseString(final_xml_string)
    final_xml_string = final_xml_string.toprettyxml(encoding="utf-8")
    with open(path, "w+") as f:
        f.write(final_xml_string)
