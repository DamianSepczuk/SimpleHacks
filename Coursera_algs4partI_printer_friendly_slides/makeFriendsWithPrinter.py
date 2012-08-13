# -*- coding: utf-8 -*-
from pyPdf113 import PdfFileWriter, PdfFileReader
import pyPdf113.pdf
import sys
from decimal import Decimal

REMOVE_DARK_BACKGROUND = True
REMOVE_SQUIGGLES = True

def main():
    if len(sys.argv) != 2:
        print 'Invoke the script with a PDF name you whish to make printer-friendly.'
        return -1
        
    inputFile = file(sys.argv[1] , "rb")
    inputPdf = PdfFileReader(inputFile)
    print 'Processing file: ', inputFile.name
    
    totalPages = inputPdf.getNumPages()
    print 'Total pages: ', totalPages

    #for pageNum in 0,1,2,3:
    output = PdfFileWriter()
    for pageNum in range(totalPages):
        print 'Processing page %.3d... '%(pageNum+1), 
        page = inputPdf.getPage(pageNum)
        page = fixPage(page)
        page.compressContentStreams()
        output.addPage(page)
        print 'Done! [%.2f%%]'%(float(pageNum+1)/totalPages*100)
    
    outputStream = file(inputFile.name[:-4] + '_printerFriendly.pdf', "wb")
    print 'Writing to file: ', outputStream.name
    print 'Please wait...', 
    output.write(outputStream)
    outputStream.close()
    print 'Done!'

def fixPage(page):
    from pyPdf113.pdf import FloatObject, NumberObject, ContentStream
    
    content = page["/Contents"].getObject()
    if not isinstance(content, ContentStream):
        content = pyPdf113.pdf.ContentStream(content, page.pdf)
    
    newContentOperations = []

    for i, op in enumerate(content.operations):
        if (i <= 38 and i >= 5 and REMOVE_SQUIGGLES  
           and content.operations[i-1][1]=='q'
           and content.operations[i-2][1]=='Q'
           and content.operations[i-3][1]=='f'
           and op[1] == 're'):
            newContentOperations.append(([FloatObject('0'), FloatObject('0'), FloatObject('0'), NumberObject('0')],'re'))
        elif i<=15 and op[1] == 'sc' and REMOVE_DARK_BACKGROUND:
            if len(op[0]) == 1 and abs(op[0][0]-Decimal('0.95')) < 0.001:
                newContentOperations.append(([FloatObject(1)],'sc'))
            elif abs(op[0][0]-Decimal('0.94902')) < 0.001:
                newContentOperations.append(([FloatObject(1),FloatObject(1),FloatObject(1)],'sc'))
        else:
            newContentOperations.append(op)

    content.operations = newContentOperations
    
    newContentArray = pyPdf113.pdf.ArrayObject()
    newContentArray.append(pyPdf113.pdf.PageObject._pushPopGS(content, page.pdf))
    page[pyPdf113.pdf.NameObject('/Contents')] = ContentStream(newContentArray, page.pdf)
    
    return page

if __name__ == "__main__":    
    main()