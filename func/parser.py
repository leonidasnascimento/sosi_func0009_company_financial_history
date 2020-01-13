class Parser:
    @staticmethod
    def ParseFloat(valStr):
        if str(valStr).isspace() or valStr == "":
            return 0.00
        
        if valStr is None:
            return 0.00

        if str(valStr) == "N/A":
            return 0.00

        if str(valStr) == "N/D":
            return 0.00

        if str(valStr) == "--":
            return 0.00

        if str(valStr) == "-":
            return 0.00

        if str(valStr).find('.') > 0:
            valStr = str(valStr).replace('.', '')

        if str(valStr).find(',') > 0:
            valStr = str(valStr).replace(',', '.')

        # PERCENT
        if str(valStr).find('%') > 0:
            return float(str(valStr).replace('%',''))/100
        
        return float(valStr)

    @staticmethod
    def ParseOrdinalNumber(valStr):
        returnValue = 0.00

        if str(valStr).isspace() or valStr == "":
            return 0.00
        
        if valStr is None:
            return 0.00

        if str(valStr).lower().find('k') > 0:
            valStr = str(valStr).lower().replace('k', '')
            returnValue = Parser.ParseFloat(valStr) * 1000

        if str(valStr).lower().find('m') > 0:
            valStr = str(valStr).lower().replace('m', '')
            returnValue = Parser.ParseFloat(valStr) * 1000000

        if str(valStr).lower().find('b') > 0:
            valStr = str(valStr).lower().replace('b', '')
            returnValue = Parser.ParseFloat(valStr) * 1000000000
        
        return returnValue