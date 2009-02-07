"""XMLSchema bindings 

These bindings are hand-written to support the XMSchema namespace.
Maybe, if the generated code is good enough, they'll be replaced by
bindings that are generated.

"""

import PyWXSB.Namespace as Namespace

import structures as xsc

import datatypes as xsd

from PyWXSB.exceptions_ import *

from xml.dom import Node
import sys
import types

# Hand-written classes used to get to the point where we can subclass
# generated bindings.

class schemaTop (xsc.ModelGroup):
    def __init__ (self, *args, **kw):
        super(schemaTop, self).__init__(*args, **kw)

    @classmethod
    def Match (cls, wxs, node):
        rv = redefinable.Match(wxs, node)
        if rv is not None:
            return rv
        if wxs.xsQualifiedName('element') == node.nodeName:
            return wxs._processElementDeclaration(node)
        if wxs.xsQualifiedName('attribute') == node.nodeName:
            return wxs._processAttributeDeclaration(node)
        if wxs.xsQualifiedName('notation') == node.nodeName:
            print "WARNING: Ignoring notation"
            return node
        return None

class redefinable (xsc.ModelGroup):
    def __init__ (self, *args, **kw):
        super(redefinable, self).__init__(*args, **kw)

    @classmethod
    def Match (cls, wxs, node):
        if wxs.xsQualifiedName('simpleType') == node.nodeName:
            return wxs._processSimpleType(node)
        if wxs.xsQualifiedName('complexType') == node.nodeName:
            return wxs._processComplexType(node)
        if wxs.xsQualifiedName('group') == node.nodeName:
            return wxs._processGroup(node)
        if wxs.xsQualifiedName('attributeGroup') == node.nodeName:
            return wxs._processAttributeGroup(node)
        return None

