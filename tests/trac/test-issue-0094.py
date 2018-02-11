# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import pyxb.binding.generate
import pyxb.utils.domutils
import xml.dom.minidom as dom


if __name__ == '__main__':
    logging.basicConfig()
_log = logging.getLogger(__name__)

xsd = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" elementFormDefault="qualified"
  targetNamespace="http://opennebula.org/XMLSchema" xmlns="http://opennebula.org/XMLSchema">
  <xs:element name="MARKETPLACE">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="ID" type="xs:integer"/>
        <xs:element name="UID" type="xs:integer"/>
        <xs:element name="GID" type="xs:integer"/>
        <xs:element name="UNAME" type="xs:string"/>
        <xs:element name="GNAME" type="xs:string"/>
        <xs:element name="NAME" type="xs:string"/>
        <xs:element name="MARKET_MAD" type="xs:string"/>
        <xs:element name="ZONE_ID" type="xs:string"/>
        <xs:element name="TOTAL_MB" type="xs:integer"/>
        <xs:element name="FREE_MB" type="xs:integer"/>
        <xs:element name="USED_MB" type="xs:integer"/>
        <xs:element name="MARKETPLACEAPPS">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="ID" type="xs:integer" minOccurs="0" maxOccurs="unbounded"/>
            </xs:sequence>
          </xs:complexType>
        </xs:element>
        <xs:element name="PERMISSIONS" minOccurs="0" maxOccurs="1">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="OWNER_U" type="xs:integer"/>
              <xs:element name="OWNER_M" type="xs:integer"/>
              <xs:element name="OWNER_A" type="xs:integer"/>
              <xs:element name="GROUP_U" type="xs:integer"/>
              <xs:element name="GROUP_M" type="xs:integer"/>
              <xs:element name="GROUP_A" type="xs:integer"/>
              <xs:element name="OTHER_U" type="xs:integer"/>
              <xs:element name="OTHER_M" type="xs:integer"/>
              <xs:element name="OTHER_A" type="xs:integer"/>
            </xs:sequence>
          </xs:complexType>
        </xs:element>
        <xs:element name="TEMPLATE" type="xs:anyType"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
  <xs:element name="MARKETPLACE_POOL">
    <xs:complexType>
        <xs:sequence maxOccurs="1" minOccurs="1">
            <xs:element ref="MARKETPLACE" maxOccurs="unbounded" minOccurs="0"/>
        </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
'''

nakedXmlSample = '''<MARKETPLACE_POOL><MARKETPLACE><ID>0</ID><UID>0</UID><GID>0</GID><UNAME>oneadmin</UNAME><GNAME>oneadmin</GNAME><NAME>OpenNebula Public</NAME><MARKET_MAD><![CDATA[one]]></MARKET_MAD><ZONE_ID><![CDATA[0]]></ZONE_ID><TOTAL_MB>0</TOTAL_MB><FREE_MB>0</FREE_MB><USED_MB>0</USED_MB><MARKETPLACEAPPS><ID>0</ID><ID>1</ID><ID>2</ID><ID>3</ID><ID>4</ID><ID>5</ID><ID>6</ID><ID>7</ID><ID>8</ID><ID>9</ID><ID>10</ID><ID>11</ID><ID>12</ID><ID>13</ID><ID>14</ID><ID>15</ID><ID>16</ID><ID>17</ID><ID>18</ID><ID>19</ID><ID>20</ID><ID>21</ID><ID>22</ID><ID>23</ID><ID>24</ID></MARKETPLACEAPPS><PERMISSIONS><OWNER_U>1</OWNER_U><OWNER_M>1</OWNER_M><OWNER_A>1</OWNER_A><GROUP_U>1</GROUP_U><GROUP_M>0</GROUP_M><GROUP_A>0</GROUP_A><OTHER_U>1</OTHER_U><OTHER_M>0</OTHER_M><OTHER_A>0</OTHER_A></PERMISSIONS><TEMPLATE><DESCRIPTION><![CDATA[OpenNebula Systems MarketPlace]]></DESCRIPTION><MARKET_MAD><![CDATA[one]]></MARKET_MAD></TEMPLATE></MARKETPLACE></MARKETPLACE_POOL>'''

xmlSample = '''<MARKETPLACE_POOL xmlns='http://opennebula.org/XMLSchema'><MARKETPLACE><ID>0</ID><UID>0</UID><GID>0</GID><UNAME>oneadmin</UNAME><GNAME>oneadmin</GNAME><NAME>OpenNebula Public</NAME><MARKET_MAD><![CDATA[one]]></MARKET_MAD><ZONE_ID><![CDATA[0]]></ZONE_ID><TOTAL_MB>0</TOTAL_MB><FREE_MB>0</FREE_MB><USED_MB>0</USED_MB><MARKETPLACEAPPS><ID>0</ID><ID>1</ID><ID>2</ID><ID>3</ID><ID>4</ID><ID>5</ID><ID>6</ID><ID>7</ID><ID>8</ID><ID>9</ID><ID>10</ID><ID>11</ID><ID>12</ID><ID>13</ID><ID>14</ID><ID>15</ID><ID>16</ID><ID>17</ID><ID>18</ID><ID>19</ID><ID>20</ID><ID>21</ID><ID>22</ID><ID>23</ID><ID>24</ID></MARKETPLACEAPPS><PERMISSIONS><OWNER_U>1</OWNER_U><OWNER_M>1</OWNER_M><OWNER_A>1</OWNER_A><GROUP_U>1</GROUP_U><GROUP_M>0</GROUP_M><GROUP_A>0</GROUP_A><OTHER_U>1</OTHER_U><OTHER_M>0</OTHER_M><OTHER_A>0</OTHER_A></PERMISSIONS><TEMPLATE><DESCRIPTION><![CDATA[OpenNebula Systems MarketPlace]]></DESCRIPTION><MARKET_MAD><![CDATA[one]]></MARKET_MAD></TEMPLATE></MARKETPLACE></MARKETPLACE_POOL>'''


code = pyxb.binding.generate.GeneratePython(schema_text=xsd)

rv = compile(code, 'test', 'exec')
eval(rv)

import unittest

class TestIssue0094 (unittest.TestCase):

    def testXmlDocument (self):
        doc = CreateFromDocument(xmlSample);
        self.assertEqual(doc.MARKETPLACE[0].NAME, "OpenNebula Public")

    def testNakedXmlDocument (self):
        doc = CreateFromDocument(nakedXmlSample);
        self.assertEqual(doc.MARKETPLACE[0].NAME, "OpenNebula Public")

    def testNakedXmlDocumentWithDefaultNamespace (self):
        doc = CreateFromDocument(nakedXmlSample, default_namespace = Namespace);
        self.assertEqual(doc.MARKETPLACE[0].NAME, "OpenNebula Public")

if __name__ == '__main__':
    unittest.main()
