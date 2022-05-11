library('ape')
library('TreeSim')
library('TreeSimGM')

# Simulates sequences with Binary substitution model down a tree

source("simulate_seq_binary.r")

get_error <- function(alpha, beta) {
	error <- matrix(c(
		1 - alpha, beta,
		alpha, 1 - beta), byrow=T, ncol=2)
	error
}

add_error <- function(x, alpha, beta) {
	seq <- rep(0, length(x))	
	error_model <- get_error(alpha, beta)
	for (i in 1:length(x)) {
		state <- x[i]
		prob <- error_model[, state]
		seq[i] <- sample_from(prob)
	}	
	seq
}

simulate_tree <- function(tree, n, l, lambda, alpha, beta) {  
	Q <- get_q(lambda)
	freq <- get_pi(lambda)	
	edges <- tree$edge
	lengths <- tree$edge.length	
	labels <- as.numeric(tree$tip.label)
	N <- 2 * n - 1	
	nodes <- vector(mode = "list", length = N)	
	root <- generate_seq(l, freq)
	nodes[[n + 1]] <- root
	for (i in 1:dim(edges)[1]) {
		t <- lengths[i] 		
		parent_index <- edges[i, 1] 
		child_index <- edges[i, 2]
		parent <- nodes[[parent_index]]
		child <- mutate_seq(parent, get_p(Q, t))		
		nodes[[child_index]] <- child
	}	
	# add error and translate seq
	tr_nodes <- vector(mode = "list", length = n)
	for (i in 1:n) {		
		seq_errors <- add_error(nodes[[i]], alpha, beta)
		child_label <- labels[i]
		tr_nodes[[child_label]] <- translate_seq(seq_errors)
	}
	tr_nodes
}

simulate_trees_fixed <- function(filename, tree, n, l, num_trials, lambdas, alphas, betas) {
	dir.create(file.path("../output", "sequences"), showWarnings = F)
	sink(file.path("../output", "sequences", filename))
	cat("tree,lambda,alpha,beta,node,sequence\n")
	for (i in 1:num_trials) {
		lambda <- lambdas[i]
		alpha <- alphas[i]
		beta <- betas[i]
		seqs <- simulate_tree(tree, n, l, lambda, alpha, beta)
		for (j in 1:n) {
			cat(i, lambda, alpha, beta, j, "", sep = ",")
			cat(seqs[[j]], "\n", sep = "")
		}
	}
	sink()
	write.tree(tree)
}

simulate_trees_yule <- function(filename, n, l, num_trials, lambdas, alphas, betas, birthrates) {
  dir.create(file.path("../output", "sequences"), showWarnings = F)
  sink(file.path("../output", "sequences", filename))
  cat("tree,lambda,alpha,beta,birthrate,treelength,treeheight,node,sequence\n")
  trees <- vector(mode = "list", length = num_trials)
  for (i in 1:num_trials) {
    lambda <- lambdas[i]
    alpha <- alphas[i]
    beta <- betas[i]
    birthrate <- birthrates[i]
    tree <- generate_tree(mode = 2, n = n, birthrate = birthrate)
    tree_length <- sum(tree$edge.length)
    tree_height <- max(node.depth.edgelength(tree))
    trees[i] <- write.tree(tree)
    seqs <- simulate_tree(tree, n, l, lambda, alpha, beta)
    for (j in 1:n) {
      cat(i, lambda, alpha, beta, birthrate, tree_length, tree_height, j, "", sep = ",")
      cat(seqs[[j]], "\n", sep = "")
    }
  }
  sink()
  # writing tree log
  tree_file <- paste0(gsub(pattern = '\\.[^\\.]*$', '', filename), '.newick')
  sink(file.path("../output", "sequences", tree_file))
  cat(paste(unlist(trees)), sep='\n')
  sink()
}

# scale and format tips
format_tree <- function(tree, depth, mode = 1) {
	tree$root.edge <- 0.0
	tree$root <- 0.0
	branch_depth <- node.depth.edgelength(tree)
	if (mode == 1) {
		d <- max(branch_depth) # max depth
	} else if (mode == 2) {
		d <- mean(branch_depth) # average depth
	} else if (mode == 3) {
		d <- min(branch_depth) # min depth
	} else {
		d <- mean(tree$edge.length)
	}	
	
	if (depth > 0) {
	  scale <- depth / d
	} else {
	  scale <- 1.0
	}
	
	for (i in 1: length(tree$edge.length)) {
		tree$edge.length[i] <- scale * tree$edge.length[i]
	}
	labels <- tree$tip.label 
	for (i in 1:length(labels)) {
		labels[i] <- gsub("[^<0-9>]*", "", labels[i])
	}
	tree$tip.label <- labels
	
	return(tree)
}

# flag for indicating whether tree is ultrametric
is_ultrametric <- function(mode) {
	if (mode == 1 | mode == 2) {
		flag <- "true"
	} else {
		flag <- "false"
	}
	return(flag)
}

