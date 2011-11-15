
n <- 1
powerset <- function(fullset) {
	n <<- 1
	temp <- powersetHelper(fullset)
	return(temp)
}

powersetHelper <- function(fullset) {

	fullset <- sort(fullset)
	
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
	#cat("Comparing ")
	#print(term1)
	#cat(" with ")
	#print(term2)

	if (!(length(term1) == length(term2))) {
		return(FALSE)
	}
	v = (unlist(term1, use.names = FALSE) == unlist(term2, use.names = FALSE))
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


toInt <- function(x) {
	retVal = as.numeric(unlist(strsplit(x, ", ")))
	return(retVal)
}


subfreqs <- function(numsets) {
	freqs = list()
	#calculating the powerset of the (distinct) union of numsets
	fullps = powerset(union(numsets))
	
	# numps holds the powersets of the individual numsets
	numps = mapply(powerset, numsets)
	#print(numps)

	for (subset in fullps) {
		freqs[toString(subset)] <- 0
		for (i in 1:length(numsets)) {
			cat("i = ", i, "\n", "numps[[", i, "]] =\n")

			v = list()
			if (is.matrix(numps)) {
				v = mapply(compareSubsets, numps[, i], list(subset))
			}
			else
			{
				v = mapply(compareSubsets, numps[[i]], list(subset))
			}
				

			freqs[[toString(subset)]] <- freqs[[toString(subset)]] + sum(v)
		}
	}
	freqs <- freqs[-1]
	class(freqs) <- "subfreqs"
	return(freqs)
}


# list(sum(subset), sum(freq))

freqOp <- function(t, freqs, myOp) {
	op = match.fun(myOp)
	printList = list()

	for (key in names(t)) {
		print(key)
		subsetOp = op(toInt(key))
		print(subsetOp)
		printList[[toString(subsetOp)]] <- 0
	}

	for (key in names(t)) {
		subsetOp = op(toInt(key))
		printList[[toString(subsetOp)]] <- printList[[toString(subsetOp)]] + freqs[[key]]
	}
	return(printList)
}


plot.subfreqs <- function(frobj, xaxisftn=sum) {
	t = mapply(toInt, names(frobj))
	printList = freqOp(t, frobj, xaxisftn)

	xaxis = as.numeric(names(printList))
	yaxis = unlist(printList, use.names = FALSE)



	for (i in 1:length(xaxis)) {
#		cat("(", xaxis[[i]], ", ", yaxis[[i]], ")\n")
	}

	print(xaxis)
	print(yaxis)

	plot(xaxis, yaxis)
}






