library(pixmap)

getDist <- function(points) {
	x <- (points[1] - points[3])^2
	y <- (points[2] - points[4])^2
	return(sqrt(x+y))
}

getInput <- function(type = "str") {
	return(scan(what = type, n=1))
}

redraw <- function(image, stack) {
	plot(image)
	if (is.matrix(stack) && nrow(stack) > 1) {
		for (i in 1:nrow(stack)) {
			segments(stack[i, 1], stack[i, 2], stack[i, 3], stack[i, 4], col= "red", lty=1, lwd=3)
		}
	}
	else {
			segments(stack[1], stack[2], stack[3], stack[4], col= "red", lty=1, lwd=3)
	}
}


mydist <- function(mapfile) {
	
	image <- read.pnm(mapfile)
	plot(image)

	segmentStack = NULL
	scale <- 1
	totalDist <- 0

	while (TRUE) {
		cmd <- getInput()

		if (cmd == "as") {
			print("Select two locations")

			points <- locator(2)
			segments(points$x[1], points$y[1], points$x[2], points$y[2], col= "red", lty=1, lwd=3)

			segmentStack <- rbind(segmentStack, c(points$x[1], points$y[1], points$x[2], points$y[2]))

			totalDist <- totalDist + scale*getDist(segmentStack[nrow(segmentStack),])
		}

		if(cmd =="dls") {
			if (is.matrix(segmentStack) && nrow(segmentStack) > 1) {
				redraw(image, segmentStack[-nrow(segmentStack), ])
				totalDist <- totalDist - scale*getDist(segmentStack[nrow(segmentStack), ])
				segmentStack <- segmentStack[-nrow(segmentStack), ]
			}
			else {
				plot(image)
				totalDist <- 0
				segmentStack <- NULL
			}


		}

		if (cmd == "gs") {
			print("Select two locations:")
						
			points <- locator(2)
			ourDist <- getDist(c(points$x[1], points$y[1], points$x[2], points$y[2]))

			print("Enter distance: ")
			userDist <- getInput(double(0))
			scale = userDist / ourDist
			totalDist <- totalDist*scale

		}

		if (cmd == "q") {
			break
		}
		cat("Total distance: ", totalDist, "\n")
	}


}