# generate tree
# mode 1: Tree from input newick string
# mode 2: Ultrametric Yule tree 
# mode 3: Birth-death tree with time sampled tips
# n: number of leaves
# depth: tree depth
generate_tree <- function(mode, n, depth = 0, newick = "", birthrate = 1.5) {
	if (mode == 1) {
		newick = "((1:0.05, 2:0.05)4:0.05, 3:0.1)5;"
		tree <- read.tree(text = newick)
	} else if (mode == 2) {
	  birth_param <- sprintf("rexp(%s)", birthrate)
		trees <- sim.taxa(numbsim = 1, n = n, waitsp = birth_param)
		tree <- trees[[1]]
	} else {
		lambda <- c(2,1,2)
		mu <- c(1,0.5,1.5)
		sampprob <- c(0.5,0.5,0.5)
		times <- c(0,1,2)
		trees <- lapply(
			rep(n, numbsim = 1), sim.bdsky.stt,
			lambdasky = lambda, deathsky = mu,
			timesky = times, sampprobsky = sampprob,
			rho = 0, timestop = 0
		)
		tree <- trees[[1]][[1]]
		branchingserial <- getx(tree, sersampling = 1)
	}
	tree <- format_tree(tree, depth)
	return(tree)
}

# create single beast xml
create_xml <- function(data, i, newick, ultrametric, template, logname, n, lambda_mu, alpha_shape, beta_shape, lambda_weight = 1, alpha_weight = 1, beta_weight = 1, lambda_init = 1.0, alpha_init = 0.1, beta_init = 0.1, error_mode = 1, birthrate_mu = 0.0) {
	seq <- data$sequence[data$tree == i & data$node == "1"]
	s <- gsub(pattern = "%seq_1%", replace = seq, x = template)
	for (j in (2:n)) {	
		seq <- data$sequence[data$tree == i & data$node == toString(j)]
		p <- paste0("%seq_", toString(j), "%")	
		s <- gsub(pattern = p, replace = seq, x = s)
	}
	
	if (newick != "") {
	  s <- gsub(pattern = "%newick%", replace = newick, x = s)		
	  s <- gsub(pattern = "%ultrametric%", replace = ultrametric, x = s)
	}
	
	s <- gsub(pattern = "%lambda_mu%", replace = lambda_mu, x = s)
	s <- gsub(pattern = "%alpha_shape%", replace = alpha_shape, x = s)
	s <- gsub(pattern = "%beta_shape%", replace = beta_shape, x = s)
	s <- gsub(pattern = "%logname%", replace = logname, x = s)
	
	if (birthrate_mu > 0) {
	  s <- gsub(pattern = "%birthrate_mu%", replace = birthrate_mu, x = s)
	}
	
	if (lambda_weight == 0) {
		lambda_init <- data$lambda[data$tree == i & data$node == "1"]
	}
	
	if (alpha_weight == 0) { 
		alpha_init <- data$alpha[data$tree == i & data$node == "1"]
	}
	
	if (beta_weight == 0) {
		beta_init <- data$beta[data$tree == i & data$node == "1"]
	}
	
	if (error_mode == 1) {
		s <- gsub(pattern = '%lambda_weight%', replace = lambda_weight, x = s)
      		s <- gsub(pattern = '%lambda_init%', replace = lambda_init, x = s)
		s <- gsub(pattern = '%alpha_weight%', replace = alpha_weight, x = s)
		s <- gsub(pattern = '%alpha_init%', replace = alpha_init, x = s)
		s <- gsub(pattern = '%beta_weight%', replace = beta_weight, x = s)
		s <- gsub(pattern = '%beta_init%', replace = beta_init, x = s)
	}
	
	return(s)
}

# create beast xmls
create_xmls <- function(seq_file, template_file, output_format, newick, ultrametric, n, lambda_mu, alpha_shape, beta_shape, lambda_weight, alpha_weight, beta_weight, mode = 1, birthrate_mu = 0.0) {
	template_path <- file.path("../templates", template_file)
	seq_path <- file.path("../output", "sequences", seq_file)
	template <- readLines(template_path)  
	data <- read.csv(seq_path, colClasses = c("sequence" = "character"))
	N <- length(unique(data$tree))  
	dir.create(file.path("../output", "xml"), recursive = T, showWarnings = F)  
	for (i in 1:N) {
		filename <- file.path("../output", "xml", sub("%num%", i, output_format))
		logname <- sub(".xml", "", basename(filename))
		content <- create_xml(data, i, newick, ultrametric, template, logname, n, lambda_mu, alpha_shape, beta_shape, lambda_weight, alpha_weight, beta_weight, error_mode = mode, birthrate_mu = birthrate_mu)
		writeLines(content, filename)
	}  
}

