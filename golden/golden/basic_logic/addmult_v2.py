#Python program for bfloat16, a truncated mantissa version of IEEE 754 float32

class bfloat:
	def __init__(self, s, e, m):
		if len(s) + len(e) + len(m) != 16:
			print("Argument isn't 16bits")
		else:
			self.sign = s
			self.exp = e
			self.man  = m
			self.value = ''

			if self.exp == '11111111':
				if int(self.man,2) == 0:
					self.value = 'inf'
				else:
					self.value = 'NaN'

			if int(e,2) + int(m,2) == 0:
				self.value = 'zero'
	#end __init___

	def display_bin(self):
		return (self.sign, self.exp, self.man)
	#end display_bin()
	
	def bin(self):
		return self.sign + self.exp + self.man
	#end bin()

	def display_dec(self):
		exp_mag = int(self.exp,2)
		start = -1
		man_mag = 0.0
		for m in self.man:
			man_mag = man_mag + int(m) * 2 ** (start)
			start = start - 1

		if self.exp == '00000000':
			if self.man == '0000000':
				return 0.0
			else: 
				out = ((-1)**int(self.sign) * 2**(exp_mag - 126) * (man_mag)) 
				return (out)
		elif self.value == 'inf':
			return float('Inf')
		else:
			out = ((-1)**int(self.sign) * 2**(exp_mag - 127) * (man_mag + 1))
			return (out)
	#end mag
#end class
#----------------------------------------------------------------------------------------------

def bin_parser(a):
	return a[0] , a[1:9] , a[9:]

#mult_bfloat16:
#   input: (a, b) two 16bit binary string in Bfloat16 format, where a[0], b[0] are the MSBs
#   output: (mult_out) 16bit binary string in Bfloat16 format, where mult_out[0] is the
def bfloat_mult(a, b):

	#output sign
	o_sign = int(a.sign) ^ int(b.sign)
	o_sign = bin(o_sign)[2:]

	#Edge cases for +-Inf, +-NaN, +-Zero
	#Order of precedence: NaN -> Zero -> Inf
	if a.value == 'NaN' or b.value == 'NaN':
		return bfloat(o_sign, '11111111', '0000001')

	if a.value == 'zero' or b.value == 'zero':
		return bfloat(o_sign, '00000000', '0000000')

	if a.value == 'inf' or b.value == 'inf':
		return bfloat(o_sign, '11111111', '0000000')

	#Substrate the bias and add the exponents.
	o_exp = (int(a.exp,2) - 127)  + (int(b.exp,2) - 127)

	#normalize
	a_man = '1' + a.man
	b_man = '1' + b.man

	if a.exp == '00000000':
		a_man = a.man
	if b.exp == '00000000':
		b_man = b.man

	o_man = int(a_man,2) * int(b_man,2)
	o_man = bin(o_man)[2:]

	#Normalize output mantissa, adding the extra exponents, and add the bias
	dec_len =(len(a_man) - 1) + (len(b_man) - 1)
	o_exp += 127
	if len(o_man) <= dec_len + 1 and o_exp == 0:
		o_man = o_man.rjust(15,'0')
	else:
		o_exp += len(o_man) - (dec_len) - (1)

	#shift mantissa to right to accomudate for negative exp 
	if o_exp < 0: 
		o_man = '0'*(-o_exp) + o_man
		o_man = o_man[0:7].ljust(7, '0')
		return bfloat(o_sign, '0'*8, o_man)
		
	if o_exp >= 255:  #if o_exp > '1111_1111'
		return bfloat(o_sign, '1'*8, '0'*7)

	o_exp = bin(o_exp)[2:].rjust(8, '0')
	o_man = o_man[1:8].ljust(7, '0')
	
	return bfloat(o_sign, o_exp, o_man)
# end mult_bfloat()----------------------------------------------------------------------------
    
def bfloat_add(a, b):
    if a.exp == "11111111":
        return a
    elif b.exp == "11111111":
        return b
    elif (a.exp == "00000000" and a.man == "0000000") and (b.exp == "00000000" and b.man == "0000000"):
        return bfloat("0","00000000", "0000000")
    elif (a.exp == "00000000" and a.man == "0000000") and not(b.exp == "00000000" and b.man == "0000000"):
        return b
    elif not(a.exp == "00000000" and a.man == "0000000") and (b.exp == "00000000" and b.man == "0000000"):
        return a
    if(a.exp == "00000000" and a.man != "0000000"):
        a_man = "0" + a.man
        a_exp = -126
    else:
        a_man = "1" + a.man
        a_exp = int(a.exp, 2) -127
    if(b.exp == "00000000" and b.man != "0000000"):
        b_man = "0" + b.man
        b_exp = -126
    else:
        b_man = "1" + b.man
        b_exp = int(b.exp, 2) - 127
    diff = int(a.exp, 2) - int(b.exp, 2)
    #print(diff)
    if(diff > 0):
        b_man = int(b_man, 2) >> diff
        a_man = int(a_man, 2)
        b_exp = a_exp
    elif(diff < 0):
        a_man = int(a_man, 2) >> (-diff)
        #print(a_man)
        b_man = int(b_man, 2)
        a_exp = b_exp
    if(a.sign == b.sign): 
        out_man = a_man + b_man
    elif(a.sign == "1" and b.sign == "0"):
        out_man = b_man - a_man
    elif(a.sign == "0" and b.sign == "1"):
        out_man = a_man - b_man
    #print(out_man)
    if len(bin(out_man)[2:]) > 8:
        shift_amt = len(bin(out_man)[2:]) - 8
        out_man = out_man >> shift_amt
        out_exp = a_exp + shift_amt + 127
    elif len(bin(out_man)[2:]) < 8:
        shift_amt = 8 - len(bin(out_man)[2:])
        out_man = out_man << shift_amt
        out_exp = a_exp - shift_amt + 127
    else:
        out_exp = a_exp + 127
    out_exp = bin(out_exp)[2:]
    if len(out_exp) < 8:
        exp_fill = 8 - len(out_exp)
        for i in range(0, exp_fill):
            out_exp = "0" + out_exp
    if(out_man < 0):
        out_sign = "1"
        out_man = (-1)*out_man
    else:
        out_sign = "0"
    #print(bin(out_man))
    return bfloat(out_sign, out_exp, bin(out_man)[3:])

# a = bfloat('0','01011000','0010110')
# b = bfloat('1','00100011','0101100')
# print(a.display_bin(), "----", a.display_dec())
# print(b.display_bin(), "----", b.display_dec())
# print(bfloat_mult(a, b).display_dec())
# print(a.display_dec() * b.display_dec())