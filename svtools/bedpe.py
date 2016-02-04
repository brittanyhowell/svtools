import re
import sys

class Bedpe(object):
        def __init__(self, bed_list):
            self.c1 = bed_list[0]
            self.s1 = int(bed_list[1])
            self.e1 = int(bed_list[2])
            self.c2 = bed_list[3]
            self.s2 = int(bed_list[4])
            self.e2 = int(bed_list[5])
            self.name = bed_list[6]
            self.score = self.parse_score(bed_list[7])
            self.o1 = bed_list[8]
            self.o2 = bed_list[9]
            self.filter = bed_list[11]
            self.malformedFlag = 0
            self.misc = bed_list[12:]
            self.check_malformed()
            del self.misc[1]
            
            self.svtype = self.retrieve_svtype()
            self.af = self.retrieve_af()
            if self.svtype != bed_list[10]:
                sys.stderr.write("SVTYPE at Column 11({0})) and SVTYPE in INFO Column({1}) don't match at variant ID {3}\n".format(str(bed_list[10]), str(self.svtype), self.name))
            self.adjust_by_cipos()
            self.adjust_by_ciend()

        @staticmethod
        def parse_score(score):
            if score.isdigit():
                return float(score)
            else:
                return score

        def check_malformed(self):
            if self.misc[0] == 'MISSING':
                self.malformedFlag = 1
                self.misc[0] = self.misc[1]
            if self.misc[1] == 'MISSING':
                self.malformedFlag = 2      

        def retrieve_svtype(self):
            svtype = re.split('=', ''.join(filter(lambda x: 'SVTYPE=' in x, self.misc[0].split(';'))))[1]
            return svtype

        def retrieve_af(self):
            af = re.split('=', ''.join(filter(lambda x: 'AF=' in x, self.misc[0].split(';'))))[1]
            return af

        def adjust_by_cipos(self):
            # CIPOS is adjusted to leftmost before conversion to BEDPE? This removes this adjustment
            # XXX Do we really want to do this for every single BEDPE line? Or just when converting back to VCF?
            if 'CIPOS=' in self.misc[0]:
                self.cipos = re.split('=|,', ''.join(filter(lambda x: 'CIPOS=' in x, self.misc[0].split(';'))))
                if self.o1 == '-' and self.svtype == 'BND':
                    self.b1 = self.s1 - int(self.cipos[1]) + 1 
                else:
                    self.b1 = self.s1 - int(self.cipos[1])
            else:
                if self.o1 == '-' and self.svtype == 'BND':
                    self.b1 = self.s1 + 1 
                else:
                    self.b1 = self.s1

        def adjust_by_ciend(self):
            if 'CIEND=' in self.misc[0]:     
                self.ciend = re.split('=|,', ''.join(filter(lambda x: 'CIEND=' in x, self.misc[0].split(';'))))
                if self.o2 == '-' and self.svtype == 'BND':
                    self.b2 = self.s2 - int(self.ciend[1]) + 1
                else:
                    self.b2 = self.s2 - int(self.ciend[1])
            else: 
                self.ciend = None
                if self.o2 == '-' and self.svtype == 'BND':
                    self.b2 = self.s2 + 1
                else:
                    self.b2 = self.s2

