from tkinter import *

try:
    from coordinates import *
    from drawnValue import *
    from SortingBase import *
except ModuleNotFoundError:
    from .coordinates import *
    from .drawnValue import *
    from .SortingBase import *

V = vector

class PriorityQueue(SortingBase):

    nextColor = 0

    def __init__(self, size=12, title="Priority Queue", **kwargs):
        super().__init__(size=size, title=title, **kwargs)

        self.nItems = None
        self.buttons = self.makeButtons()
        
        self.display()

    # ARRAY FUNCTIONALITY

    isFullCode = '''
bool isFull() {{
   return nItems == maxSize;
}}
'''

    def isFull(self, code=isFullCode, wait=0.2):
        callEnviron = self.createCallEnvironment(code=code)
        self.highlightCode(
            'nItems == maxSize', callEnviron, wait=wait)
        self.cleanUp(callEnviron)
        return len(self.list) == self.size

    isEmptyCode = '''
bool isEmpty() {{
   return nItems == 0;
}}
'''

    def isEmpty(self, code=isEmptyCode, wait=0.2):
        callEnviron = self.createCallEnvironment(code=code)
        self.highlightCode(
            'nItems == 0', callEnviron, wait=wait)
        self.cleanUp(callEnviron)
        return len(self.list) == 0

    insertCode = '''
bool insert(T item = {val}) {{
   if (isFull())
      throw "Queue overflow";
   int j = nItems - 1;
   while (j >= 0 &&
         priority(item) >= priority(que[j]))
      que[j+1] = que[j];
      j--;
   que[j+1] = item;
   nItems++;
   return true;
}}
'''
    
    def insert(self, val, code=insertCode, start=True, wait=0.1):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)

        
        if self.highlightCode('isFull()', callEnviron, wait=wait / 10,
                              returnValue=lambda: self.isFull()):
            self.highlightCode(
                'throw "Queue overflow"', callEnviron, 
                color=self.EXCEPTION_HIGHLIGHT)
            self.cleanUp(callEnviron)
            return
        
        j = len(self.list) - 1  # Start at front
        startPosition = self.tempCoords(j)
        cell = self.createCellValue(startPosition, val)
        itemLabel = self.canvas.create_text(
            *self.tempLabelCoords(j, self.VARIABLE_FONT), text='item', 
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        newItem = cell + (itemLabel,)
        callEnviron |= set(newItem)

        self.highlightCode('int j = nItems - 1;', callEnviron, wait=wait)
        indexJ = self.createIndex(j, 'j', level=-2)
        callEnviron |= set(indexJ)
            
        while self.highlightCode(  # Move bigger items right
                'j >= 0', callEnviron, wait=wait,
                returnValue=j >= 0) and self.highlightCode(
                    'priority(item) >= priority(que[j])',
                    callEnviron, wait=wait,
                    returnValue=val >= self.list[j].val):

            self.highlightCode('que[j+1] = que[j];', callEnviron)
            self.assignElement(j, j+1, callEnviron)

            self.highlightCode('j--;', callEnviron)
            j -= 1
            self.moveItemsBy(indexJ + newItem, (-self.CELL_SIZE, 0),
                             sleepTime=wait / 5)
            
        self.highlightCode('que[j+1] = item;', callEnviron, wait=wait)
        # Location of the new cell in the array
        toPositions = (self.fillCoords(val, self.cellCoords(j+1)),
                       self.cellCenter(j+1))

        self.moveItemsTo(cell, toPositions, sleepTime=0.01)
        if j + 1 == len(self.list):
            self.list.append(drawnValue(val, *cell))
        else:
            self.dispose(callEnviron, *self.list[j+1].items)
            self.list[j+1] = drawnValue(val, *cell)
        callEnviron -= set(cell)  # New cell is no longer temporary

        self.highlightCode('nItems++;', callEnviron)
        self.moveItemsBy(self.nItems, (self.CELL_SIZE, 0), sleepTime=0.01)

        self.highlightCode('return true;', callEnviron)
        self.cleanUp(callEnviron)
        return True

    peekCode = '''
T* peek() {{
   return isEmpty() ? nullptr : que[nItems-1];
}}
'''
    
    def peek(self, code=peekCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)
        wait = 0.1
        
        self.highlightCode('isEmpty()', callEnviron, wait=wait)
        if self.isEmpty():
            self.highlightCode('return nullptr;', callEnviron)
            self.cleanUp(callEnviron)
            return None
            
        self.highlightCode(
            ['return', 'que[nItems-1]'], callEnviron, wait)
        # draw output box using smaller font than values
        font = (self.VALUE_FONT[0], - abs(self.VALUE_FONT[1]) * 3 // 4)
        outputBoxCoords = self.outputBoxCoords(font, N=1)
        outputBox = self.canvas.create_rectangle(
            *outputBoxCoords, fill=self.OPERATIONS_BG)
        callEnviron.add(outputBox)

        # calculate where the value will need to move to
        midOutputBox = BBoxCenter(outputBoxCoords)

        # create the value to move to output box
        valueOutput = self.canvas.copyItem(self.list[-1].items[1])
        callEnviron.add(valueOutput)

        # move value to output box
        self.moveItemsTo(valueOutput, midOutputBox, sleepTime=wait / 5)

        # adjust the font of the output item
        self.canvas.itemconfig(valueOutput, font=font)

        self.cleanUp(callEnviron)
        return self.list[-1].val

    newCode = '''
PriorityQueue(int size = {val}) {{
   maxSize = size;
   que = new T[size];
   nItems = 0;
}}
'''
    
    def newArraySize(self, val, code=newCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start)

        cell0 = self.cellCoords(0)
        pad = abs(self.VARIABLE_FONT[1])
        self.canvas.delete('all')
        wait=0.1
        callEnviron.add(self.canvas.create_text(
            *cell0[:2], text='__maxSize = {}'.format(val), anchor=SW,
            font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR))
        try:
            self.highlightCode('maxSize = size;', callEnviron, wait=wait)
        except UserStop:
            wait = 0
        
        self.highlightCode('que = new T[size];', callEnviron)
        self.size = val
        self.list = []
        self.display(showNItems=False)
        callEnviron.add(self.canvas.create_text(
            pad, (cell0[1] + cell0[3]) // 2,
            text='__que', anchor=W, font=self.VARIABLE_FONT,
            fill=self.VARIABLE_COLOR))
        try:
            self.wait(wait)
        except UserStop:
            wait = 0
            
        self.highlightCode('self.__pri = pri', callEnviron)
        callEnviron.add(self.canvas.create_text(
            cell0[0],  (cell0[1] + 2 * cell0[3]) // 2,
            text='__pri = identity', font=self.VARIABLE_FONT,
            fill=self.VARIABLE_COLOR))
        try:
            self.wait(wait)
        except UserStop:
            wait = 0

        self.highlightCode('nItems = 0;', callEnviron)
        self.display()
        try:
            self.wait(wait)
        except UserStop:
            wait = 0

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron)

    removeLastCode = '''
T remove() {{
   if (isEmpty())
      throw "Queue underflow";
   nItems--;
   T front = que[nItems];
   que[nItems] = nullptr;
   return front;
}}
'''
    
    # delete the last element of the queue, or None if empty
    def remove(self, code=removeLastCode, start=True):
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start)

        self.highlightCode('isEmpty()', callEnviron, wait=0.01)
        if self.isEmpty():
            self.highlightCode('throw "Queue underflow";',
                               callEnviron, color=self.EXCEPTION_HIGHLIGHT)
            self.cleanUp(callEnviron)
            return
        self.wait(0.3)

        self.highlightCode('nItems--;', callEnviron)
        self.moveItemsBy(self.nItems, (-self.CELL_SIZE, 0), sleepTime=0.02)

        self.highlightCode('T front = que[nItems];', callEnviron)
        self.assignToTemp(len(self.list) - 1, callEnviron, varName='front')

        self.highlightCode('que[nItems] = nullptr;', callEnviron,
                           wait=0.1)
        n = self.list.pop()
        for item in n.items:
            if item is not None:
                self.canvas.delete(item)

        self.highlightCode('return front;', callEnviron, wait=0.1)
        self.cleanUp(callEnviron)
        return n.val

    def fixPositions(self):     # Move canvas display items to exact coords
        for i, drawItem in enumerate(self.list):
            if drawItem:    # if i contains a cell...move the cells
                self.canvas.coords(drawItem.items[0], 
                                   *self.fillCoords(drawItem.val, 
                                                    self.cellCoords(i)))
                self.canvas.coords(drawItem.items[1], *self.cellCenter(i))

        # Move nItems index to position in array
        x = self.cellCenter(len(self.list))[0]
        # Use y coord from nItems index but x value from target location
        for item in self.nItems:
            coords = [x if i%2 == 0 else c
                      for i, c in enumerate(self.canvas.coords(item))]
            self.canvas.coords(item, *coords)
        
        self.window.update()

    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        if ((len(args) == 0 or args[0] is None) and # When cleaning up entire 
            kwargs.get('callEnviron', None) is None): # call stack,
            self.fixPositions()   # Restore cells to their coordinates in array

    def makeButtons(self, maxRows=4):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1, 
            argHelpText=['item'], helpText='Insert item by its priority',
            validationCmd=vcmd)
        newSizeArrayButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1,
            argHelpText=['number of items'], validationCmd=vcmd, 
            helpText='Create new priority queue for N items')
        removeButton = self.addOperation(
            "Remove", lambda: self.clickRemove(),
            helpText='Remove highest priority (lowest numbered) item')
        peekButton = self.addOperation(
            "Peek", lambda: self.clickPeek(),
            helpText='Peek at highest priority (lowest numbered) item')
        self.addAnimationButtons()
        return [insertButton, newSizeArrayButton, removeButton, peekButton]

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val
    
    def clickInsert(self):
        val = self.validArgument()
        self.setMessage(
            "Input value must be an integer from 0 to 99." if val is None else
            "Item {} inserted".format(val) 
            if self.insert(val, start=self.startMode()) else
            "Error! Queue is already full.")
                
        self.clearArgument()
    
    def clickRemove(self):
        result = self.remove(start=self.startMode())
        self.setMessage(
            "Error! Queue is empty." if result is None else
            "Item {} removed".format(result))
        self.clearArgument()

    def clickPeek(self):
        front = self.peek(start=self.startMode())
        self.setMessage("Error! Queue is empty." if front is None else
                        "Item at front is {}".format(front))

    def clickNew(self):
        val = self.validArgument()
        canvasDims = widgetDimensions(self.canvas)
        maxCells = (canvasDims[0] - self.ARRAY_X0) // self.CELL_SIZE - 1
        # Error if number of desired cells won't fit on canvas
        if val is None or 0 == val or val > maxCells:
            self.setMessage("This queue size must be beteeen 1 and {}".format(
                maxCells))
            return
        self.newArraySize(val, start=self.startMode())
        self.clearArgument()

if __name__ == '__main__':
    nonneg, negative, options, otherArgs = categorizeArguments(sys.argv[1:])
    queue = PriorityQueue()
    keys = [int(arg) for arg in nonneg[:queue.size]]
    keys.sort(reverse=True)
    queue.list = [drawnValue(key, None, None) for key in keys]
    queue.display()
    queue.runVisualization()
