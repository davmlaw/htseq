.. _genomic:

************************************
Positions, intervals and arrays
************************************

.. currentmodule:: HTSeq

.. doctest:: 
   :hide:

   >>> import HTSeq

``GenomicPosition``
===================

A ``GenomicPosition`` represents the position of a single base or base pair, i.e., it is
an interval of length 1, and hence, the class is a subclass of :class:GenomicInterval.

.. class::  GenomicPosition(chrom, pos, strand='.')

   The initialisation is as for a :class:GenomicInterval object, but no ``length`` argument is passed.
   
Attributes

   .. attribute:: pos
   
      **pos** is an alias for :attr:`GenomicInterval.start_d`.
      
   All other attributes of :class:`GenomicInterval` are still exposed. Refrain from 
   using them, unless you want to use the object as an interval, not as a position.
   Some of them are now read-only to prevent the length to be changed.


``GenomicInterval``
===================

A genomic interval is a consecutive stretch on a genomic sequence such as a chromosome.
It is represented by a ``GenomicInterval`` object.

Instantiation
   .. class:: GenomicInterval(chrom, start, end, strand)

      ``chrom`` (string)
         The name of a sequence (i.e., chromosome, contig, or the like). 
         
      ``start``  (int)
         The start of the interval. Even on the reverse strand,
         this is always the smaller of the two values 'start' and 'end'.
         Note that all positions should be given and interpreted as 0-based value!
         
      ``end``  (int)
         The end of the interval. Following Python convention for 
         ranges, this in one more than the coordinate of the last base
         that is considered part of the sequence.
         
      ``strand``  (string)
         The strand, as a single character, ``'+'``, ``'-'``, or ``'.'``.
         ``'.'`` indicates that the strand is irrelevant.


Representation and string conversion
   The class's ``__str__`` method gives a space-saving description of the
   interval, the ``__repr__`` method is a bit more verbose::
   
      >>> iv = HTSeq.GenomicInterval("chr3", 123203, 127245, "+")
      >>> print(iv)
      chr3:[123203,127245)/+
      >>> iv
      <GenomicInterval object 'chr3', [123203,127245), strand '+'>

Attributes

   .. attribute:: GenomicInterval.chrom
                  GenomicInterval.start
                  GenomicInterval.end
                  GenomicInterval.strand
                 
      as above                 
                 
   .. attribute:: GenomicInterval.start_d

      The "directional start" position. This is the position of the
      first base of the interval, taking the strand into account. Hence, 
      this is the same as ``start`` except when ``strand == '-'``, in which 
      case it is ``end-1``.
      
      Note that if you set ``start_d``, both ``start`` and ``end`` are changed, 
      such that the interval gets the requested new directional start and its
      length stays unchanged.      
      
   .. attribute:: GenomicInterval.end_d

      The "directional end": The same as ``end``, unless ``strand=='-'``, 
      in which case it is ``start-1``. This convention allows to go from
      ``start_d`` to ``end_d`` (not including, as usual in Python, the last
      value) and get all bases in "reading" direction.
      
      ``end_d`` is not writable. 

   .. attribute:: GenomicInterval.length
   
      The length is calculated as end - start. If you set the length, 
      ``start_d`` will be preserved, i.e., ``end`` is changed, 
      unless the strand is ``-``, in which case ``start`` is changed.
      
   .. attribute:: GenomicInterval.start_as_pos
                  GenomicInterval.end_as_pos
                  GenomicInterval.start_d_as_pos
                  GenomicInterval.end_d_as_pos
                  
      These attributes return :class:`GenomicPosition` objects referring to the
      respective positions.

Directional instantiation   
   .. function:: GenomicInterval_from_directional(chrom, start_d, length, strand=".")
   
      This function allows to create a new ``GenomicInterval`` object specifying
      directional start and length instead of start and end. 
   
Methods
   .. method:: GenomicInterval.is_contained_in(iv)
               GenomicInterval.contains(iv)
               GenomicInterval.overlaps(iv)
               
      These methods test whether the object is contained in, contains, or overlaps
      the second ``GenomicInterval`` object ``iv``. 
      
      For any of of these conditions
      to be true, the ``start`` and ``end`` values have to be appropriate, and furthermore,
      the ``chrom`` values have to be equal and the ``strand`` values consistent. The latter
      means that the strands have to be the same if both intervals have strand
      information. However, if at least one of the objects has ``strand == '.'``,
      the strand information of the other object is disregarded.
      
      Note that all three methods return ``True`` for identical intervals.
               
   .. method:: GenomicInterval.range(step = 1)
               GenomicInterval.range_d(step = 1)
               
      These methods yield iterators of :class:GenomicPosition objects from
      ``start`` to ``end`` (or, for ``range_d`` from ``start_d`` to ``end_d``).

   .. method:: GenomicInterval.extend_to_include(iv)
   
      Change the object's ``start`` end ``end`` values such that ``iv`` becomes contained.
         
