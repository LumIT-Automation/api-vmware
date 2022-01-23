class GroupConcatToDict:
    def __init__(self, keyList: [], fieldSeparator: str = '::', rowSeparator: str = ',', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.keys = keyList
        self.fSep = fieldSeparator
        self.rSep = rowSeparator



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    """ 
        #################
        makeDict usage:
        #################
             
        Input data string:
            Row0item0::Row0item1::Row0item2, Row1item0::Row1item1::Row1item2, Row2item0::Row2item1::Row2item2

        Output list of dictionaries:
        [
            {
                self.keys[0]: Row0item0,
                self.keys[1]: Row0item1,
                self.keys[2]: Row0item2
            },
            {
                self.keys[0]: Row1item0,
                self.keys[1]: Row1item1,
                self.keys[2]: Row1item2
            },
            {
                self.keys[0]: Row2item0,
                self.keys[1]: Row2item1,
                self.keys[2]: Row2item2
            }
        ]
    """

    def makeDict(self, data: str) -> list:
        outList = list()

        try:
            rowsList = data.split(self.rSep)
            for row in rowsList:
                outItem = dict()
                if '::' in row:
                    fieldsList = row.split(self.fSep)
                    j = 0
                    for k in self.keys:
                        outItem[k] = fieldsList[j]
                        j += 1
                else:
                    outItem[ self.keys[0] ] = row

                outList.append(outItem)

            return outList
        except Exception as e:
            raise e
