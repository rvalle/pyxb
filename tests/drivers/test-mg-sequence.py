import pyxb.binding.generate
import pyxb.utils.domutils
from xml.dom import Node

import os.path
schema_path = '%s/../schemas/test-mg-sequence.xsd' % (os.path.dirname(__file__),)
code = pyxb.binding.generate.GeneratePython(schema_file=schema_path)

rv = compile(code, 'test', 'exec')
eval(rv)

from pyxb.exceptions_ import *

from pyxb.utils import domutils
def ToDOM (instance, tag=None):
    dom_support = domutils.BindingDOMSupport()
    parent = None
    if tag is not None:
        parent = dom_support.document().appendChild(dom_support.document().createElement(tag))
    dom_support = instance.toDOM(dom_support, parent)
    return dom_support.finalize().documentElement

import unittest

class TestMGSeq (unittest.TestCase):
    def testBad (self):
        # Second is wrong element tag
        xml = '<wrapper xmlns="URN:test-mg-sequence"><first/><second/><third/><fourth_0_2/></wrapper>'
        dom = pyxb.utils.domutils.StringToDOM(xml)
        self.assertRaises(UnrecognizedContentError, wrapper.CreateFromDOM, dom.documentElement)

    def testBasics (self):
        xml = '<wrapper xmlns="URN:test-mg-sequence"><first/><second_opt/><third/><fourth_0_2/></wrapper>'
        dom = pyxb.utils.domutils.StringToDOM(xml)
        instance = wrapper.CreateFromDOM(dom.documentElement)
        self.assert_(isinstance(instance.first(), sequence_first))
        self.assert_(isinstance(instance.second_opt(), sequence_second_opt))
        self.assert_(isinstance(instance.third(), sequence_third))
        self.assert_(isinstance(instance.fourth_0_2(), list))
        self.assertEqual(1, len(instance.fourth_0_2()))
        self.assert_(isinstance(instance.fourth_0_2()[0], sequence_fourth_0_2))
        self.assertEqual(xml, ToDOM(instance).toxml())

    def testMultiplesAtEnd (self):
        xml = '<wrapper xmlns="URN:test-mg-sequence"><first/><third/><fourth_0_2/><fourth_0_2/></wrapper>'
        dom = pyxb.utils.domutils.StringToDOM(xml)
        instance = wrapper.CreateFromDOM(dom.documentElement)
        self.assert_(isinstance(instance.first(), sequence_first))
        self.assert_(instance.second_opt() is None)
        self.assert_(isinstance(instance.third(), sequence_third))
        self.assert_(isinstance(instance.fourth_0_2(), list))
        self.assertEqual(2, len(instance.fourth_0_2()))
        self.assert_(isinstance(instance.fourth_0_2()[0], sequence_fourth_0_2))
        self.assertEqual(xml, ToDOM(instance).toxml())

    def testMultiplesInMiddle (self):
        xml = '<altwrapper xmlns="URN:test-mg-sequence"><first/><second_multi/><second_multi/><third/></altwrapper>'
        dom = pyxb.utils.domutils.StringToDOM(xml)
        instance = altwrapper.CreateFromDOM(dom.documentElement)
        self.assert_(isinstance(instance.first(), list))
        self.assertEqual(1, len(instance.first()))
        self.assertEqual(2, len(instance.second_multi()))
        self.assert_(isinstance(instance.third(), altsequence_third))
        self.assertEqual(xml, ToDOM(instance).toxml())

    def testMultiplesAtStart (self):
        xml = '<altwrapper xmlns="URN:test-mg-sequence"><first/><first/><third/></altwrapper>'
        dom = pyxb.utils.domutils.StringToDOM(xml)
        instance = altwrapper.CreateFromDOM(dom.documentElement)
        self.assert_(isinstance(instance.first(), list))
        self.assertEqual(2, len(instance.first()))
        self.assertEqual(0, len(instance.second_multi()))
        self.assert_(isinstance(instance.third(), altsequence_third))
        self.assertEqual(xml, ToDOM(instance).toxml())

    def testMissingInMiddle (self):
        xml = '<wrapper xmlns="URN:test-mg-sequence"><first/><third/></wrapper>'
        dom = pyxb.utils.domutils.StringToDOM(xml)
        instance = wrapper.CreateFromDOM(dom.documentElement)
        self.assert_(isinstance(instance.first(), sequence_first))
        self.assert_(instance.second_opt() is None)
        self.assert_(isinstance(instance.third(), sequence_third))
        self.assert_(isinstance(instance.fourth_0_2(), list))
        self.assertEqual(0, len(instance.fourth_0_2()))
        self.assertEqual(xml, ToDOM(instance).toxml())

    def testMissingAtStart (self):
        xml = '<altwrapper xmlns="URN:test-mg-sequence"><third/></altwrapper>'
        dom = pyxb.utils.domutils.StringToDOM(xml)
        self.assertRaises(UnrecognizedContentError, altwrapper.CreateFromDOM, dom.documentElement)

    def testMissingAtEndLeadingContent (self):
        xml = '<altwrapper xmlns="URN:test-mg-sequence"><first/></altwrapper>'
        dom = pyxb.utils.domutils.StringToDOM(xml)
        self.assertRaises(MissingContentError, altwrapper.CreateFromDOM, dom.documentElement)

    def testMissingAtEndNoContent (self):
        xml = '<altwrapper xmlns="URN:test-mg-sequence"></altwrapper>'
        dom = pyxb.utils.domutils.StringToDOM(xml)
        self.assertRaises(MissingContentError, altwrapper.CreateFromDOM, dom.documentElement)

    def testTooManyAtEnd (self):
        xml = '<wrapper xmlns="URN:test-mg-sequence"><first/><third/><fourth_0_2/><fourth_0_2/><fourth_0_2/></wrapper>'
        dom = pyxb.utils.domutils.StringToDOM(xml)
        self.assertRaises(ExtraContentError, wrapper.CreateFromDOM, dom.documentElement)

    def testTooManyAtStart (self):
        xml = '<altwrapper xmlns="URN:test-mg-sequence"><first/><first/><first/><third/></altwrapper>'
        dom = pyxb.utils.domutils.StringToDOM(xml)
        self.assertRaises(UnrecognizedContentError, altwrapper.CreateFromDOM, dom.documentElement)

    def testTooManyInMiddle (self):
        xml = '<altwrapper xmlns="URN:test-mg-sequence"><second_multi/><second_multi/><second_multi/><third/></altwrapper>'
        dom = pyxb.utils.domutils.StringToDOM(xml)
        self.assertRaises(UnrecognizedContentError, altwrapper.CreateFromDOM, dom.documentElement)


if __name__ == '__main__':
    unittest.main()
    
        
