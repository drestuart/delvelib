
def main():
	print StringToSeed("Hello")
	print StringToSeed("there")
	print StringToSeed("sailors!!")
	

def StringToSeed(strIn):
	return int(strIn.encode('hex'), 16)
	
if __name__ == '__main__':
	main()