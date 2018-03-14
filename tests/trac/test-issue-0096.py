# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import pyxb.binding.generate
import pyxb.utils.domutils


if __name__ == '__main__':
    logging.basicConfig()
_log = logging.getLogger(__name__)

xsd = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" elementFormDefault="qualified"
  targetNamespace="http://opennebula.org/XMLSchema" xmlns="http://opennebula.org/XMLSchema">
  <xs:element name="VROUTER">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="ID" type="xs:integer"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
  <xs:element name="VM">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="ID" type="xs:integer"/>
        <xs:element name="USER_TEMPLATE" type="xs:anyType"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
'''

xmlSample = '''<?xml version="1.0" encoding="UTF-8"?>
<VM xmlns="http://opennebula.org/XMLSchema">
  <ID>4010</ID>
  <USER_TEMPLATE>
    <VROUTER><![CDATA[yes]]></VROUTER>
  </USER_TEMPLATE>
</VM>
'''

code = pyxb.binding.generate.GeneratePython(schema_text=xsd)

rv = compile(code, 'test', 'exec')
eval(rv)

import unittest

class TestIssue0096 (unittest.TestCase):

    def testXmlDocument (self):
        doc = CreateFromDocument(xmlSample);
        self.assertEqual(doc.ID,4010)

if __name__ == '__main__':
    unittest.main()