Special methods      

   ``GenomicInterval`` implements the methods necessary for
   
   - obtaining a copy of the object (the ``copy`` method)
   - pickling the object
   - representing the object and converting it to a string (see above)
   - comparing two GenomicIntervals for equality and inequality
   - hashing the object


``GenomicArray``
================

A ``GenomicArray`` is a collection of :class:`ChromVector` objects, either one or two 
for each chromosome of a genome. It allows to access the data in these 
transparently via :class:`GenomicInterval` objects.

**Note: ``GenomicArray``'s interface changed significantly in version 0.5.0. Please
see the Version History page.**

Instantiation
   .. class:: GenomicArray(chroms, stranded=True, typecode='d', storage='step', memmap_dir='')

   Creates a ``GenomicArray``. 
   
   If ``chroms`` is a list of chromosome names,  two (or one, see below) ``ChromVector`` 
   objects for each chromosome are created, with start index 0 and indefinite
   length. If ``chroms`` is a ``dict``, the keys are used for the chromosome names
   and the values should be the lengths of the chromosome, i.e., the ChromVectors
   index ranges are then from 0 to these lengths. (Note that the term chromosome
   is used only for convenience. Of course, you can as well specify contig IDs
   or the like.) Finally, if ``chroms`` is the string ``"auto"``, the GenomicArray
   is created without any chromosomes but whenever the user attempts to assign a 
   value to a yet unknown chromosome, a new one is automatically created with 
   :meth:`GenomicArray.add_chrom`.
   
   If ``stranded`` is ``True``, two ``StepVector`` objects are created for each chromosome,
   one for the '+' and one for the '-' strand. For ``stranded == False``, only one
   ``StepVector`` per chromosome is used. In that case, the strand argument of
   all ``GenomicInterval`` objects that are used later to specify regions in the
   ``GenomicArray`` are ignored.
   
   The ``typecode`` determines the data type and is as in ``numpy``, i.e.:

      - ``'d'`` for float values (C type 'double'),
      - ``'i'`` for int values,
      - ``'b'`` for Boolean values,
      - ``'O'`` for arbitrary Python objects as value.

   The storage mode determines how the ChromVectors store the data internally:
   
      - mode ``'step'``: A step vector is used. This is the default and useful
        for large amounts of data which may stay constant along a range of indices.
        Each such step is stored internally as a node in a red-black tree.

      - mode ``'ndarray'``: A 1D numpy array is used internally. This is useful
        if the data changes a lot, and steps are hence inefficient. Using this mode
        requires that chromosome lengths are specified.
        
      - mode ``memmap``: This is useful for large amounts of data with very short 
        steps, where ``step`` is inefficient, but a numpy vectors would not fit
        into memory. A numpy memmap is used that stores the whole vector in a
        file on disk and transparently maps into memory windows of the data. This
        mode requires chromosome lengths, and specification of a directory, via
        the ``memmap_dir`` argument, to store the temporary files in. It is not
        suitable for type code ``O``.
   
Attributes

   .. attribute:: GenomicArray.stranded
                 GenomicArray.typecode
                 
      see above
      
   .. attribute:: GenomicArray.chrom_vectors   
   
      a dict of dicts of ``ChromVector`` objects, using the chromosome
      names, and the strand as keys::
      
      .. doctest::
      
         >>> ga = HTSeq.GenomicArray(["chr1", "chr2"], stranded=False)
         >>> sorted(ga.chrom_vectors.items()) #doctest:+NORMALIZE_WHITESPACE
         [('chr1', {'.': <ChromVector object, chr1:[0,Inf)/., step>}),
          ('chr2', {'.': <ChromVector object, chr2:[0,Inf)/., step>})] 
         >>> ga = HTSeq.GenomicArray(["chr1", "chr2"], stranded=True)
         >>> sorted([(st[0], sorted(st[1].items())) for st in ga.chrom_vectors.items()])  #doctest:+NORMALIZE_WHITESPACE
         [('chr1', [('+', <ChromVector object, chr1:[0,Inf)/+, step>), 
                    ('-', <ChromVector object, chr1:[0,Inf)/-, step>)]),
          ('chr2', [('+', <ChromVector object, chr2:[0,Inf)/+, step>), 
                    ('-', <ChromVector object, chr2:[0,Inf)/-, step>)])]

   .. attribute:: GenomicArray.auto_add_chroms
   
      A boolean. This attribute is set to True if the GenomicArray was created with the ``"auto"``
      arguments for the ``chroms`` parameter. If it is true, an new chromosome
      will be added whenever needed.

                   
