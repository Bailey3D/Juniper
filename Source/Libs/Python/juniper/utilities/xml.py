"""
Module of various XML utility functions
"""
import xml.etree.ElementTree


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