class schema (xsc.Schema):
    """Class corresponding to a W3C XML Schema instance.

    This class is a subclass of the corresponding schema component.
    """
    
    __domRootNode = None
    __pastProlog = False

    # A set of namespace instances referenced by this schema.
    # Namespaces cannot be removed from this set.
    __namespaces = None

    # Map from a prefix to the namespace it represents in this schema.
    # Namespaces with bound prefixes cannot be reassigned, and the
    # prefix associated with a namespace cannot change.  This is
    # prefix->Namespace, not prefix->URI.
    __prefixToNamespaceMap = None

    # Reverse direction: given a Namespace instance, determine the
    # prefix used for that namespace.
    __namespaceToPrefixMap = None

    # Map from the namespace URI to the instance that represents it
    # @todo redundant with Namespace registry
    __namespaceURIMap = None    # Map from URI to a namespace instance

    # Namespaces bound per Namespaces in XML 1.0 (Second Edition) (http://www.w3.org/TR/xml-names/)
    __xml = None                # http://www.w3.org/XML/1998/namespace
    __xmlns = None              # http://www.w3.org/2000/xmlns/

    # Namespaces relevant to XMLSchema; xsi is bound (see
    # http://www.w3.org/TR/xmlschema-1/#no-xsi)
    __xs = None                 # http://www.w3.org/2001/XMLSchema
    __xsi = None                # http://www.w3.org/2001/XMLSchema-instance

    # Default namespace for current schema.  Will be None unless
    # schema has an 'xmlns' attribute.
    __defaultNamespace = None 

    # Target namespace for current schema.  Will be None unless schema
    # has a 'targetNamespace' attribute.
    __targetNamespace = None

    def __init__ (self):
        xsc.Schema.__init__(self)
        self.__namespaces = set()
        self.__namespaceToPrefixMap = { }
        self.__prefixToNamespaceMap = { }

        self.__namespaceURIMap = { }
        self.__addNamespace(Namespace.XML)
        self.__xs = Namespace.XMLSchema
        self.__addNamespace(self.__xs)

    def initializeBuiltins (self):
        # If there's a target namespace, use this as its schema
        if self.__targetNamespace:
            self.__targetNamespace.schema(self)

        # If we're targeting the XMLSchema namespace, define the
        # built-in types.  Otherwise, allocate and associate a schema
        # instance for the XMLSchema namespace so we get access to
        # those built-in types.
        if self.__xs == self.__targetNamespace:
            xsd.DefineSimpleTypes(self)
        else:
            self.__xs.schema(SchemaForXS(self))

    def __getNamespaceForLookup (self, type_name):
        """Resolve a QName or NCName appropriately for this schema.

        Returns the namespace to be used for lookup, or None if the
        schema is associated with the lookup nnamespace.
        """
        ns = None
        local_name = type_name
        if 0 <= type_name.find(':'):
            ( prefix, local_name ) = type_name.split(':', 1)
            ns = self.namespaceForPrefix(prefix)
        elif (self.__defaultNamespace is not None) and (self.__defaultNamespace != self.__targetNamespace):
            raise LogicError('This code is wrong if a namespace instance is doing the lookup')
            #ns = self.__defaultNamespace
        print 'Namespace %s used for %s in %s' % (ns, local_name, type_name)
        if (ns is None) and (self.__defaultNamespace is not None) and (self.__defaultNamespace != self.__targetNamespace):
            raise LogicError('This code is wrong if a namespace instance is doing the lookup')
        return (ns, local_name)

    def lookupType (self, type_name):
        (ns, local_name) = self.__getNamespaceForLookup(type_name)
        assert 0 > local_name.find(':')
        if ns is not None:
            rv = ns.lookupType(local_name)
        # Invoke superclass lookup
        rv = self._lookupTypeDefinition(local_name)
        if rv is None:
            raise Exception('lookupType: No match for "%s" in %s' % (local_name, self.__targetNamespace))
        return rv

    def lookupSimpleType (self, type_name):
        rv = self.lookupType(type_name)
        if isinstance(rv, xsc.SimpleTypeDefinition):
            return rv
        raise Exception('lookupSimpleType: Name "%s" in %s is not a simple type' % (local_name, self.__targetNamespace))

    def lookupAttributeGroup (self, ref_name):
        (ns, local_name) = self.__getNamespaceForLookup(ref_name)
        if ns is not None:
            return ns.lookupAttributeGroup(local_name)
        rv = self._lookupAttributeGroupDefinition(local_name)
        if rv is None:
            raise SchemaValidationError('lookupAttributeGroup: No match for "%s" in %s' % (local_name, self.__targetNamespace))
        return rv

    def lookupAttributeDeclaration (self, ref_name):
        (ns, local_name) = self.__getNamespaceForLookup(ref_name)
        if ns is not None:
            return ns.lookupAttributeDeclaration(local_name)
        rv = self._lookupAttributeDeclaration(local_name)
        if rv is None:
            raise SchemaValidationError('lookupAttributeDeclaration: No match for "%s" in %s' % (local_name, self.__targetNamespace))
        return rv

    def lookupGroup (self, group_name):
        (ns, local_name) = self.__getNamespaceForLookup(group_name)
        if ns is not None:
            return ns.lookupGroup(local_name)
        rv = self._lookupModelGroupDefinition(local_name)
        if rv is None:
            raise SchemaValidationError('lookupGroup: No match for "%s" in %s' % (local_name, self.__targetNamespace))
        return rv

    def lookupElement (self, element_name):
        (ns, local_name) = self.__getNamespaceForLookup(element_name)
        if ns is not None:
            return ns.lookupElement(local_name)
        rv = self._lookupElementDeclaration(local_name)
        if rv is None:
            raise SchemaValidationError('lookupElement: No match for "%s" in %s' % (local_name, self.__targetNamespace))
        return rv

    def __recordNamespacePrefix (self, prefix, namespace):
        """Associate the given prefix with the given namespace in this schema.

        If the prefix is None, this call has no effect.  If the
        namespace is None, or has already been associated with a
        prefix, an exception will be thrown.

        This differs from __addNamespace in that  it is assumed the
        namespace has already been associated with the schema; it is
        just that the prefix is now known.
        """
        # @todo Recording and association cannot be separated
        assert namespace is not None
        if prefix is None:
            return
        if prefix in self.__prefixToNamespaceMap:
            raise LogicError('Prefix %s already associated with %s' % (prefix, namespace))
        old_prefix = self.__namespaceToPrefixMap.get(namespace, None)
        if old_prefix is not None:
            # This is not a LogicError because I'm not convinced doing this
            # isn't legal.  Even if it does seem a little nonsensical.
            raise IncompleteImplementationError('Namespace %s cannot have multiple prefixes (%s, %s)' % (namespace, prefix, old_prefix))
        print 'schema for %s maps %s to %s' % (self.getTargetNamespace(), prefix, namespace)
        self.__prefixToNamespaceMap[prefix] = namespace
        self.__namespaceToPrefixMap[namespace] = prefix

    def __addNamespace (self, namespace, prefix=None):
        assert namespace not in self.__namespaces
        self.__namespaces.add(namespace)
        self.__namespaceURIMap[namespace.uri()] = namespace
        if prefix is None:
            prefix = namespace.boundPrefix()
        if prefix is not None:
            self.__recordNamespacePrefix(prefix, namespace)
        return namespace

    def lookupOrCreateNamespace (self, uri, prefix=None):
        # NB: This can replace the prefix if it changed since creation
        print '%s LOOKUP Associate %s with %s' % (self, prefix, uri)
        namespace = Namespace.NamespaceForURI(uri)
        if namespace is None:
            namespace = Namespace.Namespace(uri)
            self.__addNamespace(namespace)
        if prefix is not None:
            self.__recordNamespacePrefix(prefix, namespace)
        return namespace

    def setDefaultNamespace (self, namespace):
        """Specify the namespace that should be used for non-qualified
        lookups.  """
        print 'DEFAULT: %s' % (namespace,)
        self.__defaultNamespace = namespace
        return namespace

    def getDefaultNamespace (self):
        return self.__defaultNamespace

    def setTargetNamespace (self, namespace):
        """Specify the namespace for which this schema provides
        information."""
        print 'TARGET: %s' % (namespace,)
        self.__targetNamespace = namespace
        return namespace

    def getTargetNamespace (self):
        return self.__targetNamespace

    def targetNamespaceFromDOM (self, node, default_tag):
        """Determine the approprate namespace for a local
        attribute/element in the schema.

        This takes the appropriate schema-level attribute default
        value (identified by the given tag) from the schema,
        potentially overrides it from an attribute in the node, then
        returns either this schema's target namespace or None.  See
        any discussion of the targetNamespace property in the
        component specification.
        """
        # Failure to provide a valid tag for the default is a
        # programmer error.  There's only two; surely you can get that
        # many right.  Oh, hell, probably not...
        assert default_tag in [ 'attributeFormDefault', 'elementFormDefault' ]
        assert self.hasAttribute(default_tag)
        form = self.getAttribute(default_tag)
        assert form is not None
        if node.hasAttribute('form'):
            form = node.getAttribute('form')
        if not form in [ 'qualified', 'unqualified' ]:
            raise SchemaValidationError('form attribute must be "qualified" or "unqualified"')
        if 'qualifled' == form:
            return self.getTargetNamespace()
        return None

    def targetPrefix (self):
        if self.__targetNamespace:
            return self.__targetNamespace.prefix()
        return None

    def namespaceForURI (self, uri):
        """Return the namespace for the URI.

        Throws an exception if the namespace has not been associated
        with this schema (must be done by processing an xmlns
        attribute)."""
        if self.__namespaceURIMap.has_key(uri):
            return self.__namespaceURIMap[uri]
        raise SchemaValidationError('Namespace "%s" not recognized' % (uri,))

    def namespaceForPrefix (self, prefix):
        """Return the namespace associated with the given prefix in this schema.

        The prefix must be a non-empty string associated with a
        namespace through an xmlns attribute in the schema element."""
        if self.__prefixToNamespaceMap.has_key(prefix):
            return self.__prefixToNamespaceMap.get(prefix, None)
        raise Exception('Namespace prefix "%s" not recognized' % (prefix,))

    def prefixForNamespace (self, namespace):
        """Return the prefix used in this schema for the given namespace.

        If the namespace was not assigned a prefix in this schema,
        returns None."""
        assert isinstance(namespace, Namespace.Namespace)
        return self.__namespaceToPrefixMap.get(namespace, None)

    def qualifiedName (self, nc_name, namespace=None):
        """Return a namespace-qualified name for the given NCName in
        the optionally-specified namespace.

        If no namespace is provided, the target namespace will be
        used.  If the namespace is the default namespace for this
        schema, the NCName is returned without qualifying it."""

        if namespace is None:
            namespace = self.getTargetNamespace()
        if namespace is None:
            raise LogicError('Cannot get qualified name for %s without namespace.' % (nc_name,))

        if self.getDefaultNamespace() == namespace:
            return nc_name

        prefix = self.prefixForNamespace(namespace)
        if prefix is None:
            raise LogicError('Namespace %s has no prefix in schema to qualify name "%s"' % (namespace.uri(), nc_name))
        return '%s:%s' % (prefix, nc_name)

    def xsQualifiedName (self, nc_name):
        """Returns a name in the XMLSchema, qualified appropriately
        for this schema.

        @note A schema that uses XMLSchema as its default namespace
        will produce an NCName.
        """
        return self.qualifiedName(nc_name, self.xs())

    # @todo put these in base class
    def processDocument (self, doc):
        """Take the root element of the document, and scan its attributes under
        the assumption it is an XMLSchema schema element.  That means
        recognize namespace declarations and process them.  Also look for
        and set the default namespace.  All other attributes are passed up
        to the parent class for storage."""
        default_namespace = None
        root_node = doc.documentElement
        for attr in root_node.attributes.values():
            if 'xmlns' == attr.prefix:
                print 'Created namespace %s for %s' % (attr.nodeValue, attr.localName)
                self.lookupOrCreateNamespace(attr.nodeValue, attr.localName)
            elif 'xmlns' == attr.name:
                default_namespace = attr.nodeValue
            else:
                self._setAttributeFromDOM(attr)
        if default_namespace is not None:
            # TODO: Is it required that the default namespace be recognized?
            # Does not hold for http://www.w3.org/2001/xml.xsd
            ns = self.lookupOrCreateNamespace(default_namespace)
            #ns = self.namespaceForURI(default_namespace)
            self.setDefaultNamespace(ns)

        # Apply the targetNamespace attribute.  There is a default,
        # which is to have no associated namespace.
        assert self.hasAttribute('targetNamespace')
        target_namespace = self.getAttribute('targetNamespace')
        if target_namespace is not None:
            self.setTargetNamespace(self.lookupOrCreateNamespace(target_namespace))

        # Now install all the standard types, including fleshing out
        # the xs() namespace schema.
        self.initializeBuiltins()

        # Verify that the root node is an XML schema element
        if self.xsQualifiedName('schema') != root_node.nodeName:
            raise SchemaValidationError('Root node %s of document is not an XML schema element' % (root_node.nodeName,))

        self.__domRootNode = root_node

        for cn in root_node.childNodes:
            if Node.ELEMENT_NODE == cn.nodeType:
                rv = self.processTopLevelNode(cn)
                if rv is None:
                    print 'Unrecognized: %s' % (cn.nodeName,)
            elif Node.TEXT_NODE == cn.nodeType:
                # Non-element content really should just be whitespace.
                # If something else is seen, print it for inspection.
                text = cn.data.strip()
                if text:
                    print 'Ignored text: %s' % (text,)
            elif Node.COMMENT_NODE == cn.nodeType:
                #print 'comment: %s' % (cn.data.strip(),)
                pass
            else:
                # ATTRIBUTE_NODE
                # CDATA_SECTION_NODE
                # ENTITY_NODE
                # PROCESSING_INSTRUCTION
                # DOCUMENT_NODE
                # DOCUMENT_TYPE_NODE
                # NOTATION_NODE
                print 'Ignoring non-element: %s' % (cn,)

        self._resolveDefinitions()

        return self

    def reset (self):
        self.__pastProlog = False

    def _requireInProlog (self, node_name):
        """Throw a SchemaValidationException referencing the given
        node if we have passed the sequence point representing the end
        of prolog elements."""
        if self.__pastProlog:
            raise SchemaValidationError('Unexpected node %s after prolog' % (node_name,))

    def _processInclude (self, node):
        self._requireInProlog(node.nodeName)
        raise IncompleteImplementationException('include directive not implemented')

    def _processImport (self, node):
        """Process an import directive.

        This attempts to locate schema (named entity) information for
        a namespace that is referenced by this schema.
        """

        self._requireInProlog(node.nodeName)
        if not node.hasAttribute('namespace'):
            raise SchemaValidationError('import directive must provide namespace')
        uri = node.getAttribute('namespace')
        namespace = self.namespaceForURI(uri)
        # @todo 
        namespace.checkInitialized()
        if namespace.schema() is None:
            # Just in case somebody imports a namespace but doesn't
            # actually use it, let this go.  If they do try to use it,
            # we'll get a NotInNamespace exception then.
            sys.stderr.write("Warning: No available schema for imported %s, forging ahead\n" % (uri,))
        return node

    def _processRedefine (self, node):
        self._requireInProlog(node.nodeName)
        raise IncompleteImplementationException('redefine not implemented')

    def _processAnnotation (self, node):
        an = self._addAnnotation(xsc.Annotation.CreateFromDOM(self, node))
        return self

    def _processAttributeDeclaration (self, node):
        # NB: This is an attribute of the schema itself.
        an = xsc.AttributeDeclaration.CreateFromDOM(self, node)
        self._addNamedComponent(an)
        return an

    def _processSimpleType (self, node):
        """Walk a simpleType element to create a simple type definition component.
        """
        # Node should be a topLevelSimpleType
        assert self.xsQualifiedName('simpleType') == node.nodeName
        assert self.xsQualifiedName('schema') == node.parentNode.nodeName

        rv = xsc.SimpleTypeDefinition.CreateFromDOM(self, node)
        self._addNamedComponent(rv)
        return rv

    def _processComplexType (self, node):
        """Walk a complexType element to create a complex type definition component.
        """
        # Node should be a topLevelComplexType
        assert self.xsQualifiedName('complexType') == node.nodeName
        assert self.xsQualifiedName('schema') == node.parentNode.nodeName

        rv = xsc.ComplexTypeDefinition.CreateFromDOM(self, node)
        self._addNamedComponent(rv)
        return rv

    def _processAttributeGroup (self, node):
        # Node should be a namedAttributeGroup
        assert self.xsQualifiedName('attributeGroup') == node.nodeName
        assert self.xsQualifiedName('schema') == node.parentNode.nodeName
        rv = xsc.AttributeGroupDefinition.CreateFromDOM(self, node)
        self._addNamedComponent(rv)
        return rv

    def _processGroup (self, node):
        # Node should be a namedGroup
        assert self.xsQualifiedName('group') == node.nodeName
        assert self.xsQualifiedName('schema') == node.parentNode.nodeName
        rv = xsc.ModelGroupDefinition.CreateFromDOM(self, node)
        self._addNamedComponent(rv)
        return rv

    # @todo make process* private
    def _processElementDeclaration (self, node):
        # Node should be a named element
        assert self.xsQualifiedName('element') == node.nodeName
        assert self.xsQualifiedName('schema') == node.parentNode.nodeName
        ed = xsc.ElementDeclaration.CreateFromDOM(self, node)
        self._addNamedComponent(ed)
        return ed

    def processTopLevelNode (self, node):
        """Process a DOM node from the top level of the schema.

        This should return a non-None value if the node was
        successfully recognized."""
        if self.xsQualifiedName('include') == node.nodeName:
            return self._processInclude(node)
        if self.xsQualifiedName('import') == node.nodeName:
            return self._processImport(node)
        if self.xsQualifiedName('redefine') == node.nodeName:
            return self._processRedefine(node)
        if self.xsQualifiedName('annotation') == node.nodeName:
            return self._processAnnotation(node)
        rv = schemaTop.Match(self, node)
        if rv is not None:
            self.__pastProlog = True
            return rv
        raise SchemaValidationError('Unexpected top-level element %s' % (node.nodeName,))

    def domRootNode (self):
        return self.__domRootNode

    # @todo import Namespace.XMLSchema as xs
    def xs (self):
        return self.__xs

# @todo Replace this with a reference to Namespace.XMLSchema
def SchemaForXS (wxs):
    '''Create a Schema instance that targets the XMLSchema namespace.
    Preload all its elements.  Note that we only need to do this in
    the bootstrap code.'''
    rv = schema()
    rv.setTargetNamespace(wxs.xs())
    xsd.DefineSimpleTypes(rv)
    return rv

Namespace.SetStructuresModule(xsc, schema)