Data access
   To access the data, use :class:GenomicInterval objects.
   
   To set an single position or an interval, use::
   
      >>> ga[HTSeq.GenomicPosition("chr1", 100, "+")] = 7
      >>> ga[HTSeq.GenomicInterval("chr1", 250, 400, "+")] = 20
      
   To read a single position::
   
      >>> ga[HTSeq.GenomicPosition("chr1", 300, "+")]
      20.0

   .. method:: ChromVector.steps(self)
      
   To read an interval, use a ``GenomicInterval`` object as index, and
   obtain a ``ChromVector`` with a sub-view::
   
      >>> iv = HTSeq.GenomicInterval("chr1", 250, 450, "+")
      >>> v = ga[iv]
      >>> v
      <ChromVector object, chr1:[250,450)/+, step>
      >>> list(v.steps())  #doctest:+NORMALIZE_WHITESPACE
      [(<GenomicInterval object 'chr1', [250,400), strand '+'>, 20.0), 
       (<GenomicInterval object 'chr1', [400,450), strand '+'>, 0.0)]
       
   Note that you get (interval, value) pairs , i.e., you can conveniently cycle
   through them with::
   
      >>> for iv, value in ga[iv].steps():
      ...    print(iv, value)
      chr1:[250,400)/+ 20.0
      chr1:[400,450)/+ 0.0
      
   .. method:: GenomicArray.steps(self)
 
    You can get all steps from all chromosomes by calling the arrays own ``steps``
    method.

         
Modifying values

   ChromVector implements the ``__iadd__`` method. Hence you can use ``+=``:
   
      >>> ga[HTSeq.GenomicInterval("chr1", 290, 310, "+")] += 1000
      >>> list(ga[HTSeq.GenomicInterval("chr1", 250, 450, "+")].steps())  #doctest:+NORMALIZE_WHITESPACE
      [(<GenomicInterval object 'chr1', [250,290), strand '+'>, 20.0), 
       (<GenomicInterval object 'chr1', [290,310), strand '+'>, 1020.0), 
       (<GenomicInterval object 'chr1', [310,400), strand '+'>, 20.0), 
       (<GenomicInterval object 'chr1', [400,450), strand '+'>, 0.0)]

   To do manipulations other than additions, use Chromvector's ``apply`` method:
   
   .. method:: ChromVector.apply(func)
   
       >>> ga[HTSeq.GenomicInterval("chr1", 290, 300, "+")].apply(lambda x: x * 2) 
       >>> list(ga[HTSeq.GenomicInterval("chr1", 250, 450, "+")].steps()) #doctest:+NORMALIZE_WHITESPACE
       [(<GenomicInterval object 'chr1', [250,290), strand '+'>, 20.0), 
        (<GenomicInterval object 'chr1', [290,300), strand '+'>, 2040.0), 
        (<GenomicInterval object 'chr1', [300,310), strand '+'>, 1020.0), 
        (<GenomicInterval object 'chr1', [310,400), strand '+'>, 20.0), 
        (<GenomicInterval object 'chr1', [400,450), strand '+'>, 0.0)]
      
Adding a chromosome
   .. method:: GenomicArray.add_chrom(chrom, length=sys.maxint, start_index=0)
   
      Adds step vector(s) for a further chromosome. This is useful if you do not have a full
      list of chromosome names yet when instantiating the ``GenomicArray``.
      
