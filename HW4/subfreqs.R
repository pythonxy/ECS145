
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


#toString(ps[[8]])