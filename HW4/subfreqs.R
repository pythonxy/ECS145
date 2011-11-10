
n <- 1
powerset <- function(fullset) {
	n <<- 1
	temp <- powersetHelper(fullset)
	return(temp)
}

powersetHelper <- function(fullset) {
	if (length(fullset) == 0) {
		base <- list()
		base[[n]] <- NA
		n <<- n + 1
		return(base)
	}
	
	ps <- powerset(fullset[-1])

	temp <- ps
	for (subset in temp) {		
		if (!(is.na(subset[1]))) {
			term <- append(c(fullset[1]), subset)
		}
		else
		{
			term <- c(fullset[1])
		}
		ps[[n]] <- term
		n <<- n + 1				
	}
	return(ps)
}


compareSubsets <- function(term1, term2) {
	cat("Comparing ")
	print(term1)
	cat(" with ")
	print(term2)

	if (!(length(term1) == length(term2))) {
		return(FALSE)
	}
	v = term1 == term2
	v = Reduce("&&", v)
	
	if (is.na(v)) {
		return(FALSE)
	}

	return(v)
}


union <- function(numsets) {
	v = Reduce(c, numsets)
	return(unique(v))
}


subfreqs <- function(numsets) {

	#calculating the powerset of the (distinct) union of numsets
	fullps = powerset(union(numsets))
	
	# numps holds the powersets of the individual numsets
	numps = mapply(powerset, numsets)

	freqs = list()

	for (subset in fullps) {
		freqs[toString(subset)] <- 0
		for (i in 1:length(numsets)) {
			cat("i = ", i, "\n", "numps[[", i, "]] =\n")
			print(numps[,i])
			v = mapply(compareSubsets, rep.int(list(subset), length(numps[,i])), numps[,i])
			print(v)
			freqs[[toString(subset)]] <- freqs[[toString(subset)]] + sum(v)
		}
	}

	return(freqs)
}