run_simulation_fixed <- function(lambdas, alphas, betas, n, depth, seed, tree_mode, N, L, template, template_error) {
	# generate tree once
	set.seed(seed)
	tree <- generate_tree(tree_mode, n, depth)
	newick <- write.tree(tree)
	ultrametric <- is_ultrametric(tree_mode)	
	filename <- paste0("binary_mode", tree_mode, "_no_error_N", N, "_L", L, ".csv")
	filename_error <- paste0("binary_mode", tree_mode, "_error_N", N, "_L", L, ".csv")

	# set seed for generating seqs
	set.seed(seed)
	simulate_trees_fixed(filename, tree, n, L, N, lambdas, rep(0, N), rep(0, N))
	set.seed(seed)
	simulate_trees_fixed(filename_error, tree, n, L, N, lambdas, alphas, betas)

	# generate xmls	
	output <- paste0("binary_N", N, "_L", L, "_%exp%_%num%.xml")

	# 1 -  no error - error parameters set to 0
	create_xmls(
		seq_file = filename, 
		template_file = template, 
		output_format = sub("%exp%", "1", output), 
		newick = newick, 
		ultrametric = ultrametric,
		n = n, 
		lambda_mu = lambda_mu, 
		alpha_shape = alpha_shape, 
		beta_shape = beta_shape, 
		lambda_weight = 1.0, 
		alpha_weight = 0.0, 
		beta_weight = 0.0, 
		mode = 0
	)

	# 2 - error - error parameters set to 0
	create_xmls(
		filename_error, 
		template, 
		sub("%exp%", "2", output), 
		newick,
		ultrametric,
		n, 
		lambda_mu, 
		alpha_shape, 
		beta_shape, 
		1.0, 
		0.0, 
		0.0, 
		0
	)

	# 3 - error - fix error parameters to truth, estimate subs
	create_xmls(
		filename_error, 
		template_error, 
		sub("%exp%", "3", output), 
		newick, 
		ultrametric,
		n, 
		lambda_mu, 
		alpha_shape, 
		beta_shape, 
		1.0, 
		0.0, 
		0.0
	)

	# 4 - error - fix one error parameter to truth, estimate subs and 1 error param
	create_xmls(
		filename_error, 
		template_error, 
		sub("%exp%", "4", output), 
		newick, 
		ultrametric,
		n, 
		lambda_mu, 
		alpha_shape, 
		beta_shape, 
		1.0, 
		1.0, 
		0.0
	)

	# 5 - error - estimate all parameters (*)
	create_xmls(
		filename_error, 
		template_error, 
		sub("%exp%", "5", output), 
		newick, 
		ultrametric,
		n, 
		lambda_mu, 
		alpha_shape, 
		beta_shape, 
		1.0, 
		1.0, 
		1.0
	)

	# 6 - error - fix subs params - estimate one error param
	create_xmls(
		filename_error, 
		template_error, 
		sub("%exp%", "6", output), 
		newick, 
		ultrametric,
		n, 
		lambda_mu, 
		alpha_shape, 
		beta_shape, 
		0.0, 
		1.0, 
		0.0
	)

	# 7 - error - fix subs params - estimate both error params
	create_xmls(
		filename_error, 
		template_error, 
		sub("%exp%", "7", output), 
		newick, 
		ultrametric,
		n, 
		lambda_mu, 
		alpha_shape, 
		beta_shape, 
		0.0, 
		1.0, 
		1.0
	)
}

example_simulation_fixed <- function() {
  seed <- 666
  n <- 10 # num tips
  depth <- 0.1 # tree depth
  tree_mode <- 3
  num_trials <- 200 # num trials  
  l <- 400 # sequence length
  
  lambda_mu <- -1
  alpha_shape <- 50
  beta_shape <- 50
  
  lambdas <- rlnorm(num_trials, lambda_mu)
  alphas <- rbeta(num_trials, 1, alpha_shape)
  betas <- rbeta(num_trials, 1, beta_shape)
  
  template <- "binary_fixed_no_error_large_template.xml"
  template_error <- "binary_sampled_large_template.xml"
  
  run_simulation_fixed(lambdas, alphas, betas, n, depth, seed, tree_mode, num_trials, l, template, template_error)
}

run_simulation_yule <- function() {
  seed <- 666
  n <- 30
  l <- 400
  num_trials <- 200
  
  lambda_mu <- -1
  alpha_shape <- 50
  beta_shape <- 50
  birthrate_mu <- 7
  ultrametric <- "true"
  
  lambdas <- rlnorm(num_trials, lambda_mu)
  alphas <- rbeta(num_trials, 1, alpha_shape)
  betas <- rbeta(num_trials, 1, alpha_shape)
  birthrates <- rnorm(num_trials, birthrate_mu) # rexp(num_trials, birthrate_mu)
  
  seq_file <- paste0("binary_yule_N", num_trials, "_L", l, ".csv")
  template_file <- "binary_yule_large_template.xml"
  output_format <- paste0("binary_yule_N", num_trials, "_L", l, "_%num%.xml")

  simulate_trees_yule(seq_file, n, l, num_trials, lambdas, alphas, betas, birthrates)
  create_xmls(seq_file, template_file, output_format, newick = "", ultrametric, n, lambda_mu, alpha_shape, beta_shape, 1, 1, 1, birthrate_mu = birthrate_mu)
}
    
run_simulation_yule()