I/O from and to files
   You can read an instance from a BedGraph/BigWig file and write an instance into the same file formats.

   .. method:: GenomicArray.write_bedgraph_file(file_or_filename, strand=".", track_options="")
   
      Write out the data in the GenomicArray as a BedGraph_ track. This is a subtype of the Wiggle_ format
      (i.e., the file extension is usually ".wig") and such files can be conveniently viewed in
      a genome browser, e.g., with IGB_. 
      
      This works only for numerical data, i.e., ``datatype`` ``'i'`` or ``'d'``. As a bedgraph track
      cannot store strand information, you have to specify either ``'+'`` or ``'-'`` as the
      strand argument if your ``GenomicArray`` is stranded (``stranded==True``). Typically, you
      will write two wiggle files, one for each strand, and display them together.


   .. method:: GenomicArray.from_bedgraph_file(file_or_filename, strand=".", typecode="d")

      Create GenomicArray from BedGraph file.

      See GenomicArray.write_bedgraph_file for details on the file format.

        Args:
            file_or_filename (str, path, or open file handle): Where to load the BedGraph data from.
            strand ("+", "-", or "."): strandedness of the returned array.
            typecode ("d", "i", or "l"): Type of data in the file. "d" means floating point (double), "i" is integer, "l" is long integer.

        Returns:
            A GenomicArray instance with the data. 


   .. method:: GenomicArray.write_bigwig_file(filename, strand=".")

        Write GenomicArray to BigWig file.

        BigWig files are used to visualize genomic "tracks", notably in
        UCSC's genomic viewer. They are, in a sense, the binary compressed
        equivalent of BedGraph files. This function stores the GenomicArray
        into such a file for further use.

        Args:
            filename (str or path): Where to store the data.
            strand (".", "+", or "-"): Which strand to write to file.

        The BigWig file format is described here:
        
            http://genome.ucsc.edu/goldenPath/help/bigWig.html

        NOTE: This function requires the package pyBigWig at:

            https://github.com/deeptools/pyBigWig

        Install it via pip, conda, or see instructions at that page.

   .. method:: GenomicArray.from_bigwig_file(filename, strand=".", typecode="d")

        Create GenomicArray from BigWig file.

        See GenomicArray.write_bigwig for details on the file format.

        Args:
            filename (str or path): Where to load the data from.
            strand ("+", "-", or "."): strandedness of the returned array.
            typecode ("d", "i", or "l"): Type of data in the file. "d" means floating point (double), "i" is integer, "l" is long integer.

        Returns:
            A GenomicArray instance with the data.

.. _BedGraph: http://genome.ucsc.edu/goldenPath/help/bedgraph.html
.. _Wiggle: http://genome.ucsc.edu/goldenPath/help/wiggle.html
.. _IGB: http://igb.bioviz.org/
   


``GenomicArrayOfSets``
======================

A ``GenomicArrayOfSets`` is a sub-class of :class:`GenomicArray` that deal with the common
special case of overlapping features. This is best explained by an example: Let's say, we
have two features, ``"geneA"`` and ``"geneB"``, that are at overlapping positions::

   >>> ivA = HTSeq.GenomicInterval("chr1", 100, 300, ".")
   >>> ivB = HTSeq.GenomicInterval("chr1", 200, 400, ".")
   
In a ``GenomicArrayOfSets``, the value of each step is a ``set`` and so can hold more than
one object. The __iadd__ method is overloaded to add elements to the sets:

   >>> gas = HTSeq.GenomicArrayOfSets(["chr1", "chr2"], stranded=False)
   >>> gas[ivA] += "gene A"
   >>> gas[ivB] += "gene B"
   >>> [(st[0], sorted(st[1])) for st in gas[HTSeq.GenomicInterval("chr1", 0, 500, ".")].steps()] #doctest:+NORMALIZE_WHITESPACE
   [(<GenomicInterval object 'chr1', [0,100), strand '.'>,   []), 
    (<GenomicInterval object 'chr1', [100,200), strand '.'>, ['gene A']), 
    (<GenomicInterval object 'chr1', [200,300), strand '.'>, ['gene A', 'gene B']), 
    (<GenomicInterval object 'chr1', [300,400), strand '.'>, ['gene B']), 
    (<GenomicInterval object 'chr1', [400,500), strand '.'>, [])]

.. class:: GenomicArrayOfSets(chroms, stranded = True)

   Instantiation is as in :class:`GenomicArray`, only that ``datatype`` is always ``'O'``.


Negative Index
==============
Sometimes a negative index is useful for representing upstream elements. For instance, you might want to pool information about [-500,500) near transcription start site. You can do that using :class:`StepVector`::

   >>> iv = HTSeq.GenomicInterval('chr1',-5, 30,'+')
   >>> vct = HTSeq.StepVector.StepVector.create(length=60,start_index=-10)
   >>> vct[iv.start:iv.end] +=1
   >>> list(vct)[:10]
   [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0]

Notice that unlike :class:`StepVector`, :class:`GenomicArray` cannot be used with negative indices.
